import enum
import os
import sys
import traceback
import socket
import logging
from datetime import datetime

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.db import connection
from Smart_Office import settings
from goods_received.models import GRForm, GRApproversProcess
from mro_invoice.models import InvoiceForm, InvoiceApproversProcess
from purchase.models import PurchaseRequestForm, PRApprovalProcess
from travel.models import EmployeeInformation, TADetails, TemporaryApprovalStage, TRApprovalProcess



class LogType(enum.Enum):
    ERR = 'Error'
    WARN = 'Warning'
    INFO = 'Info'
    DEBUG = 'Debug'
    CRIT = 'Critical'


class FormTypes(enum.Enum):
    TravelApplication = 'TA'
    TravelReimbursement = 'TR'
    PurchaseRequest = 'PR'
    GoodsReceived = 'GR'
    Invoice = 'AP'

'''
    Created by: Jacob Lattergrass
    ====== About EmailHandler ======
    The EmailHandler class is one I created to do just that: handle the sending of emails.
    The BOT_NAME property is the name displayed at the bottom of emails sent out by our site.
    Any functions that relate to sending email should be put in here unless they are
    required to be a part of the module that uses them.
'''


class EmailHandler:
    BOT_NAME = 'FoxBot'
    TEST_URL = 'http://127.0.0.1:8000'
    URL = 'https://office.fii-corp.com'
    DB_HOST = connection.settings_dict['HOST']
    DB_NAME = connection.settings_dict['NAME']

    site_admin_list = ['jacob.lattergrass@fii-usa.com','zaawar.ejaz@fii-usa.com', 'corrina.barr@fii-usa.com',
                       'josua.ataansuyi@fii-usa.com']

    form_link_list = {
        'TA': 'travel_application',
        'TR': 'travel_reimbursement',
        'PR': 'purchase_request',
        'GR': 'goods_received',
        'AP': 'mro_invoice'
    }

    form_true_name = {
        'TA': 'Travel Application',
        'TR': 'Travel Reimbursement',
        'PR': 'Purchase Request',
        'GR': 'Goods Received',
        'AP': 'Invoice'
    }

    class StopEmails(Exception):
        pass

    @staticmethod
    def __send_email(msg=None, override_test=False):
        if msg is None:
            raise ValueError("You need to provide an EmailMultiAlternatives object.")
        if type(msg) is not EmailMultiAlternatives:
            raise ValueError("You need to provide an EmailMultiAlternatives object.")
        # Check if DB is a test db
        # Also check if test case is being overwritten

        running_test_server = ConnectionHandler.server_check()
        msg.send()
        # if EmailHandler.DB_NAME in ['smart_test', 'smart_office'] and EmailHandler.DB_HOST in ['10.20.193.61'] and not override_test:
        #     msg.to = ['jacob.lattergrass@fii-usa.com']
        #     msg.send()
        #     raise EmailHandler.StopEmails
        # else:
        #     msg.to = EmailHandler.site_admin_list
        #     msg.send()

    '''
        send_notification_email
        This function sends an email to recipients based on the form and notification type.
        :param formType: a 2-3 character representation of a form
        :param formID: the id of the form in question
        :param requester: the user submitting the form or the user adding others to the process
        :param approvers: a list of Account objects that are to receive the email
        :param isUrgent: determines if the action required is an urgent one
    '''

    @staticmethod
    def send_notification_email(formType, formID, requester, approvers, isUrgent=False):
        other_errors = []
        # Get Form object
        form_type_list = {
            'TA': EmployeeInformation.objects.filter(formID=formID).first(),
            'TR': TADetails.objects.filter(taDetail=formID).first(),
            'PR': PurchaseRequestForm.objects.filter(formID=formID).first(),
            'GR': GRForm.objects.filter(formID=formID).first(),
            'AP': InvoiceForm.objects.filter(formID=formID).first()
        }

        if type(formType) is FormTypes:
            try:
                true_form_type = formType.value
                form = form_type_list[formType.value]
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to next approvers")
                return other_errors
        elif type(formType) is not FormTypes:
            try:
                true_form_type = EmailHandler.form_true_name[formType]
                form = form_type_list[formType]
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to next approvers")
                return other_errors

        # Send to localhost if DEBUG is True
        # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
        if type(formType) is FormTypes:
            link_value = formType.value
        elif type(formType) is not FormTypes:
            link_value = formType

        if settings.DEBUG is True:
            try:
                form_link = f'<a href="{EmailHandler.TEST_URL}/forms/{EmailHandler.form_link_list[link_value]}/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to next approvers")
                return other_errors
        else:
            try:
                form_link = f'<a href="{EmailHandler.URL}/{EmailHandler.form_link_list[link_value]}/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to next approvers")
                return other_errors
        subject_heading = f"Smart Office: Please review {true_form_type} Form: {formID}"

        if not isUrgent:
            # Travel App and Reimbursement have the same message.
            if true_form_type is 'Travel Application':
                for person in approvers:
                    try:
                        content = f"<p>Hello {person.fullname},<br><br>There is a {true_form_type} from " \
                                  f"<b>{requester.fullname}</b> that you need to review. Total amount is " \
                                  f"{form.estimatedExpense}. Go to {form_link} and approve the form. " \
                                  f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
                        msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [person.email])
                        msg.attach_alternative(form_link, "text/html")
                        msg.content_subtype = "html"
                        EmailHandler.__send_email(msg)
                        # msg.send()
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        other_errors.append('Error sending email to ' + str(person))
                        return other_errors
            elif true_form_type is 'Travel Reimbursement':
                for person in approvers:
                    try:
                        content = f"<p>Hello {person.fullname},<br><br>There is a {true_form_type} from " \
                                  f"<b>{requester.fullname}</b> that you need to review. " \
                                  f"Go to {form_link} and approve the form." \
                                  f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
                        msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [person.email])
                        msg.attach_alternative(form_link, "text/html")
                        msg.content_subtype = "html"
                        # msg.send()
                        EmailHandler.__send_email(msg)
                    except EmailHandler.StopEmails:
                        break
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        other_errors.append('Error sending email to ' + str(person))
                        return other_errors
            elif true_form_type is 'Purchase Request':
                print(f"form type: {form.prAmount}")
                for person in approvers:
                    try:
                        print("form: " + str(form))
                        content = f"<p>Hello {person.fullname},<br><br>There is a {true_form_type} form " \
                                  f"from <b>{requester.fullname}</b> that you need to review. Total amount is " \
                                  f"{form.prAmount}." \
                                  f"Go to {form_link} and approve the form." \
                                  f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
                        msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [person.email])
                        msg.attach_alternative(form_link, "text/html")
                        msg.content_subtype = "html"
                        EmailHandler.__send_email(msg)
                    except EmailHandler.StopEmails:
                        break
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        other_errors.append('Error sending email to ' + str(person))
                        return other_errors
            elif true_form_type is 'Invoice':
                for person in approvers:
                    try:
                        print("form: " + str(form))
                        content = f"<p>Hello {person.fullname},<br><br>There is an {true_form_type} form " \
                                  f"from <b>{requester.fullname}</b> that you need to review. " \
                                  f"Go to {form_link} and approve the form." \
                                  f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
                        msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [person.email])
                        msg.attach_alternative(form_link, "text/html")
                        msg.content_subtype = "html"
                        EmailHandler.__send_email(msg)
                    except EmailHandler.StopEmails:
                        break
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        other_errors.append('Error sending email to ' + str(person))
                        return other_errors
        elif isUrgent:
            for person in approvers:
                try:
                    content = f"<p style='color: red;'>Hello {person.fullname},<br><br>Kindly note that a {true_form_type} form " \
                              f"has been submitted and on {form.creationDate} and this form is urgent. Please see to it " \
                              f"as soon as possible.<br><br>Go to {form_link} and approve the form." \
                              f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
                    msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [person.email])
                    msg.attach_alternative(form_link, "text/html")
                    msg.content_subtype = "html"
                    EmailHandler.send_email(msg)
                except EmailHandler.StopEmails:
                    break
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    other_errors.append('Error sending email to ' + str(person))
                    return other_errors
        return other_errors

    '''
        send_declined_email
        This function sends an email to inform approvers and the requester that the form was declined.
        :param formType: a 2-3 character representation of a form
        :param formID: the id of the form in question
        :param requester: the user submitting the form or the user adding others to the process
        :param recipients: a list of Account objects that are to receive the email
        :param decliningUser: the user that declined the form
    '''

    @staticmethod
    def send_declined_email(formType, formID, requester, approvers, decliningUser, itemID=None):
        other_errors = []
        # Get Form object
        form_type_list = {
            'TA': EmployeeInformation.objects.filter(formID=formID).first(),
            'TR': TADetails.objects.filter(taDetail=formID).first(),
            'PR': PurchaseRequestForm.objects.filter(formID=formID).first(),
            'GR': GRForm.objects.filter(formID=formID).first(),
            'AP': InvoiceForm.objects.filter(formID=formID).first()
        }

        # Find Declining User
        form_declining_user = {
            'TA': TemporaryApprovalStage.objects.filter(formID=formID, approverID=decliningUser.associateID).first(),
            'TR': TRApprovalProcess.objects.filter(formID=formID, approverID=decliningUser.associateID).first(),
            'PR': PRApprovalProcess.objects.filter(formID=itemID, approverID=decliningUser.associateID).first(),
            'GR': GRApproversProcess.objects.filter(grForm__formID=formID, approver__associateID=decliningUser.associateID).first(),
            'AP': InvoiceApproversProcess.objects.filter(formID__formID=formID, approverID__associateID=decliningUser.associateID).first()
        }

        if type(formType) is FormTypes:
            try:
                true_form_type = formType.value
                decliningUserComment = form_declining_user[formType.value].comments
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to notifying people of form being declined")
                return other_errors
        elif type(formType) is not FormTypes:
            try:
                true_form_type = EmailHandler.form_true_name[formType]
                decliningUserComment = form_declining_user[formType].comments
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to notifying people of form being declined")
                return other_errors

        # form = form_type_list[formType.value]

        # Send to localhost if DEBUG is True
        # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
        if type(formType) is FormTypes:
            try:
                link_value = formType.value
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to notifying people of form being declined")
                return other_errors
        elif type(formType) is not FormTypes:
            try:
                link_value = formType
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to notifying people of form being declined")
                return other_errors

        if settings.DEBUG is True:
            try:
                form_link = f'<a href="{EmailHandler.TEST_URL}/{EmailHandler.form_link_list[link_value]}/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to notifying people of form being declined")
                return other_errors
        else:
            try:
                form_link = f'<a href="{EmailHandler.URL}/{EmailHandler.form_link_list[link_value]}/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to notifying people of form being declined")
                return other_errors
        try:
            subject_heading = f"Smart Office: {true_form_type} Form: {formID} has been declined"
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append("Error sending email to notifying people of form being declined")
            return other_errors

        if true_form_type is not 'Purchase Request' and true_form_type is not 'Goods Received':
            try:
                content = f"<p>Hello {requester.fullname}," \
                          f"<br><br>{true_form_type} form has been declined by <b>{decliningUser.fullname}</b>." \
                          f"<br><br>The Comment is left reads <b>'{decliningUserComment}.'</b>" \
                          f"<br><br>Go to {form_link} to see detailed information. " \
                          f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
                msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, to=[requester.email],
                                             cc=approvers)
                msg.attach_alternative(form_link, "text/html")
                msg.content_subtype = "html"
                # msg.send()
                EmailHandler.__send_email(msg)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to form's creator. Please contact IT")
                return other_errors
        elif true_form_type is 'Purchase Request':
            try:
                content = f"<p>Hello {requester.fullname}," \
                          f"<br><br>An item on {true_form_type} form has been declined by <b>{decliningUser.fullname}</b>." \
                          f"<br><br>The Comment is left reads <b>'{decliningUserComment}.'</b>" \
                          f"<br><br>Go to {form_link} to see detailed information. " \
                          f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
                msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, to=[requester.email],
                                             cc=approvers)
                msg.attach_alternative(form_link, "text/html")
                msg.content_subtype = "html"
                EmailHandler.__send_email(msg)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(requester.fullname) + " notifying them that the form was declined")
                return other_errors
        elif true_form_type is 'Goods Received':
            try:
                content = f"<p>Hello {requester.fullname}," \
                          f"<br><br>An item on {true_form_type} form has been declined by <b>{decliningUser.fullname}</b>." \
                          f"<br><br>The Comment is left reads <b>'Hello Jacob.'</b>" \
                          f"<br><br>Go to {form_link} to see detailed information. " \
                          f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
                msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, to=[requester.email],
                                             cc=approvers)
                # f"<br><br>The Comment is left reads <b>'{decliningUserComment}.'</b>" \
                msg.attach_alternative(form_link, "text/html")
                msg.content_subtype = "html"
                EmailHandler.__send_email(msg)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(requester.fullname) + " notifying them that the form was declined")
                return other_errors

    '''
        send_modification_email
        This function sends an email to inform the requester that his/her form was modified.
        :param formType: a 2-3 character representation of a form
        :param formID: the id of the form in question
        :param requester: the user submitting the form or the user adding others to the process
        :param modifyingUser: the user that modified the form
    '''

    @staticmethod
    def send_modification_email(formType, formID, requester, modifyingUser):
        other_errors = []
        # Get Form object
        form_type_list = {
            'TA': EmployeeInformation.objects.filter(formID=formID).first(),
            'TR': TADetails.objects.filter(taDetail=formID).first(),
            'GR': GRForm.objects.filter(taDetail=formID).first(),
        }

        if type(formType) is FormTypes:
            try:
                true_form_type = formType.value
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(requester.fullname) + " notifying them of modification request")
                return other_errors
        elif type(formType) is not FormTypes:
            try:
                true_form_type = EmailHandler.form_true_name[formType]
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(requester.fullname) + " notifying them of modification request")
                return other_errors

        # Find Modifying User
        form_modifying_user = {
            'TA': TemporaryApprovalStage.objects.filter(formID=formID, approverID=modifyingUser.associateID).first(),
            'TR': TRApprovalProcess.objects.filter(formID=formID, approverID=modifyingUser.associateID).first(),
            'GR': GRApproversProcess.objects.filter(grForm=form_type_list['GR'], approverID=modifyingUser.associateID).first(),
        }

        # form = form_type_list[formType.value]
        # Send to localhost if DEBUG is True
        # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
        if type(formType) is FormTypes:
            try:
                link_value = formType.value
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(requester.fullname) + " notifying them of modification request")
                return other_errors
        elif type(formType) is not FormTypes:
            try:
                link_value = formType
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(requester.fullname) + " notifying them of modification request")
                return other_errors

        if settings.DEBUG is True:
            try:
                form_link = f'<a href="{EmailHandler.TEST_URL}/{EmailHandler.form_link_list[link_value]}/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(requester.fullname) + " notifying them of modification request")
                return other_errors
        else:
            try:
                form_link = f'<a href="{EmailHandler.URL}/{EmailHandler.form_link_list[link_value]}/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append(
                    "Error sending email to " + str(requester.fullname) + " notifying them of modification request")
                return other_errors

        try:
            subject_heading = f"Smart Office: {EmailHandler.form_true_name[formType.value]} Form: {formID} has been modified"

            content = f"<p>Hello {requester.fullname},<br><br>{modifyingUser.fullname} " \
                      f"has modified your {true_form_type} form." \
                      f"<br><br>Go to {form_link} and approve the modification." \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [requester.email])
            msg.attach_alternative(form_link, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending email to " + str(requester.fullname) + " notifying them of modification request")
            return other_errors
        return other_errors

    '''
        send_cosigner_email
        This function sends an email to inform the requester that his/her form was modified.
        :param formType: a 2-3 character representation of a form
        :param formID: the id of the form in question
        :param requester: the user who added the cosigner
        :param newCosigner: the user that has been added and will be emailed
    '''

    @staticmethod
    def send_cosigner_email(formType, formID, requester, newCosigner):
        other_errors = []
        # Get Form object
        form_type_list = {
            'TA': EmployeeInformation.objects.filter(formID=formID).first(),
            'TR': TADetails.objects.filter(taDetail=formID).first(),
            'PR': PurchaseRequestForm.objects.filter(formID=formID).first(),
        }

        form = form_type_list[formType.value]

        if type(formType) is FormTypes:
            try:
                true_form_type = formType.value
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(newCosigner.fullname) + " notifying them of modification request")
                return other_errors
        elif type(formType) is not FormTypes:
            try:
                true_form_type = EmailHandler.form_true_name[formType]
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append(
                    "Error sending email to " + str(newCosigner.fullname) + " notifying them of modification request")
                return other_errors

        # Send to localhost if DEBUG is True
        # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
        if type(formType) is FormTypes:
            try:
                link_value = formType.value
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(newCosigner.fullname) + " notifying them of modification request")
                return other_errors
        elif type(formType) is not FormTypes:
            try:
                link_value = formType
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(newCosigner.fullname) + " notifying them of modification request")
                return other_errors

        if settings.DEBUG is True:
            try:
                form_link = f'<a href="{EmailHandler.TEST_URL}/{EmailHandler.form_link_list[link_value]}/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(newCosigner.fullname) + " notifying them of modification request")
                return other_errors
        else:
            try:
                form_link = f'<a href="{EmailHandler.URL}/{EmailHandler.form_link_list[link_value]}/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append("Error sending email to " + str(newCosigner.fullname) + " notifying them of modification request")
                return other_errors

        try:
            subject_heading = f"Smart Office: Please review {true_form_type} Form: {formID}"

            content = f"<p>Hello {newCosigner.fullname},<br><br>{requester.fullname} " \
                      f"has added you as a co-signer for {true_form_type} form {formID}." \
                      f"<br><br>Go to {form_link} and approve the modification." \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [newCosigner.email])
            msg.attach_alternative(form_link, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending email to " + str(newCosigner.fullname) + " notifying them of modification request")
            return other_errors
        return other_errors

    '''
        send_tr_reminder_email
        This function sends an email reminder at the end date of a person's travel.
        :param formID: the id of the form in question
        :param originalRequester: the user who applied for the travel form
    '''

    @staticmethod
    def send_tr_reminder_email(formID, originalRequester):
        other_errors = []
        # Send to localhost if DEBUG is True
        # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
        if settings.DEBUG is True:
            try:
                form_link = f'<a href="{EmailHandler.TEST_URL}/travel_application/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append(
                    "Error sending email to " + str(originalRequester.fullname) + " notifying them of of tr policy")
                return other_errors
        else:
            try:
                form_link = f'<a href="{EmailHandler.URL}/travel_application/{formID}">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append(
                    "Error sending email to " + str(originalRequester.fullname) + " notifying them of of tr policy")
                return other_errors

        try:
            subject_heading = f"Smart Office: Please submit TR Form for Form: {formID} in 30 days"
            content = f"<p>Hello {originalRequester.fullname},<br><br>" \
                      f"Kindly note that within 30 days after you return to home office, " \
                      f"you must submit your <b>Travel Reimbursement</b> form to substantiate " \
                      f"all travel expenses." \
                      f"<br><br>Go to {form_link} and submit the form with actual original receipts. " \
                      f"To apply for reimbursement, click the Apply for Reimbursement button located " \
                      f"at the top-right of your original Travel Application." \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [originalRequester.email])
            msg.attach_alternative(form_link, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending email to " + str(originalRequester.fullname) + " notifying them of of tr policy")
        return other_errors

    '''
        send_password_change_email
        This function sends an email to users who are approved for password changes.
        :param originalRequester: the user who applied for the travel form
    '''

    @staticmethod
    def send_password_change_email(approvedUser):
        other_errors = []
        # Send to localhost if DEBUG is True
        # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
        if settings.DEBUG is True:
            try:
                form_link = f'<a href="{EmailHandler.TEST_URL}/user/change_password">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append(
                    "Error sending email to " + str(approvedUser.fullname) + " notifying them that they can change their password")
                return other_errors
        else:
            try:
                form_link = f'<a href="{EmailHandler.URL}/user/change_password">Smart Office</a>'
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append(
                    "Error sending email to " + str(approvedUser.fullname) + " notifying them that they can change their password")
                return other_errors
        try:
            subject_heading = f"Smart Office: You've been approved to change your password"

            content = f"<p>Hello {approvedUser.fullname},<br><br>" \
                      f"You have been approved to change your account password. You have 24 hours to go to {form_link} " \
                      f"and change your password. " \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [approvedUser.email])
            msg.attach_alternative(form_link, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending email to " + str(
                    approvedUser.fullname) + " notifying them that they can change their password")
        return other_errors

    '''
        send_form_submitted_email
        This function sends an email to the user that submits the form.
        :param formType: a 2-3 character representation of a form
        :param formID: the id of the form in question
        :param originalRequester: the user who applied for the travel form
    '''

    @staticmethod
    def send_form_submitted_email(formType, formID, originalRequester):
        other_errors = []
        if type(formType) is FormTypes:
            try:
                true_form_type = formType.value
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append(
                    "Error sending email to " + str(originalRequester.fullname) + " notifying them that thier form has been submitted")
                return other_errors
        elif type(formType) is not FormTypes:
            try:
                true_form_type = EmailHandler.form_true_name[formType]
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                other_errors.append(
                    "Error sending email to " + str(originalRequester.fullname) + " notifying them that thier form has been submitted")
                return other_errors

        try:
            subject_heading = f"Smart Office: You have submitted a {true_form_type} Form: {formID}"
            # Send to localhost if DEBUG is True
            # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
            if type(formType) is FormTypes:
                link_value = formType.value
            elif type(formType) is not FormTypes:
                link_value = formType
            if settings.DEBUG is True:
                form_link = f'<a href="{EmailHandler.TEST_URL}/{EmailHandler.form_link_list[link_value]}/{formID}">click here</a>'
            else:
                form_link = f'<a href="{EmailHandler.URL}/{EmailHandler.form_link_list[link_value]}/{formID}">click here</a>'
            content = f"<p>Hello {originalRequester.fullname},<br><br>" \
                      f"Your form has been successfully submitted! You can go back and view it on the " \
                      f"{true_form_type} index page. If you have any questions " \
                      f"regarding your form, contact your manager." \
                      f"<br><br>You can also {form_link} to be taken directly to your form." \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [originalRequester.email])
            msg.attach_alternative(form_link, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending email to " + str(originalRequester.fullname) + " notifying them that thier form has been submitted")

        return other_errors

    '''
        send_form_approved_email
        This function sends an email to the user that submits the form.
        :param formType: a 2-3 character representation of a form
        :param formID: the id of the form in question
        :param originalRequester: the user who applied for the travel form
    '''

    @staticmethod
    def send_form_approved_email(formType, formID, originalRequester):
        other_errors = []
        try:
            # Send to localhost if DEBUG is True
            # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
            if type(formType) is FormTypes:
                link_value = formType.value
            elif type(formType) is not FormTypes:
                link_value = formType

            if settings.DEBUG is True:
                form_link = f'<a href="{EmailHandler.TEST_URL}/{EmailHandler.form_link_list[link_value]}/{formID}">click here</a>'
            else:
                form_link = f'<a href="{EmailHandler.URL}/{EmailHandler.form_link_list[link_value]}/{formID}">click here</a>'

            if type(formType) is FormTypes:
                true_form_type = formType.value
            elif type(formType) is not FormTypes:
                true_form_type = EmailHandler.form_true_name[formType]

            subject_heading = f"Smart Office: {true_form_type} Form: {formID} has been fully approved"

            content = f"<p>Hello {originalRequester.fullname},<br><br>" \
                      f"Your form has been reviewed and approved! You may still go back and view it on the " \
                      f"{true_form_type} index page. If you have any questions " \
                      f"regarding your form, contact your manager." \
                      f"<br><br>You can also {form_link} to be taken directly to your form." \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [originalRequester.email])
            msg.attach_alternative(form_link, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append("Error sending email to " + str(originalRequester.fullname) + " notifying them that thier form has been completely approved")
            return other_errors

    '''
        send_gl_email
        This function sends an email to GS for ticket booking.
        :param formType: a 2-3 character representation of a form
        :param formID: the id of the form in question
        :param originalRequester: the user who applied for the travel form
    '''

    @staticmethod
    def send_gs_email(formType, formID, recipient):
        other_errors = []
        try:
            # Send to localhost if DEBUG is True
            # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
            if settings.DEBUG is True:
                form_link = f'<a href="{EmailHandler.TEST_URL}/travel_application/{formID}">click here</a>'
            else:
                form_link = f'<a href="{EmailHandler.URL}/travel_application/{formID}">click here</a>'

            if type(formType) is FormTypes:
                true_form_type = formType.value
            elif type(formType) is not FormTypes:
                true_form_type = EmailHandler.form_true_name[formType]

            subject_heading = f"Smart Office: A {true_form_type} Form has been fully approved: {formID}"

            content = f"<p>Hello {recipient.fullname},<br><br>" \
                      f"A {true_form_type} form has been submitted. Please {form_link} to view " \
                      f"the information you need for booking tickets. " \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [recipient.email])
            msg.attach_alternative(form_link, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending email to " + str(recipient.fullname) + " notifying them that they need to book tickets for the form.")
        return other_errors

    '''
        send_po_email
        This function notifies a user that a PO number needs to be generated.
        :param formType: a 2-3 character representation of a form
        :param formID: the id of the form in question
        :param originalRequester: the user who applied for the travel form
    '''

    @staticmethod
    def send_po_email(formType, formID, recipient):
        other_errors = []
        try:
            # Send to localhost if DEBUG is True
            # Else direct to .67 server for now # TODO: Find out if I can see which server is running and use that url
            if settings.DEBUG is True:
                form_link = f'<a href="{EmailHandler.TEST_URL}/{formID}">click here</a>'
            else:
                form_link = f'<a href="{EmailHandler.URL}/{formID}">click here</a>'

            if type(formType) is EmailHandler.FormTypes:
                true_form_type = formType.value
            elif type(formType) is not EmailHandler.FormTypes:
                true_form_type = EmailHandler.form_true_name[formType]

            subject_heading = f"Smart Office: A {true_form_type} Form has been fully approved: {formID}"

            content = f"<p>Hello {recipient.fullname},<br><br>" \
                      f"A {true_form_type} form needs a PO number. Please go to {form_link} to view " \
                      f"and generate a number for the form. " \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, [recipient.email])
            msg.attach_alternative(form_link, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending email to " + str(
                    recipient.fullname) + " notifying them that they need to book tickets for the form.")
        return other_errors

    @staticmethod
    def send_contact_email(requester, subject, msg=None, isPwdReq=False):
        other_errors = []
        if isPwdReq:
            msg = "I want to change my password."
        try:
            subject_heading = f"Smart Office: A user has sent a contact request"

            content = f"<p>Hello Admin,<br><br>" \
                      f"{requester.fullname} has submitted a contact request regarding {subject}. The message they left " \
                      f"reads:<br><br>\"{msg}\"<br><br>Please respond as soon as you are able." \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER, EmailHandler.site_admin_list)
            msg.attach_alternative(content, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending contact email to " + str(
                    requester.fullname) + ".")
            return other_errors


    @staticmethod
    def send_emergency_email(msg):
        other_errors = []
        try:
            subject_heading = f"Smart Office: A user has sent a contact request"

            content = f"<p>Hello Admin,<br><br>" \
                      f"There has been a critical error on Smart Office! The error message reads:" \
                      f"<br><br><p style=\"color: red;\">\"{msg}\"" \
                      f"</p><br><br>Please look into this error as soon as possible." \
                      f"<br><br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER,
                                         EmailHandler.site_admin_list)
            msg.attach_alternative(content, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending contact email to " + str(EmailHandler.site_admin_list[0]) + ".")
            return other_errors

    @staticmethod
    def send_excel_attachment_email(recipient, file_path, file_name):
        other_errors = []
        try:
            import openpyxl
            from io import BytesIO

            file = openpyxl.open(file_path)
            out = BytesIO()
            file.save(out)

            subject_heading = f"Smart Office: Excel spreadsheet for GR Form"

            content = f"<p>Hello {recipient.fullname},<br><br>" \
                      f"You have finished fill out a GR form. Smart Office has created " \
                      f"a spreadsheet based on the information provided.</p>" \
                      f"<br>Best Regards, <br><br>{EmailHandler.BOT_NAME}</p>"
            msg = EmailMultiAlternatives(subject_heading, content, settings.EMAIL_HOST_USER,
                                         [recipient])
            msg.attach(file_name, out.getvalue(), 'application/vnd.ms-excel')
            msg.attach_alternative(content, "text/html")
            msg.content_subtype = "html"
            EmailHandler.__send_email(msg)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            other_errors.append(
                "Error sending contact email to " + str(EmailHandler.site_admin_list[0]) + ".")
            return other_errors


class ConnectionHandler:
    SERVER_NAME = socket.gethostbyname(socket.gethostname())
    PROD_SERVERS = settings.PROD_SERVER_LIST
    TEST_SERVERS = settings.TEST_SERVER_LIST
    SERVER_LIST = PROD_SERVERS + TEST_SERVERS

    '''
        server_check
        This function checks to see if the current server is in the server list. If it is, then it returns True.
        :returns: Boolean value
        
    '''
    @staticmethod
    def server_check():
        if ConnectionHandler.SERVER_NAME in ConnectionHandler.SERVER_LIST:
            return True
        else:
            return False

    @staticmethod
    def check_if_production():
        if ConnectionHandler.SERVER_NAME in ConnectionHandler.PROD_SERVERS:
            return True
        else:
            return False
