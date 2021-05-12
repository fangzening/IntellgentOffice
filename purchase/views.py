import json
import sys
import traceback

from django.contrib import messages
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import *
from office_app.sessions import *
# Create your views here.
from purchase.models import *
from purchase.pr_custom_functions import *
from purchase.models import *
from office_app.approval_functions import *
from goods_received.models import *
from purchase.models import *


def pr_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'pr_dashboard/index.html', {'is_buyer':is_user_buyer(request)})
    else:
        return redirect('../../accounts/login/?next=/purchase_request/')


def my_purchase(request):
    if request.user.is_authenticated:
        return render(request, 'purchase/submitted_pr.html', {})
    else:
        return redirect('../../accounts/login/?next=/purchase_request/submitted_purchase')


def approve_purchase_list(request):
    if request.user.is_authenticated:
        return render(request, 'purchase/approve_pr.html', {})
    else:
        return redirect('../../accounts/login/?next=/purchase_request/purchase_to_approve')


#
# ========DataTable function for purchase========####
# ========== Author: Josua Ataansuyi========####

# def my_purchase_api(request):
#     if request.user.is_authenticated:
#         try:
#             if request.method == "GET":
#                 submitted = []
#                 for form in PurchaseRequestForm.objects.filter(employee=request.session['user_id']):
#                     submitted.append({
#                         'formID': form.formID,
#                         'pr_Number': form.prNumber,
#                         'creationDate': form.creationDate,
#                         'project': form.purchasebasicinfo_set.all()[0].project if len(
#                             form.purchasebasicinfo_set.all()) > 0 else "",
#
#                         'items': [{'description': item.itemDesc, 'stage': item.currentStage,
#                                    'approved': item.isApproved, 'declined': item.isDeclined, 'po_num': item.poNumber
#                                    } for item in form.purchaseitemdetail_set.all()],
#
#                     })
#                 return JsonResponse({'submitted': submitted})
#         except:
#             print('\n'.join(traceback.format_exception(*sys.exc_info())))
#             return HttpResponseServerError('Server Error. Please Contact IT Support')
#     else:
#         return redirect('login')


def UoM(request):
    global unitofmeasurement
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                unitofmeasurement = []

            for units in UnitOfMeasurement.objects.filter():
                unitofmeasurement.append({
                    'the_unit': units.uom,
                    'the_desc': units.uomDesc,
                })
            return JsonResponse({'unitofmeasurement': unitofmeasurement})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact IT Support')
    else:
        return redirect('login')


def my_purchase_api(request):
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                submitted = []

                for form in PurchaseRequestForm.objects.filter(employee=request.session['user_id']):
                    submitted.append({
                        'formID': form.formID,
                        'pr_Number': form.prNumber,
                        'creationDate': form.creationDate,
                        'form_total': form.prAmount,
                        'purpose': form.purchasebasicinfo_set.all()[0].purpose if len(
                            form.purchasebasicinfo_set.all()) > 0 else "",
                        'vendor_name': form.supplierinfo_set.get(form=form.formID).vendor.vendorName
                        if form.supplierinfo_set.filter(form=form.formID).exists() and form.supplierinfo_set.get(
                            form=form.formID).vendor is not None else "",
                        'items': [{
                            'description': item.itemDesc,
                            'stage': item.currentStage,
                            'detail_ID': item.detailID,
                            'approved': item.isApproved,
                            'declined': item.isDeclined,
                            'po_num': item.poNumber,
                            'approval_process': [{
                                'approver_name': approver.approverID.full_name,
                            } for approver in item.prapprovalprocess_set.filter(formID=item)]
                        } for item in form.purchaseitemdetail_set.filter(form=form.formID)
                        ],
                    })
                return JsonResponse({'submitted': submitted})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact IT Support')
    else:
        return redirect('login')


def purchase_to_approve_api(request):
    if request.user.is_authenticated:
        try:
            submitted = []
            # items = []
            if request.method == "GET":
                forms = []
                users_stages = PRApprovalProcess.objects.filter(approverID=request.session['user_id'])
                for stage in users_stages:
                    item = stage.formID
                    form = stage.formID.form
                    forms.append(form)
                    if item.currentStage >= stage.stage:
                        submitted.append({
                            'formID': form.formID,
                            'pr_Number': form.prNumber,
                            'form_total': form.prAmount,
                            'creationDate': form.creationDate,
                            'purpose': form.purchasebasicinfo_set.all()[0].purpose if len(
                                form.purchasebasicinfo_set.all()) > 0 else "",
                            'project': form.purchasebasicinfo_set.all()[0].project if len(
                                form.purchasebasicinfo_set.all()) > 0 else "",
                            'vendor_name': form.supplierinfo_set.get(
                                form=form.formID).vendor.vendorName if form.supplierinfo_set.get(
                                form=form.formID).vendor is not None else "",
                            'items_detail': [{'description': item.itemDesc,
                                              'stage': item.currentStage,
                                              'detail_ID': item.detailID,
                                              'approved': item.isApproved,
                                              'declined': item.isDeclined,
                                              'po_num': item.poNumber,
                                              'approval_process': [{
                                                  'approver_name': approver.approverID.full_name,
                                              } for approver in item.prapprovalprocess_set.filter(formID=item)]
                                              } for item in form.purchaseitemdetail_set.all()],
                            'action_required': "Action Required" if item.currentStage == stage.stage and stage.actionTaken in ["", None] else stage.actionTaken
                        })
                # submitted = items

            return JsonResponse({'submitted': submitted})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact IT Support')
    else:
        return redirect('login')


def PurchaseRequest(request, pk):
    if request.user.is_authenticated:

        error_messages = {'fatal_errors': '', 'other_errors': []}
        # Either returns the dictionary used for template language, or a string which is an error message
        if request.method == "POST":
            if request.POST.get('form_pk') != None and request.POST.get('form_pk') != 'undefined':
                pk = request.POST.get('form_pk')

        context = PurchaseRequestForm.get_context(request, pk)
        # print("CONTEXT: " + str(context))

        try:
            print(str(context['purchase_request_form']))
        except:
            return HttpResponse(context)

        # Check if the user can view the form:

        key = "view_pr_" + pk
        if pk != "new" and not UserPermissions.objects.filter(user=request.session['user_id'],
                                                              permission__key=key).exists() and context['user_can_view_form'] == False:
            return HttpResponseForbidden("You are not allowed to view this purchase form. Go back to the <a href= '../'>dashboard</a>")

        # if context['user_can_view_form'] == False:
        #     return HttpResponse(
        #         "Sorry. You cannot view this form. <br> Go back to the <a href='{% url \'smart_office_dashboard\' %}'>dashboard</a>")

        # Post the data
        if request.method == "POST":
            print('In the post')
            all_post_data = dict(request.POST)
            response_data = {}
            response_data['dir_to_dash'] = settings.BASE_URL + "/purchase_request"
            response_data['result'] = ''
            # The below one is only used when accountant updates a row:
            response_data['updated_row_pk'] = ''

            save_button_names = ['Finish', 'Save']
            submit_button_value = request.POST.get('submit_button')

            if submit_button_value == 'Generate Asset':
                error_messages[
                    'fatal_errors'] = "Sorry. This function is currently unavailable. Please try again later."
                response_data['result'] = error_messages
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            # region ADD COSIGNER
            if submit_button_value == 'Add Cosigner':
                current_approver = Employee.objects.get(associateID=request.session['user_id'])
                current_process = []
                current_stage = None
                checkbox_values = all_post_data['item_checkbox_value']
                all_items = context['purchase_item_details']
                context['cosigner_name'] = all_post_data['cosigner_name'][0]
                cosigner = Employee.objects.get(associateID=context['cosigner_name'])

                # FIND ITEMS IN THE CURRENT APPROVER'S PROCESS
                idx = 0
                for item in all_items:
                    process = PRApprovalProcess.objects.filter(formID=item, approverID=current_approver, stage=item.currentStage).first()
                    # CHECK IF ITEM COMES BACK AND GIVE A STAGE NUMBER
                    if process != None:
                        if current_stage == None:
                            current_stage = process.formID.currentStage
                        current_process.append(process)

                # ADD COSIGNER
                for process in current_process:
                    # ONLY ADD COSIGNER TO SELECTED ITEMS
                    if checkbox_values[idx] == 'on':
                        idx += 1
                        PRApprovalProcess.add_cosigner(process.formID, cosigner, current_stage)
                        continue
                    idx += 1
                # NOTIFY THE COSIGNER
                notify_approver(employee=cosigner, message_type='next_approver',
                                form=PurchaseRequestForm.objects.get(formID=pk), request=request)
            # endregion ADD COSIGNER


            if submit_button_value in save_button_names:
                if context['purchase_request_form'].isCompleted == False or context['details_to_edit'] != None:
                    if 'new_pk' in error_messages:
                        form_pk = error_messages['new_pk']
                        response_data['new_pk'] = form_pk
                        print("form pk: " + str(form_pk))
                        pk = form_pk
                        # Update context for submission:
                        context = PurchaseRequestForm.get_context(request, form_pk)
                        # print(context)
                    if error_messages['fatal_errors'] != '':
                        error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                    error_messages = merge_dictionaries(error_messages,
                                                        PurchaseRequestForm.update_purchase_request_information(
                                                            request=request, context=context))

                    try:
                        print(str(context['purchase_request_form']))
                    except:
                        error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                        response_data['result'] = str(context)
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

            # region Submit buttons
            print('Before submit button')
            if request.POST.get('submit_button') == 'Finish' and response_data['result'] == "":
                # If original requester is submitting:
                print('In the Finish submit')
                if context['details_to_edit'] == None:
                    error_messages = merge_dictionaries(error_messages,
                                                        context['purchase_request_form'].invite_buyers(request=request,
                                                                                                       context=context))
                # If buyer is submitting:
                else:
                    error_messages = merge_dictionaries(error_messages,
                                                        context['purchase_request_form'].buyer_update_cost(request,
                                                                                                           all_post_data,
                                                                                                           context))
                if error_messages['fatal_errors'] != '':
                    error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                messages.success(request=request, message="Purchase Request Successfully Submitted!")

            elif request.POST.get('submit_button') == 'Upload Chosen File' and response_data['result'] == "":
                error_messages = merge_dictionaries(error_messages, context['files_link'].upload_files(request=request,
                                                                                                       context=context))
                if "file_info" in error_messages:
                    file_info = error_messages['file_info']
                else:
                    error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                response_data.update(file_info)
                error_messages = merge_dictionaries(error_messages, response_data)
                if error_messages['fatal_errors'] != '':
                    error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )


            elif "Generate PO Document" == request.POST.get('submit_button'):
                response_data['file_link'] = context['purchase_request_form'].generate_po_doc_and_send_to_buyer()


            elif "Approve Selected Items" in request.POST.get('submit_button') or "Decline Selected Items" in request.POST.get('submit_button') and response_data[
                'result'] == "":
                error_messages = {'fatal_errors': '', 'other_errors': []}
                error_messages = merge_dictionaries(error_messages, context['files_link'].upload_files(request=request,
                                                                                                       context=context))
                error_messages = merge_dictionaries(error_messages,
                                                    context['purchase_request_form'].approve_or_decline_selected_items(
                                                        request=request, context=context))
                if error_messages['fatal_errors'] != '':
                    error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
            # region Accounting Actions
            elif 'Accounting Save' == request.POST.get('submit_button') and response_data['result'] == "":
                for item_to_update in context['rows_to_approve']:
                    # Update item's data and assets associated with it
                    if request.session['department'] == 'Supporting - Accounting':
                        error_messages = merge_dictionaries(error_messages,
                                                            item_to_update.accountant_update_purchase_item(request,
                                                                                                           context))
                        if error_messages['fatal_errors'] != "":
                            error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                response_data['result'] = error_messages
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            elif 'Accounting Approve' == request.POST.get('submit_button') and response_data['result'] == "":
                # Do accountant update purchase item for each item
                if request.session['department'] == 'Supporting - Accounting':
                    for item_to_update in context['rows_to_approve']:
                        error_messages = merge_dictionaries(error_messages,
                                                            item_to_update.accountant_update_purchase_item(request,
                                                                                                           context))
                        if error_messages['fatal_errors'] != "":
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                error_messages = merge_dictionaries(error_messages,
                                                    PurchaseRequestForm.accountant_approve_PR_items(request=request,
                                                                                                    context=context))

                if error_messages['fatal_errors'] != '':
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                if error_messages['fatal_errors'] != '':
                    error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                # Then do SAP stuff
            # endregion Accounting Actions
            # endregion

            error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
            response_data['result'] = error_messages
            print(f"Other Errors: {str(error_messages)}")
            for error in error_messages['other_errors']:
                messages.error(request, error)
            print(f"Response Data: {response_data}")
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )

        context['show_chat'] = False

        if pk != 'new':
            context['show_chat'] = True
            context['form_id'] = pk
            context['form_type'] = 'PR'

            # Get PO numbers and comments of all items in the form
            context['poNumber'] = ""
            counter = 1
            for item in PurchaseItemDetail.objects.filter(form=pk):
                if item.poNumber != None:
                    if counter == 1:
                        context['poNumber'] += str(item.poNumber)
                    else:
                        context['poNumber'] += ", " + str(item.poNumber)

                    counter += 1

            context['is_buyer'] = is_user_buyer(request)

        # Render the page
        return render(request, 'purchase/index.html', context)
    else:
        return redirect('../../accounts/login/?next=/purchase_request/' + pk + '/')


def print_pr(request):
    try:
        temp_data_dict = dict(request.GET)
        data_dict = dict()
        pprint(temp_data_dict)

        for item in temp_data_dict:
            if len(temp_data_dict[item]) > 1:
                for pos in range(len(temp_data_dict[item])):
                    key = str(item) + '_' + str(pos)
                    data_dict[key] = temp_data_dict[item][pos]
            else:
                data_dict[item] = temp_data_dict[item][0]

        pdf_file = generate_pr_print(data_dict)

        if os.path.exists(pdf_file):
            with open(pdf_file, 'rb') as f:
                file = f.read()
            response = HttpResponse(file, content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=PR-' + os.path.basename(pdf_file)
        else:
            raise FileNotFoundError

        response.set_cookie("file_received", "true")
        return response

    except:
        messages.error(request, "Error submitting form. Please contact the I.T Department.")
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        return HttpResponseServerError('Error generating PDF file for download')


def generate_pr_print(data_dict):
    try:
        # Read PDF Template
        template_pdf = pdfrw.PdfReader(os.path.join(settings.STATIC_ROOT, 'purchase/pr_printform.pdf'))
        template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))

        annotations = template_pdf.pages[0]['/Annots']

        # Write on field using data dictionary
        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget':
                if annotation['/T']:
                    key = annotation['/T'][1:-1]
                    if key in data_dict.keys():
                        annotation.update(pdfrw.PdfDict(V=data_dict[key]))

        # Write PDF File
        pdf_file = 'media/purchase/' + str(data_dict['requestor']).replace(" ", "-") + '-PR request.pdf'
        pdfrw.PdfWriter().write(pdf_file, template_pdf)

        return pdf_file

    except:
        raise Exception("Error generating PDF File")


def all_purchase_form(request):
    if request.user.is_authenticated:
        if not is_user_buyer(request):
            return HttpResponse("You are not allowed to view this page.")

        return render(request, 'purchase/all_purchase_form.html')
    else:
        return redirect('../../accounts/login/?next=/all_purchase')


def all_purchase_form_api(request):
    if request.user.is_authenticated:

        if not is_user_buyer(request):
            return HttpResponse("You are not allowed to view this page.")

        try:
            if request.method == "GET":
                submitted = []

                for form in PurchaseRequestForm.objects.all():
                    submitted.append({
                        'formID': form.formID,
                        'requestor': form.employee.full_name,
                        'pr_Number': form.prNumber,
                        'creationDate': form.creationDate,
                        'form_total': form.prAmount,
                        'purpose': form.purchasebasicinfo_set.all()[0].purpose if len(
                            form.purchasebasicinfo_set.all()) > 0 else "",
                        'vendor_name': form.supplierinfo_set.get(form=form.formID).vendorName
                        if form.supplierinfo_set.filter(form=form.formID).exists() and form.supplierinfo_set.get(form=form.formID).vendor is not None else "",
                        'items': [{
                            'description': item.itemDesc,
                            'stage': item.currentStage,
                            'detail_ID': item.detailID,
                            'approved': item.isApproved,
                            'declined': item.isDeclined,
                            'po_num': item.poNumber,
                            'approval_process': [{
                                'approver_name': approver.approverID.full_name,
                            } for approver in item.prapprovalprocess_set.filter(formID=item)]
                        } for item in form.purchaseitemdetail_set.filter(form=form.formID)
                        ],
                    })
                return JsonResponse({'submitted': submitted})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact IT Support')
    else:
        return redirect('login')
