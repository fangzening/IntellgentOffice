import json
from django.http import HttpResponse
from django.shortcuts import render

from mro_invoice.models import InvoiceForm
from office_app.sessions import *
from office_app.approval_functions import *
from goods_received.models import GRForm, GRList
from SAP.SAPFunctions import downloadGR


# Create your views here.
# you can use url http://127.0.0.1:8000/mro_invoice/invoice/AFE2091701
def invoice_home(request, po_num):
    if request.user.is_authenticated:
        context = InvoiceForm.get_context(po_num, request)
        if 'fatal_errors' in context.keys():
            return HttpResponse(context['fatal_errors'])
        if context['current_user'] not in context['people_who_can_see_form']:
            return HttpResponse("You cannot see this right now")
        print(f"context: {context}")

        if request.method == "POST":
            response_data = {}
            response_data['dir_to_dash'] = "../../"
            error_messages = {'fatal_errors': '', 'other_errors': []}

            error_messages = merge_dictionaries(error_messages, InvoiceForm.handle_post_data(context, request))

            response_data['result'] = error_messages
            for error in error_messages['other_errors']:
                messages.error(request, error)
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        return render(request, 'invoice.html', context)
    else:
        return redirect('../../accounts/login/?next=/mro_invoice/invoice')




def search_inv(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            print("getting post data")
            response_data = {}
            response_data['dir_to_form'] = "/mro_invoice/invoice/" + request.POST.get('po_number')
            response_data['result'] = 'found'

            context = InvoiceForm.get_context(request.POST.get('po_number'), request)
    
            if 'fatal_errors' in context.keys():
                response_data['result'] = context['fatal_errors']

            elif context['current_user'] not in context['people_who_can_see_form']:
                response_data['result'] = "Invoice Form exists, but you are not allowed to view it."

            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        return render(request, 'search_invoice.html', {})
    else:
        return redirect('../../accounts/?next=/mro_invoice/invoice')
