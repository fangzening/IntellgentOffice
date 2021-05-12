import enum
import sys
import traceback


from Smart_Office import settings
from office_app.models import Employee, Vendors
from purchase.models import *
import datetime
from django.db import models
from Smart_Office import settings
from goods_received.models import *
from office_app.models import Employee, Vendors
from purchase.models import SupplierInfo

'''
    Author: Jacob Lattergrass
    :param instance - the instance of the model
    :param filename - the name of the file you want
    :returns - download file location
'''
def get_upload(instance, filename):
    return '/'.join(filter(None, (instance.location, filename)))


# Create your models here.
class InvoiceForm(models.Model):
    formID = models.BigAutoField(primary_key=True)
    requestor = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='requestor')
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, related_name='vendor')
    creationDate = models.DateTimeField(auto_now=True)
    sapInvoiceNo = models.CharField(max_length=50)
    sapAccDocNo = models.CharField(max_length=50)
    manualPoNo = models.BooleanField(default=False) # If po has PR, manual PO is false. If it has no PR, then manual PO is True
    poNo = models.CharField(max_length=50, blank=True, null=True)
    currentStage = models.IntegerField(default=0, blank=True, null=True)
    isDeclined = models.BooleanField(default=False, blank=True, null=True)
    isApproved = models.BooleanField(default=False, blank=True, null=True)

    # region Properties
    def __str__(self):
        return "Invoice Form " + str(self.formID)

    @property
    def employeeID(self):
        buyer = PRApprovalProcess.objects.filter(stage=1, formID=PurchaseItemDetail.objects.filter(poNumber=self.poNo).first()).first().approverID
        return buyer

    @property
    def employee(self):
        return self.employeeID


    @property
    def sap_prefix(self):
        return "AP"

    @property
    def form_type(self):
        return "MRO Invoice"

    @property
    def form_url_without_base_url(self):
        return "mro_invoice/invoice/" + str(self.poNo)

    @property
    def full_url(self):
        return str(settings.BASE_URL) + "mro_invoice/invoice/" + str(self.poNo)

    @property
    def module(self):
        return "invoice"

    @property
    def advance_type(self):
        return None
    # endregion Properties

    # region Functions
    '''
        Author: Jacob Lattergrass
        :param self: The object instance
        :param invoiceNo: The invoice number returned from SAP
        :param poNo: The PO number assigned to the GR items
        :param sapAccDocNo: The SAP account document number returned from SAP
        :param manualPoNo(False): Whether this PO was generated manually or by SO
        This function is meant to create an invoice entry in the SO database. It still
        needs to be finished. Right now, though, it just creates the instance in the db.
    '''
    def create_invoice_entry(self, invoiceNo, poNo, sapAccDocNo, manualPoNo=False):
        gr = GRForm.objects.filter(poNumber=poNo).first()
        vendor = SupplierInfo.objects.get(form=gr.prForm).vendor
        self.sapInvoiceNo = invoiceNo
        self.requestor = gr.requester
        self.vendor = vendor
        self.sapAccDocNo = sapAccDocNo
        self.manualPoNo = manualPoNo
        self.poNo = poNo
        self.save()

    '''
    Author: Corrina Barr
        :param po_number: The po number associated with the invoice form
        This function is meant to get the variables that will be used in the template
        language on the mro invoice form page
    '''
    @staticmethod
    def get_context(po_number, request):
        context = {}

        gr_forms = GRForm.objects.filter(poNumber=po_number).order_by('pk')

        if not gr_forms.exists():
            return {'fatal_errors': 'Form not found with this PO number'}

        gr_lists = GRList.objects.filter(grForm__poNumber=po_number)
        supplier_info = SupplierInfo.objects.get(form=gr_forms[0].prForm)

        current_user = Employee.objects.get(associateID=request.session['user_id'])
        todays_date = datetime.today().date()
        context.update({'current_user': current_user, 'todays_date': todays_date})

        buyer = PRApprovalProcess.objects.filter(formID__poNumber=po_number, stage=1).first().approverID

        check_invoice = InvoiceForm.objects.filter(poNo=po_number).first()

        # region Get Buyer
        if buyer:
            purchase_request = PRApprovalProcess.objects.filter(formID__poNumber=po_number, stage=1).first().form
        else:
            purchase_request = None
            buyer_stage = GRApproversProcess.objects.filter(grForm__poNumber=po_number, approvalType='buyer').first()
            if buyer_stage:
                buyer = buyer_stage.approverID
            else:
                if check_invoice:
                    buyer = check_invoice.employeeID
                else:
                    buyer = None
        # endregion Get Buyer



        total_gr_amount = 0

        for item in gr_lists:
            print(f'Item Name: {item}')
            item_amount = item.purchaseItem.itemAmount * item.grQuantity
            total_gr_amount += item_amount

        if check_invoice:
            # region get data for existing invoice
            invoice_form = check_invoice
            invoice_basic_info = InvoiceBasicInfo.objects.filter(form=invoice_form).first()
            invoice_info = InvoiceInfo.objects.filter(form=invoice_form).first()
            files = InvoiceFileUpload.objects.filter(form=invoice_form)
            stages = InvoiceApproversProcess.objects.filter(formID=invoice_form).order_by('stage')
            invoice_gr_list = GRListItem.objects.filter(apForm=invoice_form).order_by('listItemID')
            if stages:
                print('There are stages!')
            else:
                stages = None
            # endregion
        else:
            if current_user != buyer and buyer != None:
                return {'fatal_errors': 'Only buyer can create this Invoice form'}
            else:
                # region create Invoice for PO
                invoice_form = InvoiceForm()
                # Check what manual po number is:
                items_with_po_no = PurchaseItemDetail.objects.filter(poNumber=po_number).first()

                if items_with_po_no:
                    manualPoNo = False
                else:
                    manualPoNo = True
                invoice_form.create_invoice_entry(poNo=po_number, invoiceNo='', sapAccDocNo='', manualPoNo=manualPoNo)

                invoice_basic_info = InvoiceBasicInfo()
                invoice_basic_info.create_entry([invoice_form,
                    gr_forms[0].businessGroup.legalEntity,
                    gr_forms[0].businessUnit,
                    gr_forms[0].businessGroup,
                    gr_forms[0].plantCode,
                    gr_forms[0].memo])

                invoice_info = InvoiceInfo()
                invoice_info.create_entry([invoice_form,
                    datetime.today().date(),
                    0,
                    total_gr_amount,
                    0,
                    0])

                invoice_gr_list = []
                for item in gr_lists:
                    invoice_gr = GRListItem()
                    invoice_gr.purchaseItem = item.purchaseItem
                    invoice_gr.costCenter = item.costCenter
                    invoice_gr.grQuantity = item.grQuantity
                    invoice_gr.apForm = invoice_form
                    invoice_gr.grNo = item.grForm.pk
                    invoice_gr.save()
                    invoice_gr_list.append(invoice_gr)

                files = None
                stages = None
                # endregion



        people_who_can_see_form = [invoice_form.employeeID]

        total_gr_amount = 0
        for item in invoice_gr_list:
            item_amount = item.purchaseItem.unitPrice * item.grQuantity
            total_gr_amount += item_amount

        if stages != None:
            for stage in stages:
                if stage.stage <= invoice_form.currentStage or invoice_form.isDeclined == True:
                    people_who_can_see_form.append(stage.approverID)

        po_doc_link = invoice_form.get_po_doc_link()

        context.update({'po_doc_link': po_doc_link,
                        'gr_forms': gr_forms,
                        'gr_lists': invoice_gr_list,
                        'po_num': po_number,
                        'supplier_info': supplier_info,
                        'total_gr_amount': total_gr_amount,
                        'invoice_form': invoice_form,
                        'invoice_basic_info': invoice_basic_info,
                        'invoice_info': invoice_info,
                        'stages': stages,
                        'files': files,
                        'people_who_can_see_form': people_who_can_see_form,
                        'purchase_request': purchase_request,
                        })
        return context

    def get_po_doc_link(self):
        po_number = self.poNo
        po_doc = settings.MEDIA_ROOT + "\purchase\po_documents\\" + po_number + ".pdf"
        po_doc_link = settings.BASE_URL + "/media/purchase/po_documents/" + po_number + ".pdf"
        # if there are multiple with po number in name, have to get one that has highest version number
        # data_dict['po_num'] + " version " + str(index) + '.pdf'
        doc_exists = os.path.exists(po_doc)
        if doc_exists == False:
            po_doc_link = None
        index = 2
        while doc_exists:
            check_doc = settings.MEDIA_ROOT + "\purchase\po_documents\\" + po_number + " version " + str(
                index) + ".pdf"
            doc_exists = os.path.exists(check_doc)
            if doc_exists:
                po_doc_link = settings.BASE_URL + "/media/purchase/po_documents/" + po_number + " version " + str(
                    index) + ".pdf"
                index += 1
        return po_doc_link

    '''
    This method is called in views.py when someone does something on the invoice form. 
    It sorts out which actions to take
    '''
    @staticmethod
    def handle_post_data(context, request):
        error_messages = {'fatal_errors': '', 'other_errors': []}

        if request.POST.get('submit_button') == 'Save' or request.POST.get('submit_button') == 'Submit':
            error_messages = merge_dictionaries(error_messages, InvoiceForm.save_whole_invoice(context, request))
            if error_messages['fatal_errors'] != '':
                return error_messages

        if request.POST.get('submit_button') == 'Submit':
            error_messages = merge_dictionaries(error_messages, context['invoice_form'].initialize_approval_process(request))
            if error_messages['fatal_errors'] != '':
                return error_messages
            context['invoice_form'].isDeclined = False
            context['invoice_form'].save()
            if error_messages['fatal_errors'] == '':
                messages.success(request, "Invoice Successfully Submitted!")

        elif request.POST.get('submit_button') == 'Approve':
            error_messages = merge_dictionaries(error_messages, approve_form(request, context['invoice_form'], InvoiceApproversProcess, None))
            if error_messages['fatal_errors'] == '':
                messages.success(request, "Invoice Successfully Approved!")

        elif request.POST.get('submit_button') == 'Decline':
            error_messages = merge_dictionaries(error_messages, decline_form(request=request, form=context['invoice_form'], approval_process_type=InvoiceApproversProcess))
            if error_messages['fatal_errors'] != '':
                return error_messages
            context['invoice_form'].currentStage = 0
            context['invoice_form'].save()
            if error_messages['fatal_errors'] == '':
                messages.success(request, "Invoice Successfully Declined!")

        elif request.POST.get('submit_button') == 'upload files':
            error_messages = merge_dictionaries(error_messages, InvoiceFileUpload.upload_files(request,
                                                                                               context))  # Will also give information about newly uploaded files to add to the template through js
            return error_messages

        elif request.POST.get('submit_button') == 'generate_po_doc':
            context['purchase_request'].generate_po_doc_and_send_to_buyer()
            error_messages['pdf_link'] = context['invoice_form'].get_po_doc_link()

        return error_messages

    def initialize_approval_process(self, request):
        error_messages = {"fatal_errors": "", "other_errors": []}

        businessUnit = EmployeeDepartment.objects.get(associateID=self.requestor).departmentID.businessUnit

        base_user = self.requestor
        include_base_user_in_process = True

        old_process_stages = InvoiceApproversProcess.objects.filter(stage__gt=0, formID=self)
        for stage in old_process_stages:
            stage.delete()

        error_messages = merge_dictionaries(error_messages,
                                            ProcessType.initialize_approval_process(
                                                form=self,
                                                businessUnit=businessUnit,
                                                approval_proccess_object_type=InvoiceApproversProcess,
                                                request=request,
                                                base_user=base_user,
                                                include_base_user_in_process=include_base_user_in_process
                                            )
                                            )

        return error_messages

    @staticmethod
    def save_whole_invoice(context, request):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        context['invoice_basic_info'].save_basic_info(form=context['invoice_form'],
                                                      company=None,
                                                      businessUnit=None,
                                                      businessGroup=None,
                                                      plantCode=None,
                                                      memo=request.POST.get('memo'))
        use_tax = True
        if request.POST.get('use_tax') == 'no':
            use_tax = False
        context['invoice_info'].save_invoice(form=context['invoice_form'], invDate=request.POST.get('invoice_date'), invAmount=request.POST.get('invoice_amount'),
                                             grAmount=request.POST.get('total_gr_amount'), taxAmount=request.POST.get('tax_amount'),
                                             shippingFee=request.POST.get('shipping_fee'), taxRate=request.POST.get('tax_rate'),
                                             useTax=use_tax, invoiceText=request.POST.get('invoice_text'))
        # region Delete rows
        all_post_data = dict(request.POST)
        # print(f"all post data: {all_post_data}")
        if 'deleted_row' in all_post_data.keys():
            if all_post_data['deleted_row'] != None:
                for row in all_post_data['deleted_row']:
                    for item in context['gr_lists']:
                        if item.pk == int(row):
                            item.delete()
        # endregion Delete rows
        error_messages = merge_dictionaries(error_messages, InvoiceFileUpload.upload_files(request, context)) # Will also give information about newly uploaded files to add to the template through js
        return error_messages
    # endregion Functions


class InvoiceBasicInfo(models.Model):
    basicInfoID = models.BigAutoField(primary_key=True)
    form = models.ForeignKey(InvoiceForm, on_delete=models.CASCADE, related_name='invoiceform')
    company = models.CharField(max_length=50, blank=True, null=True)
    businessUnit = models.CharField(max_length=50, blank=True, null=True)
    businessGroup = models.CharField(max_length=50, blank=True, null=True)
    plantCode = models.CharField(max_length=50, blank=True, null=True)
    memo = models.CharField(max_length=200, blank=True, null=True)

    # region Properties
    @property
    def formID(self):
        return self.form.formID

    @property
    def requestor(self):
        return self.form.requestor

    @property
    def vendor(self):
        return self.form.vendor

    @property
    def sapInvoiceNo(self):
        return self.form.sapInvoiceNo

    def sapAccDocNo(self):
        return self.form.sapAccDocNo
    # endregion Properties

    # region Functions
    @staticmethod
    def create_entry(values):
        if type(values) == list:
            InvoiceBasicInfo.objects.create(
                form=values[0],
                company=values[1],
                businessUnit=values[2],
                businessGroup=values[3],
                plantCode=values[4],
                memo=values[5]
            )
        else:
            InvoiceBasicInfo.objects.create(
                form=values['form'],
                company=values['company'] if 'company' in values else None,
                businessUnit=values['businessUnit'] if 'businessUnit' in values else None,
                businessGroup=values['businessGroup'] if 'businessGroup' in values else None,
                plantCode=values['plantCode'] if 'plantCode' in values else None,
                memo=values['memo'] if 'memo' in values else None
            )

    def save_basic_info(self, form=None, company=None, businessUnit=None, businessGroup=None, plantCode=None, memo=None):
        if form != None:
            self.form = form
        if company != None:
            self.company = company
        if businessUnit != None:
            self.businessUnit = businessUnit
        if businessGroup != None:
            self.businessGroup = businessGroup
        if plantCode != None:
            self.plantCode = plantCode
        if memo != None:
            self.memo = memo
        self.save()
    # endregion Functions


class InvoiceInfo(models.Model):
    infoID = models.BigAutoField(primary_key=True)
    form = models.ForeignKey(InvoiceForm, on_delete=models.CASCADE)
    invDate = models.DateField(default=datetime.today().date(), blank=True, null=True)
    invAmount = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    grAmount = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    taxAmount = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    shippingFee = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    taxRate = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    useTax = models.BooleanField(default=True, blank=True, null=True)
    invoiceText = models.CharField(max_length=100, blank=True, null=True)

    # region Properties
    @property
    def formID(self):
        return self.form.formID

    @property
    def requestor(self):
        return self.form.requestor

    @property
    def vendor(self):
        return self.form.vendor

    @property
    def sapInvoiceNo(self):
        return self.form.sapInvoiceNo

    def sapAccDocNo(self):
        return self.form.sapAccDocNo
    # endregion Properties

    # region Functions
    def save_invoice(self, form=None, invDate=None, invAmount=None, grAmount=None, taxAmount=None, shippingFee=None,
                     taxRate=None, useTax=None, invoiceText=None):
        if form != None:
            self.form = form
            print(f"setting form to {form}")
        if invDate != None:
            self.invDate = invDate
        if invAmount != None:
            self.invAmount = invAmount
        if grAmount != None:
            self.grAmount = grAmount
        if taxAmount != None:
            self.taxAmount = taxAmount
        if shippingFee != None:
            self.shippingFee = shippingFee
        if taxRate != None:
            self.taxRate = taxRate
        if useTax != None:
            self.useTax = useTax
        if invoiceText != None:
            self.invoiceText = invoiceText
        self.save()

    '''
        create_entry: Creates an entry of this object in the database.
        :param values: A key/value list of values OR an array of values
        
        IMPORTANT: If the values are passed through an array, then the order
        must follow the order of fields in the model (excluding the PK).
        You must also provide a value for ALL fields, even those with a default 
        value.
    '''
    @staticmethod
    def create_entry(values):
        if type(values) == list:
            InvoiceInfo.objects.create(
                form=values[0],
                invDate=values[1],
                invAmount=values[2],
                grAmount=values[3],
                taxAmount=values[4],
                useTax=values[5]
            )
        else:
            InvoiceInfo.objects.create(
                form=values['form'],
                invDate=values['invDate'] if 'invDate' in values else InvoiceInfo._meta.get_field('invDate').default,
                invAmount=values['invAmount'] if 'invAmount' in values else None,   # if this isn't found in the values, it defaults to None
                grAmount=values['grAmount'] if 'grAmount' in values else None,
                taxAmount=values['taxAmount'] if 'taxAmount' in values else None,
                useTax=values['useTax'] if 'useTax' in values else InvoiceInfo._meta.get_field('useTax').default
            )
    # endregion Functions


class GRListItem(models.Model):
    listItemID = models.BigAutoField(primary_key=True)
    apForm = models.ForeignKey(InvoiceForm, on_delete=models.CASCADE)
    grNo = models.IntegerField()
    # purchaseItem = models.ForeignKey(PurchaseItemDetail, on_delete=models.CASCADE, blank=True, null=True)
    purchaseItem = models.ForeignKey(PurchaseItemDetail, on_delete=models.CASCADE, blank=True, null=True)
    grQuantity = models.IntegerField(blank=True, null=True)
    costCenter = models.ForeignKey(CostCenter, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "GR List Item for purchase item: " + str(self.purchaseItem)

    # def update_GRList(self, grForm=None, purchaseItem=None, grQuantity=None, costCenter=None):
    #     error_messages = {'fatal_errors': '', 'other_errors': []}
    #     if grForm != None:
    #         self.grForm = grForm
    #     if purchaseItem != None:
    #         self.purchaseItem = purchaseItem
    #     if grQuantity != None:
    #         self.grQuantity = grQuantity
    #     if costCenter != None:
    #         self.costCenter = costCenter
    #     try:
    #         self.save()
    #     except:
    #         print('\n'.join(traceback.format_exception(*sys.exc_info())))
    #         error_messages['fatal_errors'] = 'Error saving GRList Item!'
    #     return error_messages


class InvoiceSAPApp(models.Model):
    poNo = models.CharField(max_length=50, blank=True, null=True)
    poItemNo = models.CharField(max_length=50, blank=True, null=True)
    grNumber = models.CharField(max_length=50, blank=True, null=True)
    itemQty = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    itemAmount = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    assignment = models.CharField(max_length=200, blank=True, null=True)
    headText = models.CharField(max_length=200, blank=True, null=True)


class InvoiceTaxUsed(models.Model):
    glAccount = models.CharField(max_length=50, blank=True, null=True)
    costCenter = models.CharField(max_length=50, blank=True, null=True)
    paymentType = models.CharField(max_length=1, default='C', blank=True, null=True)
    itemAmount = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    assignment = models.CharField(max_length=200, blank=True, null=True)
    headText = models.CharField(max_length=200, blank=True, null=True)


class InvoiceApproversProcess(models.Model):
    formID = models.ForeignKey(InvoiceForm, on_delete=models.CASCADE)
    approverID = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    stage = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    actionTaken = models.CharField(max_length=50, default=None, blank=True, null=True)
    comments = models.CharField(max_length=255, default=None, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    dayAssigned = models.DateField(blank=True, null=True)
    approvalType = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.approverID) + "stage " + str(self.stage) + " for " + self.formID.poNo

    def set_action_taken(self, actionTaken):
        self.actionTaken = actionTaken
        self.save()

    def create_approval_stage(self,  formID, approverID, stage, count):
        error_messages = {'fatal_errors': ''}
        self.formID = formID
        self.approverID = approverID
        self.stage = stage
        self.count = count
        try:
            self.save()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = 'Error updating approval process'
        return error_messages

    def count_approvers(self):
        temp = InvoiceApproversProcess
        rows = temp.objects.filter(stage=self.stage, formID=self.formID)
        ctr = 0
        for row in rows:
            ctr += 1
        return ctr

    def count_approved_forms_for_stage(self):
        temp = InvoiceApproversProcess
        rows = temp.objects.filter(stage=self.stage, formID=self.formID, count__gte=1)
        ctr = 0
        for row in rows:
            ctr += 1
        return ctr

class InvoiceFileUpload(models.Model):
    form = models.ForeignKey(InvoiceForm, on_delete=models.CASCADE)
    location = models.CharField(max_length=500, default='invoice/')  # Ex: purchase/uploads
    file = models.FileField(upload_to=get_upload)
    description = models.CharField(max_length=500)

    # This class tells where different file types go
    @staticmethod
    def where_to_upload_file(html_name_attribute):
        location = 'invoice/'
        if html_name_attribute == 'pr_file':
            location = 'invoice/purchase_request_files/'
        elif html_name_attribute == 'po_file':
            location = 'invoice/po_files/'
        elif html_name_attribute == 'gr_file':
            location = 'invoice/goods_recieved_files/'
        elif html_name_attribute == 'invoice_file':
            location = 'invoice/invoice_files/'
        elif html_name_attribute == 'ar_file':
            location = 'invoice/acceptance_report_files/'
        elif html_name_attribute == 'ps_file':
            location = 'invoice/packaging_slips/'
        return location


    # region Properties
    @property
    def formID(self):
        return self.form.formID

    @property
    def fileName(self):
        return str(self.file).split(self.location, 1)[1]
    # endregion Properties

    # region Functions

    # region save different files types
    def add_invoice_file(self, form, file, html_name_attribute):
        print("file name: " + str(html_name_attribute))
        self.form = form
        self.file = file
        self.location = self.where_to_upload_file(html_name_attribute)
        self.description = html_name_attribute
        self.save()
        print("saved file: " + str(file))

    @staticmethod
    def upload_files(request, context):
        error_messages = {'fatal_errors': '', 'other_errors': []}

        all_files = dict(request.FILES)
        print("all files inside: " + str(all_files))

        for file_html_name_attribute in all_files.keys():
            new_file = InvoiceFileUpload()

            new_file.add_invoice_file(form=context['invoice_form'], file=all_files[file_html_name_attribute][0], html_name_attribute=file_html_name_attribute)

            error_messages.update({'attachment' + str(file_html_name_attribute): {
                "link_to_file": settings.BASE_URL + "/media/" + new_file.location + new_file.fileName,
                "file_name": new_file.fileName}})

        return error_messages
