import json

from django.http import HttpResponse
from django.shortcuts import render
from office_app.sessions import *
# Create your views here.
from goods_received.models import *
from office_app.approval_functions import *

# Create your views here.
from purchase.pr_custom_functions import remove_unneccesary_keys_from_error_message_dict
from SAP.SAPFunctions import downloadPO

'''
This view renders the home page and is the middle man between the python functions/database and the template/javascript
'''


def gr_home(request, formID):
    if request.user.is_authenticated:
        # region response variables for request.POST
        response_data = {}
        response_data['dir_to_dash'] = '../../'
        response_data['result'] = ''
        # endregion

        error_messages = GRForm.get_context(request, formID)

        # region Checking for Errors in context
        if "context" in error_messages:
            context = error_messages['context']
        else:
            if request.method != "POST":
                return HttpResponse(error_messages['fatal_errors'])
            else:
                response_data['result'] = error_messages
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        if request.method == "POST":
            submit_button_value = request.POST.get('submit_button')
            headText = request.POST['header_text']
            print("header text: " + str(headText))
            if 'Save' in submit_button_value or 'Finish' in submit_button_value:
                error_messages = merge_dictionaries(error_messages,
                                                    GRForm.update_whole_gr(request=request, context=context))

                if error_messages['fatal_errors'] != '':
                    error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                # Check if it contains slip. If it does, add it to response data
                if 'slip' in error_messages.keys():
                    response_data['slip'] = error_messages['slip']
                # Check if it contains attachment#. If it does, add it to response data
                for key in error_messages.keys():
                    if 'attachment' in key:
                        response_data[key] = error_messages[key]
                if error_messages['fatal_errors'] != '':
                    error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            if 'Finish' in submit_button_value or 'Decline' in submit_button_value:
                print('IN THE FINISH, LN 72')
                error_messages = merge_dictionaries(error_messages,
                                                    context['gr_form'].update_approval_process(request, context))
                # error_messages = merge_dictionaries(error_messages,
                #                                     context['gr_form'].save_gr(prForm=context['pr_form'],
                #                                                                memo=request.POST.get('memo'),
                #                                                                refNumber=request.POST.get('ref_num'),
                #                                                                headerText=request.POST.get('header_text')))
                # GRForm.save_gr(headerText=request.POST['header_text'], refNumber=request.POST['ref_num'])
                if 'Finish' in submit_button_value:
                    messages.success(request, "Goods Received Form Approved Successfully!")
                else:
                    messages.success(request, "Goods Received Form Declined Successfully!")

            error_messages = remove_unneccesary_keys_from_error_message_dict(error_messages)
            for error in error_messages['other_errors']:
                messages.error(request, error)
            response_data['result'] = error_messages
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )

        context['show_chat'] = True
        context['form_id'] = formID
        context['form_type'] = 'GR'

        # endregion
        return render(request, 'gr_form/index.html', context)
    else:
        return redirect('../../../accounts/login/?next=/goods_received/' + formID)


def gr_soon(request):
    if request.user.is_authenticated:
        return render(request, 'soon/index.html', {})
    else:
        return redirect('../../accounts/login/?next=/goods_received/coming_soon')


def gr_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'gr_form/dashboard.html', {})
    else:
        return redirect('../../accounts/login/?next=/goods_received/')


def view_gr(request):
    if request.user.is_authenticated:
        return render(request, 'gr_form/view_my_gr.html', {})
    else:
        return redirect('../../accounts/login/?next=/goods_received/')


def approve_gr(request):
    if request.user.is_authenticated:
        return render(request, 'gr_form/approve_gr.html', {})
    else:
        return redirect('../../accounts/login/?next=/goods_received/')


def create_gr(request):
    if request.user.is_authenticated:
        plant_code_query = LegalEntity.objects.all().values_list('plantcodecombination', flat=True)
        plant_codes = ['FII8']

        for code in plant_code_query:
            if code not in plant_codes:
                plant_codes.append(code)

        print(f"Plant Codes: {plant_codes}")

        if request.method == "POST":
            print("inside POST")
            print(f"all post data: " + str(request.POST))
            response_data = {}
            response_data['result'] = 'not found'
            response_data['dir_to_form'] = ''

            po_num = request.POST.get('po_number')
            plant_code = request.POST.get('plant_code')

            print(f"PO num: {po_num} \nPlant code: {plant_code}")

            error_messages = merge_dictionaries({'fatal_errors': '', 'other_errors': []}, GRForm.generate_gr(request, plant_code, po_num))

            if 'dir_to_form' in error_messages.keys():
                response_data['dir_to_form'] = error_messages['dir_to_form']
                response_data['result'] = error_messages['result']

            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )

        return render(request, 'gr_form/create_gr.html', {'plant_codes': plant_codes})
    else:
        return redirect('../../accounts/login/?next=/goods_received/create_gr')
