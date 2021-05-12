from Smart_Office import settings
from django.contrib import messages
import sys
import traceback
from django.core.mail import EmailMultiAlternatives
from SAP.SAPFunctions import  check_invoice_SAP
from expense.models import Expense


def sendEmail(request,employee,expense_form_id):
    sender = settings.EMAIL_HOST_USER
    text_content = "Hello " + employee.full_name + ", \n\n" \
                                                         "This is an important message from your friendly company robot. " \
                                                         "There is a expense application that you need to approve. Go to " \
                   + settings.BASE_URL + "expense/" + expense_form_id\
                   + "/Approve> and approve the form." \
                                "\n\nBest Regards,\n\nRobot Connie"
    html_content = "Hello " + employee.full_name + ", <br>" \
                                                         "<br>This is an important message from your friendly company robot. " \
                                                         "There is an expense application that you need to approve. Go to " \
                                                         "<a href='" + settings.BASE_URL + "expense/"+ expense_form_id+ "/Approve'>Smart Office</a> and approve the form." \
                                "<br><br>Best Regards,<br><br>Robot Connie"
    msg = EmailMultiAlternatives("Expense Application Needs to be approved!", text_content, sender,
                                 [employee.email])
    msg.attach_alternative(html_content, "text/html")
    # print("we are sending email to "+employee.full_name+" by their email:"+employee.email)
    try:
        msg.send()
        messages.success(request, "Form has been submitted")
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        messages.error(request,
                       "Error sending email notifying approvers. Please contact IT Department")

# this is used to notify all approvers at current stage
def notifyAll(request,applist):
    for appsta in applist.approverstatus_set.all():
        if appsta.stage==applist.currentStage:
            print("we found the approver")
            sendEmail(request,appsta.approver.associateID,applist.expense.form_ID)

# check if the Invoice number is unique in databse
def check_invoice_django(invoice_id,companycode,vendorcode):
    #print(Expense.objects.filter(invoice_ID=invoice_id,company__sapCompCode=companycode,vendor__vendorCode=vendorcode))
    return False if Expense.objects.filter(invoice_ID=invoice_id,company__sapCompCode=companycode,vendor__vendorCode=vendorcode) else True

# check if the Invoice number is unique in both our database and SAP:
def check_invoice(invoice_id,companycode,vendorcode):
    return check_invoice_django(invoice_id,companycode,vendorcode) and check_invoice_SAP(invoice_id,companycode)