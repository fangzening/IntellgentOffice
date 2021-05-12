from django.core.mail import EmailMultiAlternatives
from django.db.models import F
from .models import *
from office_app.models import *
from travel.custom_functions import *
from django.db.models import Q


def send_daily_email_reminder():
    emails = []
    send_emails = False

    if send_emails:
        # TA Forms
        current_stages = TemporaryApprovalStage.objects.filter(actionTaken=None, formID__currentStage=F('stage'))
        for stage in current_stages:
            if stage.approverID.email not in emails:
                emails.append(stage.approverID.email)

        sender = settings.EMAIL_HOST_USER
        subject, from_email, to = 'Travel Application Reminder', sender, emails
        html_content = "Hello, <br><br>" \
                       "This is an important message from your friendly company robot. " \
                       "There is at least one travel application form that you need to approve. This is a friendly reminder to Log in to " \
                       "<a href='http://10.20.67.81/forms/travel_list'>Smart Office</a> and approve the form." \
                       "<br><br>Best Regards,<br><br>Robot Connie"
        msg = EmailMultiAlternatives(subject, convert_html_message_to_text(html_content), from_email, emails)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        # TR Forms
        current_stages = TRApprovalProcess.objects.filter(actionTaken=None, formID__currentStage=F('stage'))
        for stage in current_stages:
            if stage.approverID.email not in emails:
                emails.append(stage.approverID.email)

        sender = settings.EMAIL_HOST_USER
        subject, from_email, to = 'Travel Reimbursement Reminder', sender, emails
        html_content = "Hello, <br><br>" \
                       "This is an important message from your friendly company robot. " \
                       "There is at least one travel reimbursement form that you need to approve. This is a friendly reminder to Log in to " \
                       "<a href='http://10.20.67.81/forms/travel_list'>Smart Office</a> and approve the form." \
                       "<br><br>Best Regards,<br><br>Robot Connie"
        msg = EmailMultiAlternatives(subject, convert_html_message_to_text(html_content), from_email, emails)
        msg.attach_alternative(html_content, "text/html")
        msg.send()



def send_email_to_team():
    recievers = ['zening.fang@fii-uas.com', 'zawaar.ejaz@fii-usa.com']
    sender = settings.EMAIL_HOST_USER
    subject, from_email, to = 'Travel Application Reminder', sender, recievers
    text_content = 'This is an unimportant message from your friendly company robot.'
    html_content = "Hello, <br>" \
                   "<br>This is an unimportant message from your friendly company robot. " \
                   "Some one in the group is testing the email function. Prepare for mountains of emails from me." \
                   "<br><br>Best Regards,<br><br>Robot Connie"
    msg = EmailMultiAlternatives(subject, text_content, from_email, recievers)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
