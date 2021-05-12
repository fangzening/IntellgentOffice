from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.views import View
import json
from datetime import datetime
from django.core.paginator import Paginator
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.core.files import File
from django.core import serializers
from expense.custom_functions import notifyAll, check_invoice
from SAP.SAPFunctions import *
from office_app.views import set_session
from django.contrib import messages
from travel.custom_functions import convert_html_message_to_text
#from django.core.file.storage import FileSystemStorage
# Create your views here.
from Smart_Office import settings
from expense.form import *

from expense.models import *
from office_app.models import LegalEntity,BusinessGroup,BusinessUnit,EmployeeDepartment,CostCenter,Role
import sys
import traceback

# show the dashboard
@login_required
def dashboard(request):
    # result = conn.call('STFC_CONNECTION', REQUTEXT=u'Hello SAP!')
    # print(result)
    return render(request,'expense/dashboard.html')

# show the list of application history
@login_required
def expense_history(request):
    # res=createAP('EXP20208121', 'EXP')
    # print(res['SAPDocNo'])
    user=request.user
    employee=Employee.objects.get(associateID=user.associateID)
    expense_history=Expense.get_expense_history_by_id(user.associateID)#these are the expenses that requested by this employee
    paginator=Paginator(expense_history,20)
    page_numer=request.GET.get('page')
    if page_numer:
         expense_history_page=paginator.get_page(page_numer)
    else :
        expense_history_page=paginator.get_page(1)
    return render(request,'expense/expense_history.html',{"expense_history_list":expense_history_page})

#show the list of expense forms need to be approved by this user
@login_required
def expense_to_approve(request):
    user=request.user
    employee=Employee.objects.get(associateID=user.associateID)
    expense_list = Expense.get_expense_to_approve_by_id(user.associateID)  # these are the expenses that need to be approved by this emplopyee
    return render(request,'expense/expense_to_approve.html',{"expense_approve_list":expense_list})

# show the expense form from dashboard
@login_required
def showExpenseForm(request, expense_id, type):
    # return render(request, "expense/expense_detail.html", {'form_id': expense_id, "show_chat": True})

    if request.session['department'] == '':
        return HttpResponse("You are not allowed to view this page")
    else :
        expense=Expense.objects.get(form_ID=expense_id)
        currencies=Currency.objects.all()
        action_permission="none"
        partial=False
        employees= None
        GLAccounts=None
        role="requester"
        vendors=None
        if(type=="Approve"):
           app_list=expense.approverlist_set.all()[0]
           current=app_list.currentStage
           try:
                app_status=app_list.approverstatus_set.get(approver__associateID=request.user.associateID)
                employeeStage=app_status.stage
                employees=EmployeeDepartment.objects.all()
                if app_list.get_approverstatus_byapprover(request.user.associateID):
                       dept=app_list.get_approverstatus_byapprover(request.user.associateID).department
                       if dept=="accounting" :
                             role="accountant"
                             vendors=Vendors.objects.all()
                             GLAccounts=GLAccount.objects.all()
                       elif dept=="CM":
                           role="CM"
                       else:
                           role="other"
                if(employeeStage==current):# get the current approver, if they should be put later or earlier, they don't have the permission to this page
                    action_permission="approve"
                partial=app_status.partial
           except:
               return redirect('login')
        return render(request,"expense/expense_detail.html",{'form_id': expense_id, "show_chat": True, "expense":expense,"action_permission":action_permission,'partial':partial,
                                                          "GL_accounts":GLAccounts,"employees":employees,"role":role,"currencies":currencies,"vendors":vendors})

# creating expense without using modelform
@login_required
def add_expense_without_modelform(request):
    if request.method=="POST":
        all_data=request.POST
        requester=Employee.get_employee_by_associate_id(request.user.associateID)
        #adding basic expense info
        company=LegalEntity.objects.get(entityName=all_data["company"])
        vendor=Vendors.objects.get(id=all_data["vendor"])
        expense = Expense(requester=requester,
                           payment_Date=all_data["payment_date"],
                           BU=BusinessUnit.objects.get(buName=all_data["BU"]),
                           # document_Header=all_data["doc_header"],
                          company=company,
                          company_Code=company.sapCompCode,
                           invoice_ID=all_data["invoice_id"], vendor=vendor,vendor_Code=vendor.vendorCode,tax_Rate=Decimal(all_data["tax_rate"])/100,
                           shipping_Cost=Decimal(all_data["shipping_cost"]),currency=Currency.objects.get(name=all_data["currency"]).name,request_Date=datetime.datetime.now()

                           )

        expense.save()# this is important because the id we used to generate form_id is auto_incremented only when saved
        expense.form_ID = expense.get_formID()
        expense.save()
        applist1 = ApproverList(
            expense=expense
        )

        applist1.save()

        #adding items from forms
        item_names = all_data.getlist("item_name")
        item_descriptions=all_data.getlist("item_description")
        item_amounts=all_data.getlist("item_amount")
        item_cost_centers=all_data.getlist("selected_cc_expense_item")
        # item_texts=all_data.getlist("item_text")
        # item_assignments=all_data.getlist("item_assignment")
        item_length = len(item_names)
        current_item = 0

        while current_item < item_length:
            current_cc=CostCenter.objects.get(costCenterCode=item_cost_centers[current_item])
            expenseItem = ExpenseItem(
                name=item_names[current_item],
                description=item_descriptions[current_item],
                cost_Center=current_cc,
                amount=Decimal(item_amounts[current_item]),
                active_Status=ExpenseItem.ACTIVE,
                expense=expense
            )
            expenseItem.save()
            current_item+=1
            deptapprover=EmployeeDepartment.objects.get(associateID=current_cc.managedBy)
            deptduplicate = False

            for appsta in applist1.approverstatus_set.all():
                if appsta.approver == deptapprover:
                    deptduplicate = True

            if deptapprover.associateID.associateID!=requester.associateID and deptduplicate==False:# if  DM is the requester or already in the approver list, we don't need to add them one more time
                appdm = ApproverStatus(         # this is where we add department managers at stage 0 when create the expense
                    approver=deptapprover,
                    stage=0,
                    department="Department Manager",
                    approver_list=applist1,
                    partial=False,
                )
                appdm.save()
        expense.sales_Tax_Amount = expense.get_sales_tax_amount
        expense.ground_Total = expense.get_ground_total
        expense.set_cost_center()
        expense.save()
        files=request.FILES
        attachments=request.FILES.getlist('attachment')
        attachment_descriptions = all_data.getlist("attachment_description")
        current_attachment=0;
        while current_attachment<len(attachment_descriptions):
                attachment=Attachment(
                        description = attachment_descriptions[current_attachment],
                        expense=expense
                )
                attachment.attachments.save(attachments[current_attachment].name,attachments[current_attachment])
                attachment.save();
                current_attachment+=1

        #adding general approver list:
        for appassign in ApproverAssignment.get_approvers(expense.BU):
            if appassign.department=="accounting" or (appassign.minimum < expense.ground_Total and appassign.approver.associateID.associateID!=requester.associateID):
                #if current total is less than minimum or the approver is requester, then this approver doesn't need to go view this
                app = ApproverStatus(
                    approver=appassign.approver,
                    stage=appassign.stage,
                    approver_list=applist1,
                    department=appassign.department,
                    partial=appassign.partial
                )
                app.save()

        applist1.maxStage = applist1.get_max_stage()
        applist1.update_current_stage()
        #applist1.update_current_stage()
        applist1.save()
        notifyAll(request, applist1)
        #return redirect('showExpenseForm', pk=expense)
        set_session(request)
        if request.session['department'] == '':
            return HttpResponse("You are not allowed to view this page")
        else:
            return  dashboard(request)
    else:


           # costcenters=CostCenter.get_all_cost_center()
           employee=Employee.objects.get(associateID=request.user.associateID)
           BUs=BusinessUnit.objects.all()
           vendors=Vendors.objects.all()
           companies=LegalEntity.objects.all()
           currencies=Currency.objects.all()
           return render(request,'expense/expense_without_modelform.html',{#"cost_centers":costcenters,
                    "employee":employee,"BUs":BUs,"vendors":vendors,"currencies":currencies,"today":datetime.datetime.now(),"companies":companies})

# processing the expense
@login_required
def process_expense(request):
    if request.method == "POST":
        all_data = request.POST
        expenseid = all_data['expense_ID']
        expense=Expense.objects.get(form_ID=expenseid)

        if 'approve_button' in request.POST:# do approve
            checkboxes = all_data.getlist("item")
            if len(checkboxes)!=0:# check if it's partial approval
                for itemid in checkboxes:
                    item=ExpenseItem.objects.get(id=itemid)
                    item.active_Status=ExpenseItem.INACTIVE# change the item status
                    item.save()
                expense.sales_Tax_Amount=expense.get_sales_tax_amount# change the expense amount
                expense.ground_Total=expense.get_ground_total# we need to change current total amount after reject one item
                count=0
                for item in expense.expenseitem_set.all():
                    if item.active_Status==ExpenseItem.ACTIVE:
                        count+=1
                if count==0:# if  all items of the expense is inactive then the expense should be rejected now
                    applist=expense.approverlist_set.all()[0]# get the approverstatus list of this expense form
                    applist.status=ApproverList.REJECTION
                    applist.save()
            # else means the user approves all items or the user is a CM

            user=request.user
            employee=Employee.objects.get(associateID=user.associateID)
            ed=EmployeeDepartment.objects.get(associateID=user.associateID)
            applist = expense.approverlist_set.all()[0]
            result=applist.set_current_status(user.associateID, ApproverStatus.APPROVAL, all_data['memo'])# set the current ApproverStatus to "approved"
            if result!=True:# this mean all current stages now are finished
                notifyAll(request, applist)
            applist.save()
            if('doc_header' in all_data):#this means the approver is an accountant, we are gonna store current modification
                expense.document_Header=all_data['doc_header']
                expense.payment_Date=all_data["expense_payment_date"]
                expense.invoice_ID=all_data["expense_invoice_ID"]
                expense.currency=all_data['currency']
                expense.vendor=Vendors.objects.get(id=all_data["vendor"])
                expense.post_Date=datetime.datetime.now()
                item_names = all_data.getlist("item_name")
                item_descriptions = all_data.getlist("item_description")
                item_length = len(item_names)
                item_ids=all_data.getlist("item_id")
                current_item = 0
                while current_item < item_length:
                    expenseItem = ExpenseItem.objects.get(id=item_ids[current_item])
                    expenseItem.name=item_names[current_item]
                    expenseItem.description=item_descriptions[current_item]
                    expenseItem.save()
                    current_item+=1;
                attachments = request.FILES.getlist('attachment')
                attachment_descriptions = all_data.getlist("attachment_description")
                current_attachment = 0;
                while current_attachment < len(attachment_descriptions):
                    attachment = Attachment(
                        description=attachment_descriptions[current_attachment],
                        expense=expense
                    )
                    attachment.attachments.save(attachments[current_attachment].name, attachments[current_attachment])
                    attachment.save();
                    current_attachment += 1
                resSAP = createAP(expense.form_ID,'EXP')
                print(resSAP)
                expense.apnumber=resSAP['SAPDocNo']
                expense.save()



        elif 'reject_button' in request.POST:# do reject all here
            user = request.user
            employee = Employee.objects.get(associateID=user.associateID)
            ed = EmployeeDepartment.objects.get(associateID=user.associateID)
            applist = expense.approverlist_set.all()[0]  # get the approverstatus list of this expense form
            applist.set_current_status(user.associateID, ApproverStatus.REJECTION, all_data['memo'])
            # for expenseitem in expense.expenseitem_set.all():
            #     # print(expenseitem.cost_Center.managedBy)
            #     # print(employee)
            #     if expenseitem.active_Status == ExpenseItem.ACTIVE:
            #         expenseitem.active_Status = ExpenseItem.INACTIVE
            #         expenseitem.save()
            # expense.sales_Tax_Amount = expense.get_sales_tax_amount
            # expense.ground_Total = expense.get_ground_total
            # we need to change current total amount after reject one item


        elif 'add_approver_button' in request.POST:# do add approver
            applist = expense.approverlist_set.all()[0]
            currentapprover=EmployeeDepartment.objects.get(associateID=request.user.associateID)
            currentapprover.associateID
            newapprover=EmployeeDepartment.objects.get(associateID__associateID=all_data['approver'])
            pos=all_data['position']
            if pos=="before":
                current_stage=applist.currentStage
                for appsta in applist.approverstatus_set.all():
                    if appsta.stage>=applist.currentStage :
                        appsta.stage+=1
                        appsta.save()

                appsta= ApproverStatus(
                   approver_list=applist,
                   stage=current_stage,
                   approver=newapprover,
                   partial=False,
                    department=newapprover.departmentID,
                )
                if newapprover.roleID:
                    appsta.title = newapprover.roleID.title
                applist.maxStage=applist.get_max_stage()
                appsta.save()
            else:
                current_stage = applist.currentStage
                for appsta in applist.approverstatus_set.all():
                    if appsta.stage >= applist.currentStage+1:
                        appsta.stage += 1
                        appsta.save()

                appsta = ApproverStatus(
                    approver_list=applist,
                    stage=current_stage+1,
                    approver=newapprover,
                    partial=False,
                    department=newapprover.departmentID,
                )
                if newapprover.roleID:
                    appsta.title = newapprover.roleID.title
                appsta.save()
                applist.maxStage = applist.get_max_stage()
            applist.save()
            expense.save()
            return redirect('../'+expenseid+'/Approve')
        elif 'update_button' in request.POST:# do change the info of expense
            payment_date=all_data['expense_payment_date']
            expense=Expense.objects.get(form_ID=all_data['expense_ID'])
            invoice_no=all_data['expense_invoice_ID']
            currency=all_data['currency']
            companyCode=LegalEntity.objects.get(entityName=all_data["expense_company"]).sapCompCode
            vendor = Vendors.objects.get(id=all_data["vendor"])
            vendorCode=vendor.vendorCode
            doc_header=all_data['doc_header']
            item_id = all_data.getlist("item_id")
            item_names = all_data.getlist("item_name")
            item_descriptions = all_data.getlist("item_description")
            item_length = len(item_names)
            current_item = 0
            while current_item < item_length:
                item=ExpenseItem.objects.get(pk=int(item_id[current_item]))
                item.name=item_names[current_item]
                item.description=item_descriptions[current_item]
                item.save()
                current_item+=1
            attachments = request.FILES.getlist('attachment')
            attachment_descriptions = all_data.getlist("attachment_description")
            current_attachment = 0;
            while current_attachment < len(attachment_descriptions):
                attachment = Attachment(
                    description=attachment_descriptions[current_attachment],
                    expense=expense
                )
                attachment.attachments.save(attachments[current_attachment].name, attachments[current_attachment])
                attachment.save();
                current_attachment += 1
            expense.vendor=vendor
            expense.currency=currency
            expense.vendor_Code=vendor.vendorCode
            expense.payment_Date=payment_date
            expense.invoice_ID=invoice_no
            expense.document_Header=doc_header
            expense.save()
            messages.success(request,"Successfully updated!")
            # print("updated!")
            # user = request.user
            # ed = EmployeeDepartment.objects.get(associateID=user.associateID)
            # applist = expense.approverlist_set.all()[0]
            # result = applist.set_current_status(user.associateID, ApproverStatus.APPROVAL,
            #                                     all_data['memo'])  # set the current ApproverStatus to "approved"
            # if result != True:  # this mean all current stages now are finished
            #     notifyAll(request, applist)
            # applist.save()
            return redirect('../'+all_data['expense_ID']+'/Approve')#showExpenseForm(request,all_data['expense_ID'],"Approve")
        elif 'replace_approver_button' in request.POST:
            applist = expense.approverlist_set.all()[0]
            currentapprover = EmployeeDepartment.objects.get(associateID=request.user.associateID)
            appsta = applist.approverstatus_set.get(approver__associateID=request.user.associateID).delete()
            newapprover = EmployeeDepartment.objects.get(associateID__associateID=all_data['reapprover'])
            appsta = ApproverStatus(
                approver_list=applist,
                stage=applist.currentStage,
                approver=newapprover,
                partial=False,
                department=newapprover.departmentID,
            )
            if newapprover.roleID:
                appsta.title = newapprover.roleID.title
            appsta.save()
            applist.save()
        expense.save()
        return dashboard(request)

# this is used to link to AJAX to check if the selected approver  is valid
def checkapprover(request):
    if request.method == "GET":
        p = request.GET.copy()
        if p['associateID'] and p['expenseID']:
            appID = p['associateID']
            expenseID=p['expenseID']
            expense=Expense.objects.get(form_ID=expenseID)
            applist=expense.approverlist_set.all()[0]
            if(appID==expense.requester.associateID):# if the new approver is the requester themselves
                return HttpResponse("Requester")
            for appsta in applist.approverstatus_set.all():
                if(appsta.approver.associateID.associateID==appID):# if the approver already exist in the approver list
                    return HttpResponse("Duplicate")
            return HttpResponse(True)
        else :
            return HttpResponse("Null")


# this is the view associates with AJAX that return a list of BU according to selected cost center
def get_BU_by_CCs(request):
    BUs=[]
    CCs=request.GET.getlist('cccode[]')
    for cc in CCs:
        if cc:
           costcenter=CostCenter.objects.get(costCenterCode=cc)
           if costcenter.businessUnit not in BUs:# prevent from adding duplicate BU
                BUs.append(costcenter.businessUnit)
    json_models = serializers.serialize("json", BUs)

    return HttpResponse(json_models, content_type ="application/javascript")

#this is the method to get associated cost centers by company
def get_CCs_by_company(request):
    companyName=request.GET.get('company')
    if companyName:
        company=LegalEntity.objects.get(entityName=companyName)
    CCs=CostCenter.objects.filter(businessUnit__businessGroup__legalEntity=company)
    json_models=serializers.serialize("json",CCs)
    return HttpResponse(json_models,content_type="application/javascript")


def getGlbycode(request):
    return HttpResponse(GLAccount.objects.get(glCode=request.GET.get('glcode')).glDescription)

# show the assets list of the item to accountant only
@login_required
def get_asset_by_item(request,item_id):
    if item_id:
        item=ExpenseItem.objects.get(pk=item_id)
        assets=item.item_asset.all()
        usetax=item.item_expense.all()
        # if len(assets)==0 or  'add_asset_button' in request.POST :
        #      return to_create_asset(request,item_id)
        # else:# if there's no asset of this item, we'll just redirect user to the create page
        if len(assets)!=0:
           json_models = serializers.serialize("json", assets)
        elif len(usetax)!=0:
            json_models = serializers.serialize("json", usetax)
        else:
            # print("no asset nor expense found!")
            json_models=json.dumps({})
        return HttpResponse(json_models, content_type="application/javascript")
        # return render(request, 'expense/asset_detail.html', {'item': item })
    else :

            return HttpResponse("Null")

#this checks if the invoice id is unique
def check_invoice_no(request):
    companyCode = LegalEntity.objects.get(entityName=request.GET.get("companyName")).sapCompCode
    vendorCode = Vendors.objects.get(id=request.GET.get('vendor')).vendorCode
    invoiceNo=request.GET.get("invoiceNo")
    expense_ID=request.GET.get('expense_ID')
    if  expense_ID!="null": # this means we are at editing page
        expense = Expense.objects.get(form_ID=expense_ID)
        if check_invoice(invoiceNo,companyCode,vendorCode) == False:
            queryset=Expense.objects.filter(invoice_ID=invoiceNo,company__sapCompCode=companyCode,vendor__vendorCode=vendorCode)
            if queryset.exists():
                if(queryset.count()>1):
                       return HttpResponse("The invoice is already been used!")
                elif queryset[0]==expense:
                    return HttpResponse("OK")
                elif queryset[0]!=expense:
                    return HttpResponse("The invoice is already been used!")
            else:
                return HttpResponse("Error! The invoice is already been recorded in SAP!")
        return HttpResponse("OK")
    else: # this means we are at creating page
        if check_invoice(invoiceNo,companyCode,vendorCode) == False:
           return HttpResponse("The invoice is already been used!")
        else :
            return HttpResponse("OK")

# this checks if the  department manager is in the selected CC
def check_designated_approvers(request):
    messagelist={}
    CCs=request.GET.getlist('cccode[]')
    for cc in CCs:
            current_cc = CostCenter.objects.get(costCenterCode=cc)
            key=current_cc.costCenterName +"("+current_cc.costCenterCode+")"
            if not EmployeeDepartment.objects.filter(
                    associateID=current_cc.managedBy):  # get the dept manager of the cost center:
                if  key in messagelist:
                    messagelist[key].append("department manager")
                else:
                    messagelist[key]=["department manager"]
    # json_dic=serializers.serialize("json", messagelist)
    return HttpResponse(json.dumps(messagelist))

# return create asset page
@login_required
def to_create_asset(request,item_id):
    item = ExpenseItem.objects.get(pk=item_id)
    GLAccounts = GLAccount.get_all_GL()
    return render(request, 'expense/asset_create.html', {"item": item, "GL_accounts": GLAccounts, })


# create the asset
@login_required
def asset_create(request):
    anumber = request.GET.get('anumber')
    subnumber=request.GET.get('subnumber')
    # glcode = request.GET.get('GL')
    # amount = request.GET.get('amount')
    # qty = request.GET.get('qty')
    item_id = request.GET.get('item_id')
    eitem = ExpenseItem.objects.get(id=item_id)
    # asset = Asset(
    #     asset_number=anumber, amount=amount, quantity=qty, item=eitem
    #
    # )
    # asset.save()
    eitem.asset_number=anumber;
    eitem.asset_subnumber=subnumber;
    # eitem.GL = GLAccount.objects.get(glCode=glcode);
    # eitem.asset_amount=amount;
    # eitem.asset_quantity=qty;
    eitem.type=ExpenseItem.ASSET;
    eitem.save();
    return HttpResponse("OK")

#create the usetax
@login_required
def usetax_create(request):
    text = request.GET.get('text')
    assign=request.GET.get('assignment')
    glcode=request.GET.get('GL')
    item_id=request.GET.get('item_id')
    eitem=ExpenseItem.objects.get(id=item_id)
    # usetax= UseTax(
    #     text=text,assignment=assign,GL=GLAccount.objects.get(glCode=glcode),item=ExpenseItem.objects.get(id=item_id)
    #
    # )
    # usetax.save()
    eitem.text=text;
    eitem.assignment=assign;
    eitem.GL=GLAccount.objects.get(glCode=glcode);
    eitem.type=ExpenseItem.USE_TAX;
    eitem.save()
    return HttpResponse("OK")

#delete selected use_tex
@login_required
def delete_usetax(request):
    # UseTax.objects.get(id=request.GET.get('id')).delete()
    item = ExpenseItem.objects.get(id=request.GET.get('id'))
    item.type = ExpenseItem.NOAPP
    item.text = None
    item.assignment = None
    item.GL = None
    item.save()
    return HttpResponse("OK")

# delete selected asset
@login_required
def delete_asset(request):
    # Asset.objects.get(id=request.GET.get('id')).delete()
    item=ExpenseItem.objects.get(id=request.GET.get('id'))
    item.type=ExpenseItem.NOAPP
    item.asset_number=None
    # item.asset_amount=None
    # item.asset_quantity=None
    item.save()
    return HttpResponse("OK")

def get_item(request,item_id):
    json_models = serializers.serialize("json", ExpenseItem.objects.filter(id=item_id));
    return HttpResponse(json_models, content_type="application/javascript")


#create expense
# class ExpenseCreate(CreateView):
#     model = Expense
#     template_name = 'expense/expense_create.html'
#     form_class = ExpenseFormSet
#     success_url = None
#
#     def get_context_data(self, **kwargs):
#         data = super(ExpenseCreate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['attachments'] = ExpenseAttachmentFormSet(self.request.POST,instance=self.object)
#             data['expense_items'] = ExpenseItemFormSet(self.request.POST,instance=self.object)
#             data['use_tax'] = ExpenseUseTaxFormSet(self.request.POST,instance=self.object)
#         else:
#             data['attachments'] =ExpenseAttachmentFormSet(instance=self.object)
#             data['expense_items'] = ExpenseItemFormSet(instance=self.object)
#             data['use_tax'] = ExpenseUseTaxFormSet(instance=self.object)
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         attachments = context['attachments']
#         expenseItems= context['expense_items']
#         use_tax=context['use_tax']
#         expense=context['form']
#         with transaction.atomic():
#             form.instance.created_by = self.request.user
#             self.object = form.save()
#             # if attachments.is_valid() and use_tax.is_valid() and expenseItems.is_valid():
#                # print("*****************************tables are valid")
#             attachments.instance = self.object
#             use_tax.instance=self.object
#             expenseItems.instance=self.object
#             attachments.save()
#             use_tax.save()
#             expenseItems.save()
#         return super(ExpenseCreate, self).form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('myExpenses:expense_detail', kwargs={'pk': self.object.pk})

