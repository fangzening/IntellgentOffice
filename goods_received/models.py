from django.db import models

from SAP.SAPFunctions import downloadPO, createGR
from goods_received import AssetFile
from office_app.approval_functions import merge_dictionaries
from purchase.models import *
from office_app.models import *


# DB Models for GR App
class GRForm(models.Model):
    formID = models.BigAutoField(primary_key=True)
    prForm = models.ForeignKey(PurchaseRequestForm, on_delete=models.CASCADE, blank=True, null=True)
    status = models.BooleanField(default=False, blank=True)
    headerText = models.CharField(max_length=250, blank=True)
    memo = models.CharField(max_length=1000, blank=True)
    isApproved = models.BooleanField(default=False, blank=True)
    isCompleted = models.BooleanField(default=False, blank=True)
    isDeclined = models.BooleanField(default=False, blank=True)
    poNumber = models.CharField(max_length=50, blank=True, null=True)
    plantCode = models.CharField(max_length=50, blank=True, null=True)
    businessGroup = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, blank=True, null=True)
    businessUnit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, blank=True, null=True)
    requester = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True)
    refNumber = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return "GR Form " + str(self.formID)

    @property
    def grAmount(self):
        return self.prForm.prAmount

    @property
    def sap_prefix(self):
        return "GR"

    @property
    def form_type(self):
        return "Goods Received"

    @property
    def form_url_without_base_url(self):
        return "/goods_received/" + str(self.formID)

    @property
    def full_url(self):
        return str(settings.BASE_URL) + "goods_received/" + str(self.formID)

    @property
    def module(self):
        return "goods received"

    @property
    def advance_type(self):
        return None

    @property
    def employeeID(self):
        try:
            return self.prForm.employee
        except:
            return self.requester

    @property
    def employee(self):
        try:
            return self.prForm.employee
        except:
            return self.requester

    def get_data_for_excel(self):
        # return multidimensional array where each item in array is [itemDesc, PartNum, QTY]
        excel_data = []
        all_items_for_GR = GRList.objects.filter(grForm=self).order_by('pk')
        all_sap_data = SAPFunctionsPrd.downloadPO(poNumber=self.poNumber, plantCode=self.plantCode)
        index = 0
        for item in all_sap_data:
            itemDesc = ""
            assetNum = ""
            qty = ""
            cost_center = ""
            profit_center = ""
            if item['Materialdesc'] != None and item['Materialdesc'] != 'None':
                itemDesc = item['Materialdesc']
            else:
                if self.prForm != None:
                    itemDesc = all_items_for_GR[index].itemDesc

            if item['ASSETNO'] != None and item['ASSETNO'] != 'None':
                assetNum = item['ASSETNO']
            # else:
            #     if self.prForm != None:
            #         assetNum = all_items_for_GR[index].assetNo

            qty = all_items_for_GR[index].grQuantity

            if item['costcenter'] != None and item['costcenter'] != 'None':
                cost_center = item['costcenter']
            else:
                if self.prForm != None:
                    cost_center = all_items_for_GR[index].costCenter

            if item['PROFITCENTER'] != None and item['PROFITCENTER'] != None:
                profit_center = item['PROFITCENTER']

            excel_data.append([itemDesc, assetNum, qty, cost_center, profit_center])
        print(f"Excel Data: {excel_data}")
        return excel_data

    def get_files_for_form(self, form_id):
        return GRFileUpload.objects.filter(grForm=self)

    def update_isApproved_and_isDeclined(self, request):
        error_messages = {'fatal_errors': ''}
        try:
            stages_declined_count = GRApproversProcess.objects.filter(grForm=self, actionTaken='Declined').count()
            if stages_declined_count > 0:
                self.isDeclined = True
                self.isApproved = False
                self.save()
                return error_messages
            else:
                self.isDeclined = False
                self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error declining the form! Please contact IT!"
            return error_messages

        try:
            stages_approved_count = GRApproversProcess.objects.filter(grForm=self, actionTaken='Approved').count()
            if stages_approved_count >= 2:
                self.isApproved = True
                self.isDeclined = False
            else:
                self.isApproved = False
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error approving the form! Please contact IT!"
            return error_messages

        return error_messages


    def save_gr(self, prForm=None, headerText=None, memo=None, poNumber=None, plantCode=None, businessUnit=None,
                requester=None, businessGroup=None, refNumber=None):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        if prForm != None:
            self.prForm = prForm
        if headerText != None:
            self.headerText = headerText
            print("setting header to: " + str(headerText))
        else:
            print("head text is none!")
        if memo != None:
            self.memo = memo
            print("setting memo to: " + str(memo))
        else:
            print("memo is none: " + str(memo))
        if refNumber != None:
            self.refNumber = refNumber
        print(f"ref number is: {refNumber}")
        if poNumber != None:
            self.poNumber = poNumber
        if plantCode != None:
            self.plantCode = plantCode
        if businessGroup != None:
            self.businessGroup = businessGroup
        if businessUnit != None:
            self.businessUnit = businessUnit
        if requester != None:
            self.requester = requester
        try:
            self.save()
        except:
            error_messages['fatal_errors'] = 'Error saving GR Form! Please contact IT!'
        return error_messages

    def update_gr_with_no_pr(self, request, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        business_group = request.POST.get('business_group')
        for group in context['business_groups']:
            if group.pk == business_group:
                business_group = group
                break
        business_unit = request.POST.get('business_unit')
        for unit in context['business_units']:
            if unit.pk == business_unit:
                business_unit = unit
                break
        error_messages = merge_dictionaries(error_messages, context['gr_form'].save_gr(prForm=context['pr_form'],
                                                                                       memo=request.POST.get('memo'),
                                                                                       businessGroup=business_group,
                                                                                       businessUnit=business_unit,
                                                                                       refNumber=request.POST.get('ref_num')))
        return error_messages

    @staticmethod
    def check_if_gr_can_be_updated(request, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        # If user has not already claimed a stage
        if context['users_stage'] == None:
            # Get stages that have not been claimed yet if user has no stage that has been claimed
            if context['stages_claimed'] != None:
                # If both stages have been claimed:
                if len(context['stages_claimed']) >= 2:
                    error_messages[
                        'fatal_errors'] = "People have already claimed spots in the approval process and there are no more spots left. Action Cancelled."
                    return error_messages
                else:
                    # If one or none stages were claimed:
                    for stage in context['stages_claimed']:
                        if stage.approvalType == "buyer":
                            if "buyer" in request.POST.get('submit_button'):
                                error_messages['fatal_errors'] = "You do not have the right to do actions in the name of the requestor."
                                return error_messages
                        elif stage.approvalType == "warehouse":
                            if "warehouse" in request.POST.get('submit_button'):
                                error_messages[
                                    'fatal_errors'] = "You do not have the right to do actions in the name of the warehouse reciever."
                                return error_messages
        return error_messages

    @staticmethod
    def generate_gr(request, plantCode, po_num):
        error_messages = {'fatal_errors': '', 'other_errors': []}

        new_gr = GRForm()
        # region Create GR from SAP
        SAPresponse = downloadPO(poNumber=po_num, plantCode=plantCode)
        print(f"response: {SAPresponse}")
        if SAPresponse[0]['PONO'] != None:
            new_gr.save_gr(poNumber=po_num, plantCode=plantCode)
            # Get PR Form:
            all_purchase_items_with_po_num = PurchaseItemDetail.objects.filter(poNumber=po_num) # right now it cannot see the link between PR and PO because SAP PO is different than assigned PO
            if all_purchase_items_with_po_num:
                pr_form = all_purchase_items_with_po_num.first().form
                pr_basic_info = PurchaseBasicInfo.objects.get(form=pr_form)
                new_gr.save_gr(prForm=pr_form, requester=pr_form.employee, businessUnit=pr_basic_info.businessUnit, businessGroup=pr_basic_info.businessGroup)
                # Create GR Lists
                index = 0
                print(f"all purchase items with po num: {all_purchase_items_with_po_num}")
                buyer = None
                for item_to_update in all_purchase_items_with_po_num:
                    print(f"item: {item_to_update}")
                    print(f"index: {index}")
                    buyer = PRApprovalProcess.objects.get(stage=1, formID=item_to_update).approverID
                    new_gr_list = GRList()
                    error_messages = merge_dictionaries(error_messages,
                                                        new_gr_list.update_GRList(grForm=new_gr,
                                                                                  purchaseItem=item_to_update,
                                                                                  grQuantity=SAPresponse[index]['OPENGRQty'],
                                                                                  costCenter=CostCenter.objects.filter(costCenterCode=SAPresponse[index]['costcenter']).first()))
                    if error_messages['fatal_errors'] != '':
                        return error_messages
                    index += 1
                # region Set buyer stage
                if buyer != None:
                    print("Setting buyer approval stage")
                    error_messages = merge_dictionaries(error_messages,
                                                        GRApproversProcess().save_approval_process(request=request,
                                                                                                   grForm=new_gr,
                                                                                                   approver=buyer,
                                                                                                   stage=1,
                                                                                                   dayAssigned=datetime.today(),
                                                                                                   approvalType='buyer'))
                    print("Finished setting buyer approval stage")
                    # And notify buyer
                    error_messages = merge_dictionaries(error_messages,
                                                        notify_approver(employee=buyer, form=new_gr,
                                                                        message_type='next_approver',
                                                                        module=new_gr.module, request=request))
                    # endregion
                error_messages['dir_to_form'] = './' + str(new_gr.formID)
                error_messages['result'] = 'found'
            else:
                error_messages['dir_to_form'] = './' + str(new_gr.formID)
                error_messages['result'] = 'SAP found'
                for item in SAPresponse:
                    new_item = GRList()
                    new_item.update_GRList(grForm=new_gr, grQuantity=item['OPENGRQty'])
        else:
            redirect('smart_office_dashboard')



        # endregion
        return error_messages

    @staticmethod
    def update_whole_gr(request, context):
        # region Setting function-wide variables
        error_messages = {'fatal_errors': '', 'other_errors': []}
        all_post_data = dict(request.POST)
        # endregion

        # region updating GRForm object
        print("*******************************************************updating gr form object")
        if context['pr_form'] != None:
            headText = request.POST['header_text']
            error_messages = merge_dictionaries(error_messages, context['gr_form'].save_gr(prForm=context['pr_form'],
                                                                                            memo=request.POST.get('memo'),
                                                                                            refNumber=request.POST.get('ref_num'),
                                                                                           headerText=headText))
        else:
            error_messages = merge_dictionaries(error_messages, context['gr_form'].update_gr_with_no_pr(request, context))
        if error_messages['fatal_errors'] != '':
            return error_messages
        # endregion

        # region updating GRList objects
        index = 0
        for item in context['gr_list']:
            item.grQuantity = float(all_post_data['gr_quantity'][index])
            if context['pr_form'] == None:
                #print(f"cc desc: {all_post_data['cc_description']}")
                for center in context['cost_centers']:
                    if center.costCenterCode == all_post_data['cost_center'][index]:
                        cost_center = center
                item.costCenter = cost_center
            try:
                print("saving item: " + str(item))
                item.save()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error saving GR Quantity objects! Please contact IT!"
                return error_messages
            index += 1
        # endregion

        # region updating Files
        error_messages = merge_dictionaries(error_messages, GRFileUpload().upload_attachment_files(request=request, context=context, all_post_data=all_post_data))
        if error_messages['fatal_errors'] != '':
            return error_messages
        error_messages = merge_dictionaries(error_messages, GRFileUpload().upload_packaging_files(request=request, context=context))
        # endregion

        # region update approval Process
        error_messages = merge_dictionaries(error_messages, context['gr_form'].update_approval_process(request=request, context=context))
        if error_messages['fatal_errors'] != '':
            return error_messages
        error_messages = merge_dictionaries(error_messages, context['gr_form'].update_isApproved_and_isDeclined(request=request))
        # endregion
        return error_messages


    def update_approval_process(self, request, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}

        if "Finish" in request.POST.get('submit_button'):
            actionTaken = "Approved"
        elif "Decline" in request.POST.get('submit_button'):
            actionTaken = "Declined"
        else:
            actionTaken = "Updated Information"

        if 'warehouse' in request.POST.get('submit_button'):
            approval_type = 'warehouse'
            comments = request.POST.get('comment_warehouse_manager')
        else:
            approval_type = 'buyer'
            comments = request.POST.get('comment_buyer')


        error_messages = merge_dictionaries(error_messages, GRForm.check_if_gr_can_be_updated(request, context))
        if error_messages['fatal_errors'] != '':
            return error_messages

        if context['users_stage'] != None:
            if "Save" in request.POST.get('submit_button') or "Finish" in request.POST.get('submit_button'):
                print('In the save/finish')
                error_messages = merge_dictionaries(error_messages, self.update_other_stages_because_user_changed_GR(context=context, request=request))
                if error_messages['fatal_errors'] != '':
                    return error_messages

            context['users_stage'].save_approval_process(request=request, actionTaken=actionTaken, dateActionTaken=datetime.today(), comments=comments)
        else:
            if "Save" in request.POST.get('submit_button'):
                error_messages = merge_dictionaries(error_messages,
                                                    self.update_other_stages_because_user_changed_GR(context=context, request=request))
                if error_messages['fatal_errors'] != '':
                    return error_messages

            approver = Employee.objects.get(associateID=request.session['user_id'])
            context['users_stage'] = GRApproversProcess()
            context['users_stage'].save_approval_process(request=request, grForm=context['gr_form'], actionTaken=actionTaken, dateActionTaken=datetime.today(),
                                                         dayAssigned=datetime.today(),
                                                         approver=approver,
                                                         stage=1, approvalType=approval_type, comments=comments)



        error_messages = merge_dictionaries(error_messages, context['gr_form'].update_isApproved_and_isDeclined(request=request))

        if self.isApproved == True:
            # AssetFile.createAssetFile(assetData=self.get_data_for_excel(), GRFormID=self.formID, user=request.user)
            print(self.poNumber)
            GoodsReceivedApp.create_entry(poNumber=self.poNumber)
            try:
                docDate = datetime.today().date()
                response = createGR(HeadText=self.headerText, DocDate=docDate, RefNo=self.refNumber, formID=self.formID)
                if response['GRNo'] == None:
                    error_messages['fatal_errors'] = "Error with SAP! Please try again!"
                    context['users_stage'].actionTaken = None
                    context['users_stage'].dateActionTaken = None
                    context['users_stage'].save()
                    context['gr_form'].update_isApproved_and_isDeclined(request=request)
                    return error_messages
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error with SAP! Please try again!"
                context['users_stage'].actionTaken = None
                context['users_stage'].dateActionTaken = None
                context['users_stage'].save()
                context['gr_form'].update_isApproved_and_isDeclined(request=request)
                return error_messages
            error_messages = merge_dictionaries(error_messages,
                                                notify_approver(employee=self.employeeID, message_type='approved',
                                                                module=self.module, form=self, request=request))
        return error_messages

    def update_other_stages_because_user_changed_GR(self, context, request):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        if context['stages_claimed'] != None:
            for stage in context['stages_claimed']:
                if stage != context['users_stage']:
                    error_messages = merge_dictionaries(error_messages, stage.save_approval_process(actionTaken='',
                                                                                                    dayAssigned=datetime.today(),
                                                                                                    dateActionTaken=None,
                                                                                                    request=request))
                    if error_messages['fatal_errors'] != '':
                        return error_messages
                    # notify_approver(employee=stage.approver, form=context['gr_form'], message_type='next_approver', module='GR', request=request)
                    return error_messages
        return error_messages

    @staticmethod
    def get_context(request, formID):
        error_messages = {'fatal_errors': '', 'other_errors':[]}
        context = {}

        # Region Getting Office App Data
        # Get Cost Centers
        try:
            cost_centers = CostCenter.objects.all().order_by('costCenterName')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error retrieving Cost Center Data."
            return error_messages

        # Get Business Units
        try:
            business_units = BusinessUnit.objects.all().order_by('buName')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error retrieving Business Unit Data."
            return error_messages

        # Get Business Groups
        try:
            business_groups = BusinessGroup.objects.all().order_by('name')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error retrieving Business Group Data."
            return error_messages

        # Employees
        try:
            employees = Employee.objects.all().order_by('lastName')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error retrieving Employee List."
            return error_messages
        # endregion

        # Region Getting Data from GR
        # GRForm
        gr_form = GRForm.objects.filter(formID=formID).first()
        # gr_form.get_data_for_excel()
        if gr_form:
            # GRList
            try:
                gr_list = GRList.objects.filter(grForm=gr_form).order_by('pk')
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error retreiving GR Data. Please contact IT."
                return error_messages
            if gr_list:
                print("list objects found!")
            else:
                gr_list = None
            # GRFileUpload
            try:
                gr_files = GRFileUpload.objects.filter(grForm=gr_form)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error retreiving gr_files. Please contact IT."
                return error_messages
            if gr_files:
                print("uploaded files found!")
            else:
                gr_files = None
            # Separating gr_files into packaging_slip and attachments:
            packaging_slip = None
            attachments = []
            if gr_files != None:
                for file in gr_files:
                    if "packaging_slips" in file.location:
                        packaging_slip = file
                    if "attachments" in file.location:
                        attachments.append(file)
            if attachments == []:
                attachments = None
        else:
            gr_form = GRForm()
            gr_list = None
            gr_files = None
            packaging_slip = None
            attachments = None

        # region Getting Approval Process Data
        stages = GRApproversProcess.objects.filter(grForm=gr_form)
        warehouse_stage = None
        buyer_stage = None
        user_can_choose_warehouse = True
        user_can_choose_receiver = True
        stages_claimed = []
        users_stage = None

        if gr_form.isApproved:
            user_can_choose_warehouse = False
            user_can_choose_receiver = False

        if stages:
            for stage in stages:
                if stage.approvalType == "warehouse":
                    warehouse_stage = stage
                else:
                    buyer_stage = stage
                stages_claimed.append(stage)
                if stage.approver.associateID == request.session['user_id']:
                    users_stage = stage
                    if stage.approvalType == "warehouse":
                        user_can_choose_receiver = False
                    elif stage.approvalType == "buyer":
                        user_can_choose_warehouse = False
                else:
                    if stage.approvalType == "warehouse":
                        user_can_choose_warehouse = False
                    elif stage.approvalType == "buyer":
                        user_can_choose_receiver = False


        # Check if there is a buyers's stage. If not, create one
        if buyer_stage == None and gr_form.prForm != None:
            buyer_stage = GRApproversProcess()
            error_messages = merge_dictionaries(error_messages, buyer_stage.save_approval_process(request=request, grForm=gr_form, approvalType="buyer",
                                                    approver=gr_form.employee, stage=1, dayAssigned=datetime.today(), actionTaken=''))
            if error_messages['fatal_errors'] != '':
                return error_messages
            if gr_form.employee.associateID == request.session['user_id']:
                user_can_choose_receiver = True
                user_can_choose_warehouse = False


        if stages_claimed == []:
            stages_claimed = None
        # endregion

        # endregion

        # region Getting Data from PR
        # Get PR
        try:
            pr_form = gr_list[0].purchaseItem.form
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            print("Unable to retrieve PR form.")
            pr_form = None


        if pr_form != None:
        # Data only to Get if PR Form Exists:
            # Get Basic Info
            try:
                basic_info = PurchaseBasicInfo.objects.get(form=pr_form)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error retrieving data from PR form."
                return error_messages

            # Get Supplier Info
            try:
                supplier_info = SupplierInfo.objects.get(form=pr_form)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error retrieving data from PR form."
                return error_messages

            # Get Shipping Info
            try:
                shipping_info = ShippingInfo.objects.get(form=pr_form)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error retrieving data from PR form."
                return error_messages
        else:
            basic_info = None
            supplier_info = None
            shipping_info = None
        # endregion

        # Get SAP PR Post Date / Day PR was completely Approved
        sap_pr_post_date = ""
        try:
            sap_pr_post_date = str(PRApprovalProcess.objects.filter(formID=gr_list[0].purchaseItem).order_by("stage").last().date).split(" ")[0]
            print(f"PR post date: {sap_pr_post_date}")
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))

        # Get SAP GR post date / Day GR was completely approved
        sap_gr_post_date = None
        if gr_form.isApproved:
            for stg in stages_claimed:
                if sap_gr_post_date == None:
                    sap_gr_post_date = stg.dateActionTaken
                else:
                    if stg.dateActionTaken > sap_gr_post_date:
                        sap_gr_post_date = stg.dateActionTaken



        # SAP data
        print(gr_form.poNumber)
        sap_data = downloadPO(poNumber=gr_form.poNumber, plantCode=gr_form.plantCode)
        print(f"response: {sap_data}")
        # if sap_data[0]['PONO'] == None or sap_data == None:
        if sap_data == None:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['other_errors'].append("Error retrieving SAP GR Data. Please contact IT.")
        elif sap_data != None:
            index = 0
            for item in sap_data:
                # Give item the QR_Quantity of its item detail
                if gr_list != None:
                    item.grQuantity = gr_list[index].grQuantity
                    if gr_list[index].costCenter != None:
                        item.chosen_cost_center = gr_list[index].costCenter.costCenterCode
                    else:
                        item.chosen_cost_center = ""
                    item.gr_pk = gr_list[index].pk
                index += 1

        # Update context
        context.update({"pr_form": pr_form, "shipping_info": shipping_info, 'cost_centers': cost_centers, "sap_pr_post_date": sap_pr_post_date, "sap_gr_post_date": sap_gr_post_date,
                        "basic_info": basic_info, "supplier_info": supplier_info, 'gr_form': gr_form, 'po_num': gr_form.poNumber, "users_stage": users_stage,
                        'gr_list': gr_list, 'gr_files': gr_files, 'packaging_slip': packaging_slip, 'attachments': attachments, "stages_claimed": stages_claimed,
                        'warehouse_editable': user_can_choose_warehouse, 'buyer_editable': user_can_choose_receiver, "warehouse_stage": warehouse_stage,
                        "buyer_stage": buyer_stage, 'sap_data': sap_data, 'business_groups': business_groups, 'business_units': business_units, 'employees': employees})
        # Add context to returning value
        error_messages.update({"context": context})

        return error_messages


class GRList(models.Model):
    grForm = models.ForeignKey(GRForm, on_delete=models.CASCADE)
    purchaseItem = models.ForeignKey(PurchaseItemDetail, on_delete=models.CASCADE, blank=True, null=True)
    purchaseItemOther = models.CharField(max_length=50, blank=True, null=True)
    grQuantity = models.IntegerField(blank=True, null=True)
    costCenter = models.ForeignKey(CostCenter, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "GR List Item for purchase item: " + str(self.purchaseItem)

    def update_GRList(self, grForm=None, purchaseItem=None, grQuantity=None, costCenter=None):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        if grForm != None:
            self.grForm = grForm
        if purchaseItem != None:
            self.purchaseItem = purchaseItem
        if grQuantity != None:
            self.grQuantity = grQuantity
        if costCenter != None:
            self.costCenter = costCenter
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error saving GRList Item!'
        return error_messages


class GRApproversProcess(models.Model):
    grForm = models.ForeignKey(GRForm, on_delete=models.CASCADE)
    approver = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    stage = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    actionTaken = models.CharField(max_length=50, default=None, blank=True, null=True)
    comments = models.CharField(max_length=255, default=None, blank=True, null=True)
    dateActionTaken = models.DateTimeField(blank=True, null=True)
    dayAssigned = models.DateField(blank=True, null=True)
    approvalType = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.approver) + " " + self.approvalType + " for " + self.grForm.poNumber

    def save_approval_process(self, request, grForm=None, approver=None, stage=None, count=None, actionTaken=None, comments=None, dateActionTaken=None, dayAssigned=None, approvalType=None):
        error_messages = {'fatal_errors': ''}
        if grForm != None:
            self.grForm = grForm
        if approver != None:
            self.approver = approver
        if stage != None:
            self.stage = stage
        if count != None:
            self.count = count
        if actionTaken != None:
            self.actionTaken = actionTaken
        if comments != None:
            self.comments = comments
        if dateActionTaken != None:
            self.dateActionTaken = dateActionTaken
        if dayAssigned != None:
            self.dayAssigned = dayAssigned
        if approvalType != None:
            self.approvalType = approvalType
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error updating approval process'
            return error_messages

        error_messages = merge_dictionaries(error_messages, self.grForm.update_isApproved_and_isDeclined(request))

        return error_messages


class GRFileUpload(models.Model):
    grForm = models.ForeignKey(GRForm, on_delete=models.CASCADE)
    location = models.CharField(max_length=500, default='goods_recieved/')  # Ex: purchase/uploads
    file = models.FileField(upload_to=get_upload)
    description = models.CharField(max_length=500)

    @property
    def formID(self):
        return self.grForm.formID

    @property
    def fileName(self):
        return str(self.file).split(self.location, 1)[1]

    def add_GR_packaging_slip(self, grForm, file, form_id):
        self.grForm = grForm
        self.file = file
        self.location = 'goods_recieved/packaging_slips/'
        self.save()

    def add_GR_attachment(self, grForm, file, form_id, description):
        self.grForm = grForm
        self.file = file
        self.location = 'goods_recieved/attachments/'
        self.description = description
        self.save()

    @property
    def formID(self):
        return self.form.formID

    # region Functions

    def upload_packaging_files(self, request, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        try:
            self.grForm = context['gr_form']
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages[
                'fatal_errors'] = 'Error linking newly uploaded File to the form. Pleae try again. If this problem persists, please contact IT'
            return error_messages
        if request.FILES.get('packaging_slip') != None:
            new_file = GRFileUpload()
            try:
                new_file.add_GR_packaging_slip(grForm=context['gr_form'], file=request.FILES.get('packaging_slip'),
                                               form_id=context['gr_form'].pk)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = 'Error uploading the file. Pleae try again. If this problem persists, please contact IT'
                return error_messages
            error_messages.update({'slip': {
                "link_to_file": settings.BASE_URL + "/media/" + new_file.location + new_file.fileName,
                "file_name": new_file.fileName}})
        return error_messages

    def upload_attachment_files(self, request, context, all_post_data):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        try:
            self.grForm = context['gr_form']
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages[
                'fatal_errors'] = 'Error linking newly uploaded File to the form. Pleae try again. If this problem persists, please contact IT'
            return error_messages

        print("Files exist: " + str(request.FILES.get('attachment') != None))
        if request.FILES.get('attachment') != None:
            all_files = dict(request.FILES)
            index = 0
            for file in all_files['attachment']:
                new_file = GRFileUpload()
                try:
                    new_file.add_GR_attachment(grForm=context['gr_form'], file=file,
                                               form_id=context['gr_form'].pk, description=all_post_data['attachment_description'][index])
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages[
                        'fatal_errors'] = 'Error uploading the file. Pleae try again. If this problem persists, please contact IT'
                    return error_messages
                error_messages.update({'attachment' + str(index): {
                    "link_to_file": settings.BASE_URL + "/media/" + new_file.location + new_file.fileName,
                    "file_name": new_file.fileName}})
                index += 1

        return error_messages



class GoodsReceivedApp(models.Model):
    grForm = models.ForeignKey(GRForm, on_delete=models.CASCADE)
    poNumber = models.CharField(max_length=50, blank=True, null=True)
    poItem = models.CharField(max_length=50, blank=True, null=True)
    qty = models.DecimalField(max_digits=12, decimal_places=4)
    plantCode = models.CharField(max_length=50, blank=True, null=True)

    # region Properties

    # endregion Properties

    # region Functions
    @staticmethod
    def create_entry(poNumber):

        form_entries = GRForm.objects.filter(poNumber=poNumber)
        if form_entries:
            for entry in form_entries:
                items = GRList.objects.filter(grForm=entry)
                print(f"items: {items}")
                response = SAPFunctions.downloadPO(poNumber, entry.plantCode)
                if response != None:
                    index = 0
                    print(f"Response is set to {response}.")
                    for item in items:
                        # print(f"po item: {response[index]['POITEM']}")
                        # po item is wrong! should be po item on the GR form!
                        GoodsReceivedApp.objects.create(grForm=entry, poNumber=poNumber, poItem=response[index]['POITEM'], qty=item.grQuantity, plantCode=entry.plantCode)
                        index += 1
        else:
            raise Exception("No forms Exist with po Number!")
    # endregion Functions
