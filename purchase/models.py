import os
import sys
import traceback
from datetime import datetime
from pprint import pprint
from django.shortcuts import redirect

import pdfrw
from PyPDF2 import PdfFileMerger

from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Q
from django.http import *

from SAP import SAPFunctionsPrd
# from SAP.SAPFunctionsPrd import createAP
from Smart_Office import settings
from office_app.approval_functions import *
from office_app.models import *
# from .pr_custom_functions import us_state_abbrev

# Purchase Requisition
# from purchase.pr_custom_functions import get_item_that_was_updated=
from purchase.pr_custom_functions import us_state_abbrev

item_annotation_prefixes = ['item_name_', 'due_date_', 'part_no_', 'supplier_part_no_', 'item_desc_', 'quantity_',
                            'uom_', 'rev_', 'unit_price_', 'ext_price_']

'''
    Author: Jacob Lattergrass
    :param instance - the instance of the model
    :param filename - the name of the file you want
    :returns - download file location
'''


def get_upload(instance, filename):
    return '/'.join(filter(None, (instance.location, filename)))


class MaterialGroup(models.Model):
    matGroup = models.CharField(primary_key=True, max_length=10)
    matDesc = models.CharField(max_length=50)

    # region Properties
    def __str__(self):
        return self.matDesc

    def __repr__(self):
        return self.matGroup
    # endregion Properties


class UnitOfMeasurement(models.Model):
    uom = models.CharField(primary_key=True, max_length=5)
    uomDesc = models.CharField(max_length=25)

    # region Properties
    def __str__(self):
        return self.uom

    def __repr__(self):
        return self.uomDesc
    # endregion Properties


class PurchaseRequestForm(models.Model):
    formID = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    prNumber = models.CharField(max_length=50, blank=True,
                                null=True)  # => Generated in format: AFE20200601xxxx where xxxx represents a number from 1 to 9999
    prAmount = models.DecimalField(max_digits=14, decimal_places=4, blank=True,
                                   null=True)  # => Generated from subtotal + shipping costs
    currency = models.CharField(max_length=10, blank=True, null=True,
                                default="USD")  # Conversions can be done through an API. We just need the currency name
    creationDate = models.DateField(auto_now=True, blank=True, null=True)
    glAccount = models.ForeignKey(GLAccount, on_delete=models.CASCADE, blank=True, null=True)
    isCompleted = models.BooleanField(default=False, blank=True, null=True)

    # region Properties
    @property
    def isApproved(self):
        all_items = PurchaseItemDetail.objects.filter(form=self).count()
        completely_approved_items = PurchaseItemDetail.objects.filter(form=self, isApproved=True).count()
        if completely_approved_items >= all_items:
            return True
        else:
            return False

    @property
    def plantCode(self):
        return PurchaseBasicInfo.objects.get(form=self).plantCode

    @property
    def employeeID(self):
        return self.employee.associateID

    @property
    def legalEntity(self):
        return self.employee.legalEntity

    @property
    def glDescription(self):
        return self.glAccount.glDescription

    @property
    def sap_prefix(self):
        return "PR"

    @property
    def form_type(self):
        return "Purchase Request"

    @property
    def form_url_without_base_url(self):
        return "/purchase_request/" + str(self.pk) + "/"

    @property
    def full_url(self):
        return str(settings.BASE_URL) + "purchase_request/" + str(self.pk) + "/"

    @property
    def module(self):
        return "purchase"

    @property
    def advance_type(self):
        return None

    @property
    def totalItemCount(self):
        return len(PurchaseItemDetail.objects.filter(form=self))

    @property
    def totalAssetCount(self):
        return len(PurchaseItemAsset.objects.filter(itemDetail__form=self))

    @property
    def approved_items(self):
        return PurchaseItemDetail.objects.filter(form=self, isApproved=True)

    # endregion Properties

    # region Functions

    # region Static Functions

    '''
    Author: Corrina Barr
    If no error, returns context. if Error, returns error message
    '''

    @staticmethod
    def get_context(request, pk):
        context = {}

        # Today
        try:
            today = datetime.today().astimezone().date()
            context.update({"today": today})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving today's date. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Business Units
        try:
            business_units = BusinessUnit.objects.all().order_by('buName')
            context.update({"business_units": business_units})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving business unit data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        try:
            measurement_unit = UnitOfMeasurement.objects.all().order_by('uom')
            context.update({"measurement_unit": measurement_unit})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving Unit of Measurement data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Business Groups
        try:
            business_groups = BusinessGroup.objects.all().order_by('name')
            context.update({"business_groups": business_groups})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving business group data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Companies
        try:
            companies = LegalEntity.objects.all().order_by('entityName')
            context.update({"companies": companies})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving company data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Vendor Information
        try:
            vendors = Vendors.objects.all().order_by('vendorName')
            context.update({"vendors": vendors})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving vendor data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Cosign Information
        try:
            cosignees = Account.objects.all().exclude(employee__associateID='administrator').order_by('employee')
            context.update({"cosignees": cosignees})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving cosignee data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Material Groups
        try:
            material_groups = MaterialGroup.objects.all().order_by('matGroup')
            context.update({"material_groups": material_groups})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving business unit data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # GL Accounts
        try:
            gl_accounts = GLAccount.objects.all().order_by('glCode')
            context.update({"gl_accounts": gl_accounts})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving gl account data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Departments
        try:
            departments = CostCenter.objects.all().order_by('costCenterName')
            context.update({"departments": departments})
            # print(f"depts: {departments}")
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving department data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Building List
        try:
            context['building_list'] = Building.get_all_buildings()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving building list. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Purchase request information
        try:
            # from purchase.models import PurchaseRequestForm
            if pk == "new":
                purchase_request_form = PurchaseRequestForm()
                basic_info = PurchaseBasicInfo()
                supplier_info = SupplierInfo()
                # material_info = UnitOfMeasurement()
                # material_group = MaterialGroup()
                shipping_info = ShippingInfo()
                purchase_item_details = None
                purchase_item_assets = None
                files_link = PRFilesLink()
                uploaded_files = None
            else:
                purchase_request_form = PurchaseRequestForm.objects.get(pk=pk)
                basic_info = PurchaseBasicInfo.objects.get(form=purchase_request_form)
                supplier_info = SupplierInfo.objects.get(form=purchase_request_form)
                # material_info = UnitOfMeasurement.objects.get(form=purchase_request_form)
                # material_group = MaterialGroup.objects.get(form=purchase_request_form)
                shipping_info = ShippingInfo.objects.get(form=purchase_request_form)
                purchase_item_details_queryset = PurchaseItemDetail.objects.filter(form=purchase_request_form).order_by(
                    "pk")
                purchase_item_details = []
                if purchase_item_details_queryset:
                    for item in purchase_item_details_queryset:
                        purchase_item_details.append(item)
                purchase_item_assets = PurchaseItemAsset.objects.filter(
                    itemDetail__form=purchase_request_form).order_by("pk")
                files_link = PRFilesLink.objects.filter(form=purchase_request_form).first()
                uploaded_files = PRFileUpload.objects.filter(formLink=files_link)
                # print(f'Queryset: {purchase_item_details_queryset}')
                # pprint(purchase_item_details)
                if purchase_item_details:
                    pass
                else:
                    purchase_item_details = None
                if purchase_item_assets:
                    pass
                else:
                    purchase_item_assets = None
                # if material_group:
                #     print("Material exists")
                # else:
                #     material_group = None
                if uploaded_files:
                    pass
                else:
                    uploaded_files = None
                # print("uploaded files: " + str(uploaded_files))

            context.update({"purchase_request_form": purchase_request_form})
            context.update({"basic_info": basic_info})
            context.update({"supplier_info": supplier_info})
            # context.update({"material_info": material_info})
            # context.update({"material_group": material_group})
            context.update({"shipping_info": shipping_info})
            context.update({"purchase_item_details": purchase_item_details})
            context.update({"purchase_item_assets": purchase_item_assets})
            context.update({"files_link": files_link})
            context.update({"uploaded_files": uploaded_files})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving form data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Requestor
        try:
            if pk == "new":
                requestor = Employee.objects.get(associateID=request.session['user_id'])
            else:
                requestor = purchase_request_form.employee
            context.update({"pk": pk})
            context.update({"requestor": requestor})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving employee data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Current Employee
        try:
            current_employee = Employee.objects.get(associateID=request.session['user_id'])
            context.update({"current_employee": current_employee})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving employee data. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # If user can edit any unit prices:
        users_current_stages = {}
        try:
            details_to_edit = []
            if pk != "new":
                stages_query = PRApprovalProcess.objects.filter(formID__form__pk=pk, approverID=current_employee,
                                                                stage=1).order_by("pk")
                if stages_query:
                    for stage in stages_query:
                        if stage.stage == stage.formID.currentStage and (
                                stage.actionTaken == None or stage.actionTaken == "" or stage.actionTaken == "Declined" or stage.actionTaken == "Un-Declined"):
                            details_to_edit.append(stage.formID.pk)
                            users_current_stages.update({stage.formID.pk: stage})
            if details_to_edit == []:
                details_to_edit = None
            context.update({"details_to_edit": details_to_edit})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving data concerning buyers. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Check what rows user can approve/decline
        try:
            rows_to_approve = []
            if pk != "new":
                users_stages = PRApprovalProcess.objects.filter(formID__form__pk=pk, approverID=current_employee,
                                                                stage__gt=1)
                if users_stages:
                    for stage in users_stages:
                        if stage.formID.currentStage == stage.stage and (
                                stage.actionTaken == None or stage.actionTaken == ""):
                            rows_to_approve.append(stage.formID)
                            users_current_stages.update({stage.formID.pk: stage})
                if rows_to_approve == []:
                    rows_to_approve = None

                context.update({"rows_to_approve": rows_to_approve})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "Error retrieving data concerning form approvers. Please contact IT.<br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>"

        # Get dictionary of stages associated with each item that user can do stuff to
        context.update({"users_current_stages": users_current_stages})

        # Get all stages for the form:
        if pk != "new":
            context.update(
                {"forms_stages": PRApprovalProcess.objects.filter(formID__form__pk=pk).order_by("formID", "stage")})
        else:
            context.update({"forms_stages": None})

        # Get items that user can see:
        items_user_can_see = []
        if context['forms_stages'] != None:
            for approval_stage in context["forms_stages"]:
                if approval_stage.approverID == context['current_employee'] or context['current_employee'] == context[
                    'purchase_request_form'].employee:
                    items_user_can_see.append(approval_stage.formID)

        context.update({"items_user_can_see": items_user_can_see})

        # Check if user can view form:
        context.update({"user_can_view_form": False})

        # First check if current employee is creator of form
        if context['current_employee'] == context['requestor']:
            context["user_can_view_form"] = True
        else:
            # Else, check if the employee is in the approval list for the form and currently needs to approve the form or has already approved the form
            approvers_who_can_see = purchase_request_form.get_all_people_who_can_see_form()
            if approvers_who_can_see:
                if context['current_employee'] in approvers_who_can_see:
                    context["user_can_view_form"] = True

        # region Get Items that need PO Doc Generated
        items_that_need_PO_doc_generated = []
        if context['purchase_item_details'] != None:
            for item in context['purchase_item_details']:
                user_is_buyer = False
                items_highest_stage = 0
                for stage in context['forms_stages']:
                    if stage.approverID == context['current_employee'] and stage.stage == 1:
                        user_is_buyer = True
                    if stage.formID == item:
                        if stage.stage > items_highest_stage:
                            items_highest_stage = stage.stage
                if item.currentStage >= items_highest_stage and user_is_buyer and items_highest_stage > 1:
                    items_that_need_PO_doc_generated.append(item)
        if items_that_need_PO_doc_generated == []:
            items_that_need_PO_doc_generated = None
        context.update({"items_that_need_PO_doc_generated": items_that_need_PO_doc_generated})
        # endregion

        return context

    @staticmethod
    def accountant_approve_PR_items(request, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}

        old_stages = {}
        for item_to_update in context['rows_to_approve']:
            old_stages.update({item_to_update: item_to_update.currentStage})
            # Then approve them
            error_messages = merge_dictionaries(error_messages,
                                                approve_form(request, item_to_update, PRApprovalProcess, None))
            if error_messages['fatal_errors'] != '':
                return error_messages

        # Check if the approver is Accountant manager and Initiate SAP
        approver_role = None
        if EmployeeDepartment.objects.get(associateID=request.user.associateID).roleID not in ["", None]:
            approver_role = EmployeeDepartment.objects.get(associateID=request.user.associateID).roleID.title

        if (approver_role == "Accountant Manager"):
            error_messages = merge_dictionaries(error_messages,
                                                context['purchase_request_form'].create_sap_tables_and_call_sap())

            if error_messages['fatal_errors'] != '':
                # region If there's an error with SAP, then un-approve
                users_stages_for_this_form = PRApprovalProcess.objects.filter(
                    formID__form=context['purchase_request_form'])
                for item_to_update in context['rows_to_approve']:
                    item_to_update.currentStage = old_stages[item_to_update]
                    item_to_update.save()
                    for stage in users_stages_for_this_form:
                        if stage.formID == item_to_update:
                            stage.actionTaken = None
                            stage.date = None
                            stage.save()
                # endregion

        return error_messages

    # vv updates cost for buyer vv
    @staticmethod
    def buyer_update_cost(request, all_post_data, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        if 'Finish' == request.POST.get('submit_button'):
            # print(context['purchase_item_details'])
            # print(f'Full Context: {context}')
            items_to_update = context['purchase_item_details']

            # region Before SAP Check
            index = 0
            for item_to_update in items_to_update:
                # Item index in all post data will be same as it's index in context
                item_to_update.unitPrice = all_post_data['unit_price'][index]
                item_to_update.itemAmount = all_post_data['amount'][index]
                # print(f"at first material group is: {item_to_update.matGroup}")
                item_to_update.matGroup = all_post_data['material_group'][index]
                # print(f"setting material group to : {item_to_update.matGroup}")
                try:
                    item_to_update.save()
                    # print(f"saved material group to : {item_to_update.matGroup}")
                except:
                    error_messages[
                        'fatal_errors'] += 'Error updating unit price of items. Please Try again. If this issue persists, please contact IT.'
                    return error_messages

                # Get approval process object for item
                error_messages = merge_dictionaries(error_messages,
                                                    item_to_update.initialize_PR_approval_process(request,
                                                                                                  all_post_data_index=index))
                index += 1
            # endregion Before SAP Check

            # Have to exit for loop so that if there are any errors with SAP it doesn't go to the next stage yet
            error_messages = merge_dictionaries(error_messages, context[
                'purchase_request_form'].generate_po_and_notify_buyers_if_any_stages_ready(context, request))
            if error_messages['fatal_errors'] != '':
                return error_messages

            # region After SAP Check
            index = 0
            for item_to_update in items_to_update:
                try:
                    current_stage = PRApprovalProcess.objects.get(formID=item_to_update, stage=1)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages[
                        'fatal_errors'] += "Error getting validation that you can actually update an item. Try reloading the page and see if you have already approved the item. If the page still wants you to approve the item after you reload it, please contact IT."
                    return error_messages
                # current_stage.actionTaken = 'Updated and sent to approvers'
                current_stage.actionTaken = "Approved"
                current_stage.date = datetime.now().astimezone()
                try:
                    current_stage.save()
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages[
                        'fatal_errors'] += 'Error updating form process. Please Try again. If this issue persists, please contact IT.'
                    # return error_messages
                index += 1
            # endregion After SAP Check

        return error_messages

    def approve_or_decline_selected_items(self, request, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        all_post_data = dict(request.POST)
        original_stages = {}

        # Checkboxes only show on post data when they are selected
        index = 0
        for value in all_post_data["item_checkbox_value"]:
            if value == 'on':
                original_stages.update({index: context['rows_to_approve'][index].currentStage})
                if request.POST.get("submit_button") == "Approve Selected Items":
                    error_messages = merge_dictionaries(error_messages,
                                                        approve_form(request, context['rows_to_approve'][index],
                                                                     PRApprovalProcess, None))
                else:
                    # print(f"declining form: {context['rows_to_approve'][index]}")
                    error_messages = merge_dictionaries(error_messages,
                                                        decline_form(request, context['rows_to_approve'][index],
                                                                     PRApprovalProcess))
                    # print("declined form")
                # Current Stage is updated here but not when it checks it in the check if ready for PO function:
                # print(f"item: {context['rows_to_approve'][index]} \ncurrent stage: {context['rows_to_approve'][index].currentStage}\nfinal stage: {context['rows_to_approve'][index].final_stage_number}")
            index += 1

        # For some reason, it is saying that current stage is not updated stage and so it is not creating a PO for the item
        error_messages = merge_dictionaries(error_messages, context[
            'purchase_request_form'].generate_po_and_notify_buyers_if_any_stages_ready(context, request))

        if error_messages['fatal_errors'] != '':
            # Undo approve if there was an error with SAP
            index = 0
            for value in all_post_data["item_checkbox_value"]:
                if value == 'on':
                    users_stage = PRApprovalProcess.objects.get(formID=context['purchase_item_details'][index],
                                                                approverID__associateID=request.user.associateID)
                    context['purchase_item_details'][index].currentStage = original_stages[index]
                    users_stage.actionTaken = None
                    context['purchase_item_details'][index].save()
                index += 1
        return error_messages

    # vv Creates initial stages for buyers vv
    def invite_buyers(self, request, context):
        error_messages = {"fatal_errors": "", 'other_errors': []}
        # print(f'my post: {request.POST}')
        # print(len(request.POST['supplier_pn']))
        objs = dict(request.POST)
        # for index in range(len(request.POST['supplier_pn'])):
        # for obj in objs['supplier_pn']:
        #     temp_item_detail = PurchaseItemDetail()
        #     temp_item_detail.update_purchase_item_detail(form=self, matGroup=None, supplierPn=objs['supplier_pn'][index],
        #                                                    itemDesc=objs['item_description'][index], expectedDate=None,
        #                                                    costCenterCode=objs['cost_center'][index],
        #                                                    unitPrice=objs['unit_price'][index], quantity=objs['quantity'][index],
        #                                                    itemAmount=objs['amount'][index], glAccount=objs['gl_account'][index],
        #                                                 unitOfMeasurement=objs['unit_of_measurement'][index]
        #                                                    )
        #     index += 1
        all_items = PurchaseItemDetail.objects.filter(form=self)
        # print(all_items)
        buyer_stages = []
        # print('This is the invite_buyers function')

        index = 0
        for item in all_items:
            print(item)
            print(item.costCenterCode)
            item.costCenterCode = CostCenter.objects.get(costCenterCode=objs['cost_center'][index])

            item.currentStage = 1
            item.save()
            # print("Item cost center code: " + str(item.costCenterCode))
            approver = context['basic_info'].businessUnit.buBuyer
            # Check if buyer is requestor
            if approver != self.employee:
                new_process = PRApprovalProcess(formID=item, count=0, stage=1, approverID=approver)
                new_process.dayAssigned = datetime.now().astimezone()
                new_process.save()
                # print("saved process: " + str(new_process))
                buyer_stages.append(new_process)
            # If buyer is requestor, skip the requestor stage and initialize the approval process
            # if request.POST.get('submit_button') == 'Save' and response_data['result'] == "":
            # print('Attempting to save...')
            #     # context = PurchaseRequestForm.get_context(request, form_pk)
            #     if context['purchase_item_details'] == None:
            #         print(f"Items: {context['purchase_item_details']}")
            #         print('There is nothing in the details')
            #     else:
            #         print('Item deetails exist')
            else:
                error_messages = merge_dictionaries(error_messages, item.initialize_PR_approval_process(request=request,
                                                                                                        all_post_data_index=index))
                item.currentStage = 2
                item.save()
            index += 1

        self.prNumber = self.generate_pr_num()
        self.isCompleted = True
        self.save()

        notified_buyers = []
        for stage in buyer_stages:
            if stage.approverID not in notified_buyers:
                error_messages = merge_dictionaries(error_messages,
                                                    notify_approver(message_type="next_approver", module="purchase",
                                                                    employee=stage.approverID, form=self,
                                                                    request=request))
                notified_buyers.append(stage.approverID)

        return error_messages

    def generate_pr_num(self):
        # AFEyearmonthdatexxx
        companyShorthand = PurchaseBasicInfo.objects.get(form=self).company.compShorthand
        year = datetime.now().astimezone().year
        day = datetime.now().astimezone().day
        month = datetime.now().astimezone().month

        lastFormWithPrNum = PurchaseRequestForm.objects.filter(~Q(prNumber=" "), prNumber__isnull=False,
                                                               creationDate=datetime.today().date()).order_by(
            "prNumber").last()

        if lastFormWithPrNum is not None:
            last3digits = int(lastFormWithPrNum.prNumber[-3:])

            return companyShorthand + str(year)[2:4] + str(month) + str(day) + str(last3digits + 1).zfill(3)

        else:
            return companyShorthand + str(year)[2:4] + str(month) + str(day) + str(1).zfill(3)

    def update_pr_form(self, employee, prAmount, currency, creationDate, prNumber=None, ):
        error_messages = {"fatal_errors": '', "other_errors": []}
        self.employee = employee
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error linking you to the PR. Please try again or contact IT"
            return error_messages
        if prNumber != None:
            self.prNumber = prNumber
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error saving PR number. Please try again or contact IT"
            return error_messages
        self.prAmount = prAmount
        self.creationDate = creationDate
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error Saving PR Amount. Please try again or contact IT"
            return error_messages
        self.currency = currency
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error saving currency. Please try again or contact IT"
            return error_messages
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error saving creation date. Please try again or contact IT"
            return error_messages
        self.save()
        return error_messages

    # vvv This function is called whenever the form is saved or submitted BEFORE the buyer is added to the approval process vvv
    @staticmethod
    def update_purchase_request_information(request, context):
        # region Setting Function Variables
        is_submitting = False
        if request.POST.get('submit_button') == 'Finish':
            is_submitting = True
        error_messages = {'fatal_errors': '', 'other_errors': []}
        # endregion

        # region PurchaseRequestForm
        all_post_data = dict(request.POST)
        pprint(all_post_data)
        pr_amount = PurchaseRequestForm.get_pr_amount(all_post_data)

        index = 0

        # print(f'JACOB WAS HERE: {all_post_data}')
        currency = request.POST.get('currency')
        if currency == "" or currency is None:
            currency = "USD"
        error_messages = merge_dictionaries(error_messages, context['purchase_request_form'].update_pr_form(
            employee=context['requestor'],
            prAmount=pr_amount,
            currency=currency,
            creationDate=datetime.today().astimezone().date()
        ))
        if error_messages['fatal_errors'] != "":
            return error_messages
        # endregion

        # vvv Will return this value at the end of the function vvv
        new_pk = context['purchase_request_form'].pk
        error_messages['new_pk'] = new_pk
        # ^^^ It is needed to update context dictionary so that if on new it doesn't keep creating new forms ^^^

        # region PurchaseBasicInfo
        try:
            company_chosen = False
            for comp in context['companies']:
                if comp.entityName == request.POST.get('company'):
                    company = comp
                    company_chosen = True
            if company_chosen == False:
                if is_submitting:
                    error_messages['fatal_errors'] = "Invalid company chosen. Please choose a valid company"
                    return error_messages
                else:
                    company = None
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            if is_submitting:
                error_messages['fatal_errors'] = "Error retrieving company data. Please contact IT."
                return error_messages
            else:
                company = None
        try:
            bu_chosen = False
            for unit in context['business_units']:
                if unit.pk == request.POST.get('business_unit'):
                    bu = unit
                    bu_chosen = True
            if bu_chosen == False:
                if is_submitting:
                    error_messages['fatal_errors'] = "Invalid business unit chosen. Please choose a valid business unit"
                    return error_messages
                else:
                    bu = None
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            if is_submitting:
                error_messages['fatal_errors'] = "Error retrieving business unit data. Please contact IT."
                return error_messages
            else:
                bu = None
        error_messages = merge_dictionaries(error_messages, context['basic_info'].update_basic_info(
            form=context['purchase_request_form'],
            company=company,
            businessUnit=bu,
            plantCode=request.POST.get('plant_code'),
            project=request.POST.get('project'),
            purpose=request.POST.get('purpose'),
            businessGroup=request.POST.get('business')
        ))
        if error_messages['fatal_errors'] != "":
            return error_messages
        # endregion

        # region SupplierInfo
        try:
            ven_chosen = False
            for ven in context['vendors']:
                try:
                    new_ven_pk = int(request.POST.get('vendor_name'))
                except:
                    new_ven_pk = None
                if ven.pk == new_ven_pk:
                    vendor = ven
                    ven_chosen = True
            if ven_chosen == False:
                if request.POST.get('submit_button') == 'Save and Submit form for approval':
                    error_messages['fatal_errors'] = "Error retrieving vendor data. Please contact IT."
                    return error_messages
                else:
                    vendor = None
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            if is_submitting:
                error_messages['fatal_errors'] = "Error saving vendor data. Please contact IT."
                return error_messages
            else:
                vendor = None
        error_messages = merge_dictionaries(error_messages, context['supplier_info'].update_supplier(
            form=context['purchase_request_form'], vendor=vendor, email=request.POST.get('email')))
        # endregion

        # region ShippingInfo
        try:
            error_messages = merge_dictionaries(error_messages, context['shipping_info'].update_shipping_info(
                form=context['purchase_request_form'],
                name=request.POST.get('shipping_name'),
                address=request.POST.get('shipping_address'),
                memo=request.POST.get('memo')))
            if error_messages['fatal_errors'] != "":
                return error_messages
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            if is_submitting:
                error_messages['fatal_errors'] = 'Error creating shipping information. Please contact IT.'
                return error_messages
        # endregion

        # region PurchaseItemDetail
        # Delete old items
        # print(f'Ctx b4: {context["purchase_item_details"]}')
        # print("****************************************Purchase item details: " + str(context['purchase_item_details']))
        # If user is requestor
        if context['details_to_edit'] == None:
            if context['purchase_item_details'] != None:
                for item in context['purchase_item_details']:
                    print("deleting purchase item: " + str(item))
                    item.delete()
            try:
                item_nums = all_post_data['supplier_pn']
                items_exist = True
            except:
                items_exist = False

            count = 0
            print(f"AllPostData: {all_post_data}")
            # print(f"AllPostData - Arrival: {all_post_data['arrival_date']}")
            if items_exist:
                print('Items exist')
                details_template_ids = {}
                # pprint("asset numbers: " + str(all_post_data['asset_number']))
                for item in all_post_data['supplier_pn']:
                    try:
                        gl_account = GLAccount.objects.get(glDescription=all_post_data['gl_account'][count])
                    except:
                        gl_account = None
                    try:
                        print('filling cost_center')
                        cost_center = CostCenter.objects.get(costCenterName=all_post_data['department'][count])
                        print(f'cost_center is not empty: {cost_center}')
                    except:
                        error_messages['fatal_errors'] = 'Invalid Cost Center Code'
                        return error_messages

                    print('In the for loop')
                    try:
                        mat_group = all_post_data['material_group'][count]
                    except:
                        mat_group = None

                    new_detail = PurchaseItemDetail()
                    new_detail.update_purchase_item_detail(form=context['purchase_request_form'],
                                                           matGroup=mat_group,
                                                           supplierPn=all_post_data['supplier_pn'][count],
                                                           itemDesc=all_post_data['item_description'][count],
                                                           costCenterCode=cost_center,
                                                           unitPrice=all_post_data['unit_price'][count],
                                                           quantity=all_post_data['quantity'][count],
                                                           itemAmount=all_post_data['amount'][count],
                                                           glAccount=gl_account,
                                                           unitOfMeasurement=all_post_data['unit_of_measurement'][
                                                               count],
                                                           )

                    # print("new detail pk: " + str(new_detail.pk))
                    details_template_ids.update({all_post_data['template_item_id'][count]: new_detail})
                    count += 1
            # Region Assets
            if context['purchase_item_assets'] != None:
                for asset in context['purchase_item_assets']:
                    asset.delete()
            try:
                asset_num = all_post_data['asset_numberdisplay']
                assets_exist = True
            except:
                assets_exist = False
            if assets_exist:
                count = 0
                for asset in all_post_data['asset_numberdisplay']:
                    PurchaseItemAsset().save_asset(details_template_ids[all_post_data['template_asset_id'][count]],
                                                   assetClass=all_post_data['asset_class'][count],
                                                   techCat1=all_post_data['tech_category1'][count],
                                                   techCat2=all_post_data['tech_category2'][count],
                                                   techCat3=all_post_data['tech_category3'][count],
                                                   techCat4=all_post_data['tech_category4'][count])
                    count += 1
        # if user is buyer:
        else:
            count = 0
            for item in context['purchase_item_details']:
                try:
                    gl_account = GLAccount.objects.get(glDescription=all_post_data['gl_account'][count])
                except:
                    gl_account = None
                try:
                    # print(all_post_data['department'])
                    # print(f"Dept: {all_post_data['department'][count]}")
                    cost_center = CostCenter.objects.get(costCenterName=all_post_data['department'][count])
                    # print(cost_center)
                except:
                    error_messages['fatal_errors'] = 'Invalid Cost Center Code'
                    return error_messages
                item.update_purchase_item_detail(form=context['purchase_request_form'],
                                                 matGroup=all_post_data['material_group'][count],
                                                 supplierPn=all_post_data['supplier_pn'][count],
                                                 itemDesc=all_post_data['item_description'][count],
                                                 costCenterCode=cost_center,
                                                 unitPrice=all_post_data['unit_price'][count],
                                                 quantity=all_post_data['quantity'][count],
                                                 itemAmount=all_post_data['amount'][count],
                                                 glAccount=gl_account,
                                                 # expectedDate=all_post_data['arrival_date'][count],
                                                 unitOfMeasurement=all_post_data['unit_of_measurement'][count], )
                count += 1
            # endregion
        # endregion

        # region Files
        error_messages = merge_dictionaries(error_messages,
                                            context['files_link'].upload_files(request=request, context=context))
        # endregion
        return error_messages

    @staticmethod
    def get_pr_amount(all_post_data):
        pr_amount = 0
        # Generated from subtotals
        try:
            subtotals = all_post_data['amount']
            there_are_subtotals = True
        except:
            there_are_subtotals = False
        if there_are_subtotals:
            for subtotal in all_post_data['amount']:
                if subtotal != '':
                    pr_amount += float(subtotal)
        return pr_amount

    # endregion Static Functions

    # region Non-Static Functions
    def generate_po(self, compShorthand):
        print("In PO Generating Function")
        date = str(datetime.today()).replace("-", "")[2:8]
        letters_for_month = {'01': '1', '02': '2', '03': '3', '04': '4', '05': '5', '06': '6', '07': '7', '08': '8',
                             '09': '9', '10': 'A', '11': 'B', '12': 'C'}
        year = date[0:2]
        month = date[2:4]
        day = date[4:6]
        month = letters_for_month[month]
        date = year + month + day
        items_with_similar_po = PurchaseItemDetail.objects.filter(poNumber__contains=compShorthand + date).order_by(
            "poNumber")
        new_num = "00"
        if items_with_similar_po:
            for item in items_with_similar_po:
                most_recent_appended_num = int(
                    items_with_similar_po[len(items_with_similar_po) - 1].poNumber.replace(compShorthand + date, ""))
                new_num = str(most_recent_appended_num + 1)
                if len(new_num) == 1:
                    new_num = "0" + new_num
                else:
                    new_num = "00"
        po = compShorthand + date + new_num
        print(po)
        return po

    def generate_po_and_notify_buyers_if_any_stages_ready(self, context, request):
        print("In generate PO and Notify")
        error_messages = {"fatal_errors": '', "other_errors": []}
        any_items_ready = False
        items_ready = []

        if context['rows_to_approve'] == None:
            for item in context['purchase_item_details']:
                if item.is_ready_to_generate_po_and_notify_buyer:
                    items_ready.append(item)
        else:
            for item in context['rows_to_approve']:
                if item.is_ready_to_generate_po_and_notify_buyer:
                    items_ready.append(item)
        # print(f"Items ready: {items_ready}")
        if items_ready != []:
            print("item Ready array")
            try:
                compShorthand = PurchaseBasicInfo.objects.get(form=context['pk']).company.compShorthand
                po_num = self.generate_po(compShorthand)
                print(f"Generated PO: {po_num}")
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error with generating po. Please try again later."
                return error_messages

            buyers_notified = []
            for item in items_ready:
                item.poNumber = po_num
                item.save()
                # print(f"po number: {item.poNumber}")
                if item.buyer not in buyers_notified:
                    # print(f"notifying buyer: {item.buyer}")
                    notify_approver(employee=item.buyer, message_type='generate_po', form=self, request=request)
                    buyers_notified.append(item.buyer)
        return error_messages

    def get_all_people_who_can_see_form(self):
        people_who_can_see_form = [self.employee]
        all_stages = PRApprovalProcess.objects.filter(formID__form=self)
        if all_stages:
            for stage in all_stages:
                if stage.approverID not in people_who_can_see_form:
                    people_who_can_see_form.append(stage.approverID)
        return people_who_can_see_form

    def create_sap_tables_and_call_sap(self):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        # Create data in SAP tables
        existing_sap_table = PurchaseRequestApp.objects.filter(form=self)
        if existing_sap_table:
            existing_sap_table.delete()
        error_messages = merge_dictionaries(PurchaseRequestApp.create_entry(self),
                                            error_messages)
        if error_messages['fatal_errors'] != '':
            return error_messages
        return error_messages

    @staticmethod
    def generate_data_for_po_(prefix):
        data_dict = {}
        building = Building.objects.get(locAddress='11210 County Line Road')
        if prefix != 'company_':
            data_dict[prefix + "company_name"] = building.legalEntity.entityName
        else:
            data_dict["company_name_1"] = building.legalEntity.entityName
            data_dict['comany_address_line_1'] = building.locAddress
        data_dict[prefix + 'address_line_1'] = building.locAddress
        if building.locState in us_state_abbrev.keys():
            state = us_state_abbrev[building.locState]
        else:
            state = building.locState
        data_dict[prefix + 'address_line_2'] = building.locCity + ", " + state + " " + str(building.locZip)
        data_dict[prefix + 'address_line2'] = building.locCity + ", " + state + " " + str(building.locZip)
        if building.locCountry == "United States of America":
            data_dict[prefix + 'country'] = "USA"
        else:
            data_dict[prefix + 'country'] = building.locCountry.upper()
        return data_dict

    def generate_po_doc_and_send_to_buyer(self):
        data_dict = {}
        items_that_need_PO_doc_generated = []
        all_stages_for_form = PRApprovalProcess.objects.filter(formID__form=self)
        all_item_details = PurchaseItemDetail.objects.filter(form=self)
        supplier_info = SupplierInfo.objects.get(form=self)

        # region Getting items to include on the PO
        for item in all_item_details:
            user_is_buyer = False
            items_highest_stage = 0
            for stage in all_stages_for_form:
                if stage.stage == 1:
                    user_is_buyer = True
                if stage.formID == item:
                    if stage.stage > items_highest_stage:
                        items_highest_stage = stage.stage
            if item.currentStage >= items_highest_stage and user_is_buyer and items_highest_stage > 1:
                items_that_need_PO_doc_generated.append(item)
        if items_that_need_PO_doc_generated == []:
            return HttpResponseForbidden(
                "There are no items for this form that can be put on the PO document right now.")
        # endregion Getting items to include on the PO

        # region Putting data into data dictionary

        # region Vendor Data
        data_dict['vendor_company'] = str(
            LegalEntity.objects.filter(sapCompCode=str(supplier_info.vendor.companyCode)).first().entityName)
        # print("vendor company: " + str(data_dict['vendor_company'])) # idk why it isn't showing on the pdf, field name is correct and data is not empty string
        data_dict['vendor_person_full_name'] = supplier_info.vendor.vendorName
        data_dict['vendor_code'] = supplier_info.vendor.vendorCode
        data_dict['vendor_address_line_1'] = supplier_info.vendor.supplierAddress.split(",")[
            0]  # Sample 1st Line: 14100 LEETS BIR RD
        data_dict['vendor_address_line_2'] = supplier_info.vendor.supplierAddress.split(",")[-2] + ", " + \
                                             supplier_info.vendor.supplierAddress.split(",")[
                                                 -1]  # Sample 2nd Line: STURTEVANT, WI 53177
        # data_dict['vendor_country'] = supplier_info.vendor.supplierCountry
        # endregion Vendor Data

        # region Buyer Data
        buyer = PurchaseBasicInfo.objects.get(form=self).businessUnit.buBuyer
        data_dict['buyer_name'] = buyer.full_name
        data_dict['buyer_phone'] = buyer.mainPhone
        data_dict['buyer_email'] = buyer.email
        # endregion

        # region Ship To
        shipping_info = ShippingInfo.objects.get(form=self)
        building = Building.objects.get(locAddress=shipping_info.address)
        data_dict['ship_to_company_name'] = building.legalEntity.entityName
        data_dict['ship_to_address_line_1'] = building.locAddress
        if building.locState in us_state_abbrev.keys():
            state = us_state_abbrev[building.locState]
        else:
            state = building.locState
        data_dict['ship_to_address_line_2'] = building.locCity + ", " + state + " " + str(building.locZip)
        if building.locCountry == "United States of America":
            data_dict['ship_to_country'] = "USA"
        else:
            data_dict['ship_to_country'] = building.locCountry.upper()
        # endregion Ship To

        # region Bill To and Invoice To
        data_dict = merge_dictionaries(data_dict, self.generate_data_for_po_('company_'))
        data_dict = merge_dictionaries(data_dict, self.generate_data_for_po_('bill_to_'))
        data_dict = merge_dictionaries(data_dict, self.generate_data_for_po_('invoice_to_'))
        # endregion Bill To and Invoice To

        # region PO number and date
        basic_info = PurchaseBasicInfo.objects.get(form=self)
        data_dict['po_date'] = str(datetime.today().astimezone().strftime("%b %d, %Y"))
        data_dict['po_num'] = items_that_need_PO_doc_generated[0].poNumber
        # endregion PO number and date

        # region stuff from table
        data_dict['supplier_code'] = supplier_info.vendor.vendorCode
        data_dict['plant_code'] = basic_info.plantCode
        # vvv These two right here will actually get their data from SAP later on
        # data_dict['payment_terms'] = "45 DAYS AFTER INVOICE DATE"
        # data_dict['inco_terms'] = "FOB DESTINATION"
        # endregion stuff from table

        # region Items Section
        index = 0
        data_dict['items_on_next_page'] = ""
        for item in items_that_need_PO_doc_generated:
            if index < 6:
                data_dict['item_name_' + str(index)] = str(index + 1)
                # data_dict['due_date_' + str(index)] = str(item.expectedArrivalDate.date())
                # data_dict['part_no_' + str(index)] = ""
                data_dict['supplier_part_no_' + str(index)] = str(item.supplierPn)
                data_dict['item_desc_' + str(index)] = item.itemDesc
                data_dict['quantity_' + str(index)] = str(item.quantity)
                data_dict['uom_' + str(index)] = item.unitOfMeasurement
                # data_dict['rev_' + str(index)] = ""
                data_dict['unit_price_' + str(index)] = str(item.unitPrice)
                data_dict['ext_price_' + str(index)] = "{:.2f}".format(
                    round(float(item.unitPrice) * float(item.quantity), 2))
            else:
                data_dict['items_on_next_page'] = "more items on next page..."
            index += 1
        # endregion Items Section

        # region Signature Section
        data_dict['buyer_name_2'] = data_dict['buyer_name']
        data_dict['signature_date'] = datetime.today().astimezone().strftime("%b %d, %Y")
        data_dict['total_po_amount'] = "{:.2f}".format(
            PurchaseItemDetail.get_total_amount_for_items(items_that_need_PO_doc_generated))
        data_dict['currency'] = self.currency
        # endregion Signature Section

        # endregion Putting data into data dictionary

        # region Creating PDF
        # print(f"VENDOR COMPANY BEFORE GENERATE PO: {data_dict['vendor_company']}")
        pdf_file_info = self.generate_po_document_pdf(data_dict=data_dict,
                                                      items_for_po=items_that_need_PO_doc_generated)
        # Create file download response
        if os.path.exists(pdf_file_info['pdf_file']):
            return pdf_file_info['pdf_link']
        else:
            raise FileNotFoundError
        # endregion Creating PDF

        # region Updating Items in Database

        # endregion Updating Items in Database

    '''
        This function will generate pdf form from the data provided and return file response
        Based on Function written By: Zaawar Ejaz
        Who edited it for the PR: Corrina Barr
        :param dict: Dictionary
        :return: File response
    '''

    def generate_po_document_pdf(self, data_dict, items_for_po):
        global extra_page_template_pdf
        try:
            # region Filling in Fields
            # Read PDF Template
            template_pdf = pdfrw.PdfReader(
                os.path.join(settings.STATIC_ROOT, 'purchase\\assets\\Purchase_Order_Template.pdf'))
            template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
            annotations = template_pdf.pages[0]['/Annots']
            # Write on field using data dictionary
            for annotation in annotations:
                if annotation['/Subtype'] == '/Widget':
                    if annotation['/T']:
                        key = annotation['/T'][1:-1]
                        # print(f"key: {key}") # It seems vendor_company in data_dict but not in annotations! But it shows in csv file...
                        if key == 'vendor_company':
                            # print(f"VENDOR COMPANY FOUND: {data_dict[key]}")
                            pass
                        if key in data_dict.keys():
                            # print("key in dictionary")
                            if key == 'vendor_company':
                                # print(f"VENDOR COMPANY: {data_dict[key]} going to be added!")
                                pass
                            annotation.update(pdfrw.PdfDict(V=data_dict[key], Ff=1))

            # Write PDF File
            pdf_name = data_dict['po_num'] + '.pdf'
            # print("writing pdf file")
            pdf_file = settings.MEDIA_ROOT + '\\purchase\\po_documents\\' + pdf_name
            try:
                pdfrw.PdfWriter().write(pdf_file, template_pdf)
                # print("no error writing pdf")
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                # print('error writing pdf')
                writing_pdf_error = True
                index = 2
                while (writing_pdf_error):
                    pdf_name = data_dict['po_num'] + " version " + str(index) + '.pdf'
                    pdf_file = settings.MEDIA_ROOT + '\\purchase\\po_documents\\' + pdf_name
                    try:
                        pdfrw.PdfWriter().write(pdf_file, template_pdf)
                        writing_pdf_error = False
                    except:
                        writing_pdf_error = True
            # endregion Filling in Fields

            # region Adding Extra Items
            index = 6
            pdf_index = 0
            if "item_name_" + str(index) in data_dict.keys():
                # print("adding extra items")
                pdfs = [pdf_file]
                pages = 2

                for annotation in annotations:
                    if pdf_index > 29:
                        pdf_index = 0
                    # region Creating New Extra Page to Write on
                    if pdf_index == 0:
                        extra_page_template_pdf = pdfrw.PdfReader(
                            os.path.join(settings.STATIC_ROOT, 'purchase\\assets\\Purchase_Order_Extra_Table.pdf'))
                        extra_page_template_pdf.Root.AcroForm.update(
                            pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
                        annotations = extra_page_template_pdf.pages[0]['/Annots']
                    # endregion Create New Extra Page to Write on
                    # region Adding Data to page
                    if annotation['/Subtype'] == '/Widget':
                        if annotation['/T']:
                            key = annotation['/T'][1:-1]
                            # print(f"page {pages} key: {key}")
                            if key in data_dict.keys():
                                # print("key in dictionary")
                                annotation.update(pdfrw.PdfDict(V=data_dict[key], Ff=1))
                    # endregion Adding Data to page
                    # region Writing on New Page
                    if pdf_index == 29 or "item_name_" + str(index + 1) not in data_dict.keys():
                        # print(f"adding extra page: {data_dict['po_num']}_page_{pages}.pdf")
                        extra_page = settings.MEDIA_ROOT + '\\purchase\\po_documents\\' + data_dict[
                            'po_num'] + '_page_' + str(pages) + '.pdf'
                        pdfrw.PdfWriter().write(extra_page, extra_page_template_pdf)
                        pdfs.append(extra_page)
                        pages += 1
                    # endregion Writing on New Page
                    pdf_index += 1
                    index += 1

                # region Merging Files
                merger = PdfFileMerger()
                # print("merging files")
                for pdf in pdfs:
                    # print(f'merging {pdf}')
                    merger.append(pdf)
                merger.write(pdf_file)  # <--- pdf being written to
                merger.close()
                # endregion
            # endregion Extra Adding Items

            pdf_link = settings.BASE_URL + "/media/purchase/po_documents/" + pdf_name
            return {'pdf_file': pdf_file, 'pdf_link': pdf_link}
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            raise Exception("Error generating PDF File")
    # endregion Non-Static Functions

    # endregion Functions


class PurchaseBasicInfo(models.Model):
    form = models.ForeignKey(PurchaseRequestForm, on_delete=models.CASCADE)
    basicInfoID = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(LegalEntity, on_delete=models.CASCADE, blank=True, null=True)
    businessGroup = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, blank=True, null=True)
    businessUnit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, blank=True, null=True)
    plantCode = models.CharField(max_length=100, blank=True, null=True)
    project = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.CharField(max_length=100, blank=True, null=True)

    # region Properties
    @property
    def formID(self):
        return self.form.formID

    # endregion Properties

    # region Functions
    def update_basic_info(self, form, company=None, businessGroup=None, businessUnit=None, plantCode=None, project=None,
                          purpose=None):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        self.form = form
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error linking basic information to form"
            return error_messages
        if businessUnit != None:
            try:
                self.businessUnit = businessUnit
                self.save()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error saving business unit data."
        if company != None:
            try:
                self.company = company
                self.save()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error saving company data."
        if businessGroup != None:
            try:
                self.businessGroup = BusinessGroup.objects.get(name=businessGroup)
                self.save()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error saving business group data"
        if plantCode != None:
            try:
                self.plantCode = plantCode
                self.save()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error saving plant code"
        if project != None:
            try:
                self.project = project
                self.save()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error saving project name"
        if purpose != None:
            try:
                self.purpose = purpose
                self.save()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error saving purpose"
        self.save()
        return error_messages
    # endregion Functions


class SupplierInfo(models.Model):
    form = models.ForeignKey(PurchaseRequestForm, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # region Properties
    @property
    def formID(self):
        return self.form.formID

    @property
    def vendorName(self):
        return self.vendor.vendorName

    @property
    def vendorCode(self):
        return self.vendor.vendorCode

    @property
    def vendorAddress(self):
        return self.vendor.supplierAddress

    @property
    def vendorContact(self):
        return self.vendor.supplierContact

    @property
    def vendorTelephone(self):
        return self.vendor.supplierTelephone

    # endregion Properties

    # region Functions
    def update_supplier(self, form, vendor, email):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        try:
            self.form = form
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error linking supplier data to form. Please contact IT.'
            return error_messages
        try:
            self.vendor = vendor
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error linking vendor data to form. Please contact IT.'
            return error_messages
        try:
            self.email = email
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error linking supplier email data to form. Please contact IT.'
            return error_messages
        return error_messages
    # endregion Functions


class ShippingInfo(models.Model):
    form = models.ForeignKey(PurchaseRequestForm, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    memo = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=128, blank=True, null=True)

    # region Properties
    @property
    def formID(self):
        return self.form.formID

    # endregion Properties

    # region Functions
    @staticmethod
    def create_shipping_info(form, name, address, memo=None):
        if len(ShippingInfo.objects.filter(form=form)) > 0:
            ShippingInfo.objects.get(form=form).update_shipping_info(form, name, address, memo)
            return
        ShippingInfo.objects.create(form=form, name=name, address=address, memo=memo)

    def update_shipping_info(self, form, name, address, memo):
        error_messages = {"fatal_errors": "", "other_errors": []}
        try:
            self.form = form
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error linking shipping info to the form. Please contact IT.'
            return error_messages
        try:
            self.name = name
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error linking name under shipping info to the form. Please contact IT.'
            return error_messages
        try:
            self.address = address
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error linking shipping info address to the form. Please contact IT.'
            return error_messages
        try:
            self.memo = memo
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error linking shipping info memo to the form. Please contact IT.'
        return error_messages
    # endregion Functions


class PurchaseItemDetail(models.Model):
    form = models.ForeignKey(PurchaseRequestForm, on_delete=models.CASCADE)
    detailID = models.BigAutoField(primary_key=True)
    assetNo = models.CharField(max_length=25, blank=True, null=True, default="")
    matGroup = models.CharField(max_length=25, blank=True, null=True)  # Will this be a FK?
    supplierPn = models.CharField(max_length=25, blank=True, null=True)
    itemDesc = models.CharField(max_length=100, blank=True, null=True)
    # department = models.CharField(max_length=100, blank=True, null=True)
    costCenterCode = models.ForeignKey(CostCenter, on_delete=models.CASCADE, blank=True, null=True)
    unitPrice = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    itemAmount = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    glAccount = models.ForeignKey(GLAccount, on_delete=models.CASCADE, blank=True, null=True)
    currentStage = models.IntegerField(default=0, blank=True, null=True)
    isApproved = models.BooleanField(default=False)
    isDeclined = models.BooleanField(default=False)
    poNumber = models.CharField(max_length=50, blank=True, null=True)
    expectedArrivalDate = models.DateTimeField(blank=True, null=True)
    unitOfMeasurement = models.CharField(max_length=25, blank=True, null=True, default='EA')

    # region Properties
    @property
    def formID(self):
        return self.form.formID

    @property
    def employeeID(self):
        return self.form.employee.associateID

    @property
    def employee(self):
        return self.form.employee

    @property
    def sap_prefix(self):
        return "PR"

    @property
    def form_type(self):
        return "Purchase Request"

    @property
    def form_url_without_base_url(self):
        return "/purchase_request/" + str(self.form.pk) + "/"

    @property
    def full_url(self):
        return str(settings.BASE_URL) + "purchase_request/" + str(self.form.pk) + "/"

    @property
    def module(self):
        return "purchase"

    @property
    def advance_type(self):
        return None

    @property
    def assets(self):
        assets = PurchaseItemAsset.objects.filter(itemDetail=self)
        if assets:
            return assets
        else:
            return None

    @property
    def glCode(self):
        return self.glAccount.glCode

    @property
    def glDescription(self):
        return self.glAccount.glDescription

    @property
    def department_object(self):
        return self.costCenterCode

    @property
    def final_stage_number(self):
        stage = PRApprovalProcess.objects.filter(formID=self).order_by('stage').last().stage
        return stage

    @property
    def buyer(self):
        buyer = PRApprovalProcess.objects.filter(formID=self, stage=1).first().approverID
        return buyer

    @property
    def is_ready_to_generate_po_and_notify_buyer(self):
        # If current stage is accountant return true
        approver = PRApprovalProcess.objects.get(formID=self, stage=self.currentStage).approverID
        if EmployeeDepartment.objects.get(associateID=approver).roleID not in ["", None]:
            approver_role = EmployeeDepartment.objects.get(associateID=approver).roleID.title
        else:
            approver_role = None

        if approver_role == "Accountant" and self.isApproved == False and self.currentStage != 1 and self.poNumber == None:
            print("checking....")
            return True

    # endregion Properties

    # region Functions
    @staticmethod
    def get_total_amount_for_items(item_list):
        total_amount = 0.00
        for item in item_list:
            total_amount += (float(item.itemAmount) * float(item.quantity))
        total_amount = round(total_amount, 2)
        return total_amount

    def get_cost_center_object(self):
        return CostCenter.objects.get(costCenterCode=self.costCenterCode)

    def accountant_update_purchase_item(self, request, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        all_post_data = dict(request.POST)
        # Item index in all post data will be same as it's index in context
        try:
            self.glAccount = GLAccount.objects.get(
                glDescription=all_post_data['gl_account'][context['purchase_item_details'].index(self)])
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error retrieving GL Account! Please contact IT!'
            return error_messages
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error saving changes! Please contact IT!'
            return error_messages

        try:
            # Remove old assets:
            old_assets = PurchaseItemAsset.objects.filter(itemDetail__pk=self.pk)
            print("delete " + str(old_assets))
            for asset in old_assets:
                asset.delete()
        except:
            error_messages['fatal_errors'] = 'Error updating Assets! Please contact IT!'
            return error_messages

        # Get indexes of template_asset_id where template_asset_id value = "0" + pk of this item
        index = 0
        if 'template_asset_id' in all_post_data.keys():

            try:
                for pk in all_post_data['template_asset_id']:
                    # print('checking asset:' + str(pk)[1:] + " against " + str(self.pk))
                    # Replace with new assets:
                    if str(pk)[1:] == str(self.pk):
                        # print("SAVING ASSET: " + str(pk))
                        new_asset = PurchaseItemAsset()
                        new_asset.save_asset(self,
                                             assetClass=all_post_data['asset_class'][index],
                                             techCat1=all_post_data['tech_category1'][index],
                                             techCat2=all_post_data['tech_category2'][index],
                                             techCat3=all_post_data['tech_category3'][index],
                                             techCat4=all_post_data['tech_category4'][index])
                    index += 1
            except:
                error_messages['fatal_errors'] = 'Error updating Assets! Please contact IT!'
                return error_messages

        return error_messages

    def update_purchase_item_detail(self, form, matGroup, supplierPn, itemDesc,
                                    costCenterCode, unitPrice, quantity, itemAmount, glAccount,
                                    unitOfMeasurement=None, poNumber=None, assetNo=None, expectedDate=None):
        print("----------" + str(unitOfMeasurement))
        cc_codes = []
        cc_names = []
        for cc_code in CostCenter.objects.values_list('costCenterCode'):
            cc_codes.append(cc_code[0])
        for cc_name in CostCenter.objects.values_list('costCenterName'):
            cc_names.append(cc_name[0])

        self.form = form
        if poNumber != None:
            self.poNumber = poNumber
        if assetNo != None:
            self.assetNo = assetNo
        else:
            self.assetNo = ""
        if expectedDate != "":
            self.expectedArrivalDate = expectedDate
        if unitOfMeasurement != None:
            self.unitOfMeasurement = unitOfMeasurement
        self.matGroup = matGroup
        self.supplierPn = supplierPn
        self.itemDesc = itemDesc
        # print(self.costCenterCode)

        # self.costCenterCode = CostCenter.objects.get(costCenterCode=costCenterCode)
        if costCenterCode in cc_codes:
            self.costCenterCode = CostCenter.objects.get(costCenterCode=costCenterCode)
        elif costCenterCode in cc_names:
            self.costCenterCode = CostCenter.objects.get(costCenterName=costCenterCode)
        else:
            self.costCenterCode = CostCenter.objects.get(costCenterName=costCenterCode)

        if unitPrice != "":
            self.unitPrice = unitPrice
        else:
            self.unitPrice = 0
        if quantity != "":
            self.quantity = quantity
        else:
            self.quantity = 0
        if itemAmount != "":
            self.itemAmount = itemAmount
        else:
            self.itemAmount = 0
        if glAccount == '' or glAccount == None:
            self.glAccount = None
        else:
            self.glAccount = GLAccount.objects.get(glDescription=glAccount)
        self.save()
        # print(f"Expected arrival date after save: {self.expectedArrivalDate}")

    # vvv This function initializes the approval process for the Item vvv
    # vvv To be called after buyer does their thing vvv
    def initialize_PR_approval_process(self, request, all_post_data_index=0):
        error_messages = {"fatal_errors": "", "other_errors": []}

        businessUnit = self.costCenterCode.businessUnit

        old_process_stages = PRApprovalProcess.objects.filter(stage__gt=1, formID=self)
        for stage in old_process_stages:
            stage.delete()

        error_messages = merge_dictionaries(error_messages,
                                            ProcessType.initialize_approval_process(
                                                form=self,
                                                businessUnit=businessUnit,
                                                approval_proccess_object_type=PRApprovalProcess,
                                                request=request,
                                                url_form=self.form,
                                                all_post_data_index=all_post_data_index,
                                                starting_stage=2)
                                            )

        return error_messages

    # endregion Functions


class PurchaseItemAsset(models.Model):
    itemDetail = models.ForeignKey(PurchaseItemDetail, on_delete=models.CASCADE)
    assetClass = models.CharField(max_length=50, blank=True, null=True)
    techCat1 = models.CharField(max_length=50, blank=True, null=True)
    techCat2 = models.CharField(max_length=50, blank=True, null=True)
    techCat3 = models.CharField(max_length=50, blank=True, null=True)
    techCat4 = models.CharField(max_length=50, blank=True, null=True)

    # region Properties
    @property
    def formID(self):
        return self.itemDetail.form.formID

    @property
    def detailID(self):
        return self.itemDetail.detailID

    # endregion Properties

    # region Functions
    def save_asset(self, itemDetail, assetClass, techCat1, techCat2, techCat3, techCat4):
        self.itemDetail = itemDetail
        self.assetClass = assetClass
        self.techCat1 = techCat1
        self.techCat2 = techCat2
        self.techCat3 = techCat3
        self.techCat4 = techCat4
        self.save()
    # endregion Functions


class PRFilesLink(models.Model):
    form = models.ForeignKey(PurchaseRequestForm, on_delete=models.CASCADE)

    @property
    def formID(self):
        return self.form.formID

    # region Functions
    def get_files(self):  # <-- This should work but I'm not certain
        return PRFilesLink.objects.filter(formLink=self)

    def get_files_for_form(self):
        return PRFilesLink.objects.filter(formLink=self, location__contains='purchase/')

    def upload_files(self, request, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        try:
            self.form = context['purchase_request_form']
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages[
                'fatal_errors'] = 'Error linking newly uploaded File to the form. Please try again. If this problem persists, please contact IT'
            return error_messages

        # print(f"all post data: {request.POST}")
        # print(f"all files: {request.FILES}")
        all_files = dict(request.FILES)
        file_info = {}
        file_ids = ['fileselect[]', 'filedrag']
        for id in file_ids:
            if request.FILES.get(id) != None:
                try:
                    for file in all_files[id]:
                        print(f"Uploading file: {file}")
                        new_file = PRFileUpload()
                        new_file.add_PR_file(formLink=self, file=file,
                                             form_id=context['purchase_request_form'].pk)
                        file_info.update({'file_' + str(new_file.pk): {
                            "link_to_file": settings.BASE_URL + "media/" + new_file.location + new_file.fileName,
                            "file_name": new_file.fileName}})
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages[
                        'fatal_errors'] = 'Error uploading the file. Pleae try again. If this problem persists, please contact IT'
                    return error_messages
        return file_info


class PRFileUpload(models.Model):
    formLink = models.ForeignKey(PRFilesLink, on_delete=models.CASCADE)
    location = models.CharField(max_length=500, default='purchase/')  # Ex: purchase/uploads
    file = models.FileField(upload_to=get_upload)

    @property
    def formID(self):
        return self.formLink.form.formID

    @property
    def fileName(self):
        return str(self.file).split(self.location, 1)[1]

    def add_PR_file(self, formLink, file, form_id):
        self.formLink = formLink
        self.file = file
        self.location = 'purchase/'
        self.save()


class PRApprovalProcess(models.Model):
    formID = models.ForeignKey(PurchaseItemDetail, on_delete=models.CASCADE)
    approverID = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID', blank=True, null=True)
    stage = models.IntegerField(primary_key=False, default=0)
    count = models.IntegerField(primary_key=False, default=0)
    actionTaken = models.CharField(max_length=50, default=None, blank=True, null=True)
    comments = models.CharField(max_length=255, default=None, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    dayAssigned = models.DateField(blank=True, null=True)
    approvalType = models.CharField(max_length=20, blank=True, null=True)

    # region Properties
    def __str__(self):
        return str(self.approverID) + " stage " + str(self.stage) + " for Item Detail " + str(self.form.pk)

    @property
    def form(self):
        return self.formID

    # region Functions
    def set_action_taken(self, actionTaken):
        self.actionTaken = actionTaken
        self.save()

    def create_approval_stage(self, formID, approverID, stage, count):
        self.formID = formID
        self.approverID = approverID
        self.stage = stage
        self.count = count
        self.save()

    def count_approvers(self):
        temp = PRApprovalProcess
        rows = temp.objects.filter(stage=self.stage, formID=self.formID)
        ctr = 0
        for row in rows:
            ctr += 1
        return ctr

    def count_approved_forms_for_stage(self):
        temp = PRApprovalProcess
        rows = temp.objects.filter(stage=self.stage, formID=self.formID, count=1)
        ctr = 0
        for row in rows:
            ctr += 1
        return ctr

    # @staticmethod
    # Adds cosigner and notify them
    # def add_approver(approver):
    #     pass

    @staticmethod
    def add_cosigner(item, cosigner, currentStage):
        error_messages = {}
        PRApprovalProcess.objects.create(formID=item, approverID=cosigner, stage=currentStage, count=0,
                                         dayAssigned=datetime.now().astimezone())
        approvers = PRApprovalProcess.objects.filter(formID=item)
        for approver in approvers:
            if approver.stage <= currentStage:
                continue
            approver.stage += 1
        pass
    # endregion Functions


class PurchaseRequestApp(models.Model):
    form = models.ForeignKey(PurchaseRequestForm, on_delete=models.CASCADE)
    supplierPn = models.CharField(max_length=25)
    assetNo = models.CharField(max_length=25)
    itemDesc = models.CharField(max_length=100)  # PR Number
    costCenterCode = models.CharField(max_length=50)  # Non existant when its an asset
    matGroup = models.CharField(max_length=25)
    glAccount = models.CharField(max_length=50)  # Non existant when its an asset
    quantity = models.IntegerField()
    itemAmount = models.DecimalField(max_digits=14, decimal_places=4)  # Unit Price
    currency = models.CharField(max_length=10, default="USD")

    @staticmethod
    def create_entry(prForm):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        entry = PurchaseRequestApp()

        if type(prForm) is not PurchaseRequestForm:
            raise TypeError(f'You must pass a PurchaseRequestForm type object.')

        pr_items = PurchaseItemDetail.objects.filter(form=prForm).exclude(poNumber=None)
        for item in pr_items:
            if len(PurchaseItemAsset.objects.filter(itemDetail=item)) is 0:
                # print('in the if statement')
                entry.form = prForm
                entry.currency = prForm.currency
                entry.supplierPn = item.supplierPn
                entry.assetNo = item.assetNo
                entry.itemDesc = item.itemDesc
                entry.costCenterCode = item.costCenterCode.costCenterCode
                entry.matGroup = item.matGroup
                entry.glAccount = item.glAccount.glCode
                entry.quantity = item.quantity
                entry.itemAmount = item.itemAmount
                entry.save()
                entry = PurchaseRequestApp()
                continue

            pr_assets = PurchaseItemAsset.objects.filter(itemDetail=item)
            for asset in pr_assets:
                entry.form = prForm
                entry.currency = prForm.currency
                entry.supplierPn = item.supplierPn
                entry.assetNo = item.assetNo
                entry.itemDesc = item.itemDesc
                entry.costCenterCode = ""
                entry.matGroup = item.matGroup
                entry.glAccount = ""
                entry.quantity = item.quantity
                entry.itemAmount = item.itemAmount
                entry.save()
                entry = PurchaseRequestApp()

        # Once is ready, un-comment this:
        try:
            basicInfo = PurchaseBasicInfo.objects.get(form=prForm)
            supplierInfo = SupplierInfo.objects.get(form=prForm)
            for item in pr_items:
                response = SAPFunctions.createPO(formID=str(prForm.formID),
                                                 companyCode=str(basicInfo.company.sapCompCode),
                                                 vendorCode=str(supplierInfo.vendor.vendorCode),
                                                 plantCode=str(basicInfo.plantCode),
                                                 PONumber=item.poNumber)
                if response['PONO'] == None:
                    error_messages['fatal_errors'] = "Error with SAP Webservice. Please try again later."
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error with SAP Webservice. Please try again later."
        return error_messages
