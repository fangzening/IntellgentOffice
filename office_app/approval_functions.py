'''
This file contains approval process functions usable for all forms in Smart-Office
'''
import sys
import traceback
from datetime import datetime

from django.contrib import messages
from django.core.mail import EmailMultiAlternatives

from SAP import SAPFunctions
from Smart_Office import settings
from office_app.models import Notification, Employee, EmployeeDepartment
#from office_app.services import EmailHandler

# region validation


'''
Author: Corrina Barr
Description: Checks to see whether a value is numeric or blank, and whether it's value is greater than it's max value
:param value_name: The name of the value (to be used in any error messages)
:param value: The value being checked
:param max_value: The biggest the number can be
:return: returns an error message if there is an error, else returns None
'''

def check_number_for_errors(value_name, value, max_value):
    if value != '':
        try:
            if float(value) > max_value:
                return "An Error occured: " + value_name + " cannot exceed " + max_value
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return "An Error occured: " + value_name + " must be a number"
    return None


'''
Author: Corrina Barr
Description: Set a number to this with it's own value and it's max value.
             If it's value is greater than its max value, or it is not a number,
             then it will return None
:param value: The value being checked
:param max_value: The biggest the number can be
:return: if there are no issues, it returns the original value. Otherwise it returns the max value
'''


def validate_number(value, max_value):
    if value != '':
        try:
            if float(value) > max_value:
                return max_value
            else:
                return float(value)
        except:
            return 0
    else:
        return 0


'''
Author: Corrina Barr
Description: Set a string to this with it's own value and it's max length.
             If it's length is greater than its max length
             then it will make it shorter
:param value: The value being checked
:param max_length: The biggest length the string can be
:return: if the value's length is good with the max length, it returns the original value.
         Otherwise it cuts off the end of the string and returns it with a value that works with the max length
'''


def validate_string(value, max_length):
    if len(value) <= max_length:
        return value
    else:
        return value[0:max_length - 1]
# endregion

# Region Getting approvers for a form
'''
Author: Corrina Barr
Gets approvers for a form
:param form: The form that you want to get approvers for
:param approval_stage_type: The Approval Stage class for the form. 
                            If TA, TemporaryApprovalStage
                            If TR, TRApprovalProcess
:return: returns list of approvers for the form
'''
def get_approvers_for_form(form, approval_stage_type):
    approval_stages = approval_stage_type.objects.filter(formID=form.formID)
    if approval_stages:
        approvers = []
        for stage in approval_stages:
            approvers.append(stage.approverID)
        return approvers
    else:
        print("No approvers for form with form ID: " + str(form.formID))


'''
Author: Corrina Barr
Gets approvers at current stage of the form or lower, only those who are able to see the form currently
:param form: The form that you want to get approvers for
:param approval_stage_type: The Approval Stage class for the form. 
                            If TA, TemporaryApprovalStage
                            If TR, TRApprovalProcess
:return: returns list of approvers at current stage of the form or lower, only those who are able to see the form currently
'''
def get_approvers_for_form_at_current_stage_or_lower(form, approval_stage_type):
    approval_stages = approval_stage_type.objects.filter(formID=form, stage__lte=int(form.currentStage))
    if approval_stages:
        approvers = []
        for stage in approval_stages:
            approvers.append(stage.approverID)
        return approvers
    else:
        print("No approvers for form with form ID: " + str(form.formID))
        return None
# endregion



# Region Approval Process Actions



'''
This function will approve a form
Author: Corrina Barr
:param request: the request
:param form: the specific form object that is being approved
:param approval_process_type: the main form object's approval proccess type ex: TRapprovalProcess
:return: returns nothing
'''
def approve_form(request, form, approval_process_type, advance_type):

    error_messages = {'fatal_errors': '', 'minor_errors': []}
    item_id_exists = True
    try:
        itemID = form.itemID
    except:
        item_id_exists = False


    aprrovers_stages = approval_process_type.objects.filter(formID=form)
    all_form_approvers = {}
    for stage in aprrovers_stages:
        all_form_approvers.update({stage.approverID: stage.stage})


    stage_to_update = approval_process_type.objects.get(formID=form,
                                                        approverID=Employee.objects.get(associateID=request.session['user_id']),
                                                        stage=form.currentStage)
    if advance_type != None:
        try:
            if advance_type.objects.filter(form=form).count() > 0 and approval_process_type.objects.filter(stage=form.currentStage + 1, formID=form).count() == 0:
                # if form has a advanced application and is at last stage.
                # Call SAP
                try:
                    print(f"form Id: {form.formID}\nsap prefix:{form.sap_prefix}")
                    sapResponse = SAPFunctions.createAP(form.formID, form.sap_prefix)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = "SAP Server inaccessible. Please try approving the form another time."
                    return error_messages
                if sapResponse['SAPDocNo'] is None:
                    error_messages['fatal_errors'] = sapResponse['SAPMessage'] + "\n Please fix the issue and approve again"
                    return error_messages
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            try:
                if advance_type.objects.filter(formID=form).count() > 0 and approval_process_type.objects.filter(stage=form.currentStage + 1, formID=form).count() == 0:
                    # if form has a advanced application and is at last stage.
                    # Call SAP
                    try:
                        sapResponse = SAPFunctions.createAP(form.formID, form.sap_prefix)
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "SAP Server inaccessible. Please try approving the form another time."
                        return error_messages
                    if sapResponse['SAPDocNo'] is None:
                        error_messages['fatal_errors'] = sapResponse['SAPMessage'] + "\n Please fix the issue and approve again"
                        return error_messages
            except:
                if advance_type.objects.filter(form=form.taDetail).count() > 0 and approval_process_type.objects.filter(stage=form.currentStage + 1, formID=form.taDetail).count() == 0:
                    # if form has a advanced application and is at last stage.
                    # Call SAP
                    try:
                        sapResponse = SAPFunctions.createAP(form.formID, form.sap_prefix)
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "SAP Server inaccessible. Please try approving the form another time."
                        return error_messages
                    if sapResponse['SAPDocNo'] is None:
                        error_messages['fatal_errors'] = sapResponse['SAPMessage'] + "\n Please fix the issue and approve again"
                        return error_messages

    # region updating the users stage
    try:
        stage_to_update.set_action_taken('Approved')
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error saving that you approved the form. Please contact IT or try again later"
        return error_messages
    try:
        stage_to_update.count += 1
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error updating amount of people who approved the form on this stage. Please contact IT or try again later"
        return error_messages
    try:
        stage_to_update.comments = request.POST.get('comment')
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['other_errors'].append("Error saving comment.")
    try:
        stage_to_update.date = datetime.now()
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error Logging time of approval. Please contact IT or try again later"
        return error_messages
    try:
        stage_to_update.save()
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error updating your stage on the form. Please contact IT or try again later"
        return error_messages
    # endregion


    stage_completed = False # Used to keep track of whether or not all approvers for the stage have approved the form
    if stage_to_update.count_approvers() <= stage_to_update.count_approved_forms_for_stage():
        stage_completed = True
        next_approvers_query = approval_process_type.objects.filter(stage=form.currentStage + 1,
                                                                    formID=form, actionTaken=None)
        check_if_there_is_a_next_approver = next_approvers_query.first()
        next_is_gs = False
        if check_if_there_is_a_next_approver != None:
            next_approver = next_approvers_query.first().approverID

            next_stage = approval_process_type.objects.filter(stage=form.currentStage,
                                                              formID=form).first()

            next_stage.dayAssigned = datetime.now()
            next_stage.save()

            form.currentStage += 1
            form.save()

            next_approvers_list = []
            for stage in next_approvers_query:
                next_approvers_list.append(stage.approverID)
        else:
            # region This happens if there is no next stage
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            if form.form_type == "Travel Application":
                set_user = Employee.objects.filter(email="dylan.vincent@fii-usa.com").first()
                if set_user:
                    next_approvers_list = [Employee.objects.get(email="dylan.vincent@fii-usa.com")]
                else:
                    gs_person = EmployeeDepartment.objects.filter(departmentID__costCenterName='Supporting - General Service').first()
                    if gs_person:
                        next_approvers_list = [gs_person.associateID]
                    else:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        # If you cannot get gs person, then undo approve and tell them they cannot
                        # approve the form until this gets fixed
                        stage_to_update.set_action_taken(None)
                        stage_to_update.count -= 1
                        stage_to_update.comments = None
                        stage_to_update.date = None
                        stage_to_update.save()
                        error_messages['fatal_errors'] = "Could not find GS to book tickets. Please contact IT immediately."
                        return error_messages

                next_is_gs = True
            else:
                next_approvers_list = [form.employee]

            form.isApproved = True
            form.save()
            # endregion

    if stage_completed:
        for next_approver in next_approvers_list:
            next_stage = approval_process_type.objects.filter(formID=form, stage=form.currentStage, actionTaken=None, approverID=next_approver).first()
            if next_stage:
                next_stage.dayAssigned = datetime.today()
                next_stage.save()
            else:
                if form.form_type == "Travel Application":
                    next_is_gs = True
            if (next_approver != form.employee):
                if next_is_gs == False:
                    if item_id_exists:
                        error_messages = merge_dictionaries(error_messages, notify_approver(employee=next_approver, message_type='next_approver', module=form.module, form=form, request=request, itemID=form.itemID))
                        if error_messages['fatal_errors'] != '':
                            return error_messages
                    else:
                        error_messages = merge_dictionaries(error_messages, notify_approver(employee=next_approver, message_type='next_approver', module=form.module,
                                        form=form, request=request))
                        if error_messages['fatal_errors'] != '':
                            return error_messages
                else:
                    form.isApproved = True
                    form.save()

                    gs_guy = next_approver

                    # Create Notifications/Emails
                    # For employee
                    error_messages = merge_dictionaries(error_messages, notify_approver(employee=form.employee, message_type='approved', module=form.module, form=form, request=request))
                    if error_messages['fatal_errors'] != '':
                        return error_messages

                    # For gs
                    error_messages = merge_dictionaries(error_messages,
                                                        notify_approver(employee=gs_guy, message_type='book_tickets',
                                                                        module=form.module, form=form, request=request))
                    if error_messages['fatal_errors'] != '':
                        return error_messages
                return error_messages
            else:
                error_messages = merge_dictionaries(error_messages,
                                                    notify_approver(employee=form.employee, message_type='approved',
                                                                    module=form.module, form=form, request=request))
                if error_messages['fatal_errors'] != '':
                    return error_messages
        return error_messages
    return error_messages


'''
This will decline a form
Author: Corrina Barr
:param request: the request
:param form: the specific form object that is being declined
:param approval_process_type: the main form object's approval proccess type ex: TRapprovalProcess
:return: returns nothing
'''

def decline_form(request, form, approval_process_type):
    error_messages = {'fatal_errors': '', 'minor_errors': []}

    try:
        forms_creator = form.employee
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        try:
            forms_creator = form.taDetail.employee
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error retrieving form data. Please contact IT and try again later."
            return error_messages

    try:
        stage_to_update = approval_process_type.objects.get(formID=form,
                                                            approverID=Employee.objects.get(associateID=request.session['user_id']),
                                                            stage=form.currentStage)
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error retrieving your approval stage. \nHint: Reload the page to see if you have already done something to this form. " \
                                         "If it says you have not done anything to this form after you reload the page, please contact IT and try again later."
        return error_messages

    try:
        stage_to_update.set_action_taken('Declined')
        stage_to_update.comments = request.POST.get('comment')
        stage_to_update.date = datetime.now()
        stage_to_update.save()
        form.isDeclined = True
        form.save()
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error Saving your action to the form. Please contact IT and try again later."
        return error_messages

    if hasattr(form, 'itemID'):
        error_messages = merge_dictionaries(error_messages, notify_approver(employee=forms_creator, message_type='declined', module=form.module, form=form, request=request, itemID=form.itemID))
    else:
        error_messages = merge_dictionaries(error_messages, notify_approver(employee=forms_creator, message_type='declined', module=form.module, form=form, request=request))

    return error_messages


'''
This will add an approver to the approval list on the stage the person specifies
Author: Corrina Barr
:param form: The specific form the approval stage is for
:param approvel_process_type: The Type of approval proccess being used for the form
                                ex: TRApprovalProcess
:param new_approver: The new approver that will be added
:param stage: the stage the the new approver will be on
'''

def add_approver(form, approval_process_type, new_approvers, stage, request):
    error_messages = {'fatal_errors': '', 'minor_errors': []}

    try:
        all_stages_for_this_form = approval_process_type.objects.filter(formID=form).order_by(
            '-stage')
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = 'Error getting all stages for this form. Please contact IT.'
        return error_messages

    for a_stage in all_stages_for_this_form:
        if a_stage.stage >= stage:
            a_stage.stage += 1
            a_stage.save()

    print("New approvers: " + str(new_approvers))

    try:
        requestor = Employee.objects.get(associateID=request.user.associateID)
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = 'Error getting your employee data. Are you loggged in? ' \
                                         'Try logging out and logging in again and then come back.'
        return error_messages

    for new_approver in new_approvers:
        try:
            print("approver: " + str(new_approver))
            new_process = approval_process_type()
            new_process.create_approval_stage(formID=form,
                                                      approverID=new_approver,
                                                      stage=stage,
                                                      count=0)
            new_process.dayAssigned = datetime.today()
            new_process.save()
        except:
            error_messages['fatal_errors'] = "Error adding new approver: " + str(new_approver) + ". Contact IT if this issue persists."
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return error_messages

        # Create Notification
        error_messages = merge_dictionaries(error_messages, notify_approver(employee=new_approver, message_type='add_cosigner', form=form, module=form.module, request=request))
    return error_messages


'''
Using this you can update the approval list and change who is on a specific stage in the approval process
Author: Corrina Barr
:param form: The specific form the approval stage is for
:param approvel_process_type: The Type of approval proccess being used for the form
                                ex: TRApprovalProcess
:param new_approver: The new approver that will be added
:param old_approver: The employee object for the approver who will be replaced
:param stage: the stage the the new approver will be on
'''


def replace_approver(form, approval_process_type, new_approver, old_approver, stage, request):
    error_messages = {'fatal_errors': '', 'minor_errors': []}
    item_id_exists = True
    try:
        itemID = form.itemID
    except:
        item_id_exists = False

    try:
        stage_to_update = approval_process_type.objects.get(formID=form,
                                                            approverID=old_approver,
                                                            stage=stage)
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages[
            'fatal_errors'] = "Error retrieving your approval stage. \nHint: Reload the page to see if you have already done something to this form. " \
                              "If it says you have not done anything to this form after you reload the page, please contact IT and try again later."
        return error_messages
    try:
        stage_to_update.approverID = new_approver
        stage_to_update.dayAssigned = datetime.today()
        stage_to_update.save()
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error updating approval process, please try reloading the page or contacting IT."
        return error_messages

    if hasattr(form, 'itemID'):
        error_messages = merge_dictionaries(error_messages,
                                            notify_approver(employee=new_approver, message_type='next_approver',
                                                            module=form.module, form=form, request=request,
                                                            itemID=form.itemID))
    else:
        error_messages = merge_dictionaries(error_messages, notify_approver(employee=new_approver, message_type='next_approver', module=form.module, form=form, request=request, itemID=form.itemID))

    return error_messages


'''
This function will approve modifications to a form
Author: Corrina Barr
:param request: the webpage request
:param form: the specific form that is being modified
:param approvel_process_type: The modal the the form is using for its approval process ex: TRApprovalProcess
:param modified_fields_type: The modal the form is using to store it's modified fields ex: TRModifiedFields
:return: returns nothing
'''

def approve_modifications(request, form, approval_process_type, modified_fields_type):
    error_messages = {'fatal_errors': '', 'minor_errors': []}

    # Check to see whether or not the stage below has had all approvers do action.
    # If so, go up a stage
    # Else, go down one stage so other approvers on that stage can approve it
    try:
        count_of_people_on_requestors_stage_who_did_not_approve_form = approval_process_type.objects.filter(stage=form.currentStage - 1,
                                                                               formID=form, actionTaken=None).count()
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Retrieving approval process data, please try reloading the page or contacting IT."
        return error_messages

    try:
        if count_of_people_on_requestors_stage_who_did_not_approve_form <= 0:
            next = form.currentStage + 1
        else:
            next = form.currentStage - 1
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error updating stages, please try reloading the page or contacting IT."
        return error_messages

    if form.advance_type != None:
        try:
            if form.advance_type.objects.filter(form=form).count() > 0 and approval_process_type.objects.filter(
                    stage=form.currentStage + 1, formID=form).count() == 0:
                # if form has a advanced application and is at last stage.
                # Call SAP
                try:
                    sapResponse = SAPFunctions.createAP(form.formID, form.sap_prefix)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages[
                        'fatal_errors'] = "SAP Server inaccessible. Please try approving the form another time."
                    return error_messages
                if sapResponse['SAPDocNo'] is None:
                    error_messages['fatal_errors'] = sapResponse[
                                                         'SAPMessage'] + "\n Please fix the issue and approve again"
                    return error_messages
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            try:
                if form.advance_type.objects.filter(formID=form).count() > 0 and approval_process_type.objects.filter(
                        stage=form.currentStage + 1, formID=form).count() == 0:
                    # if form has a advanced application and is at last stage.
                    # Call SAP
                    try:
                        sapResponse = SAPFunctions.createAP(form.formID, form.sap_prefix)
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages[
                            'fatal_errors'] = "SAP Server inaccessible. Please try approving the form another time."
                        return error_messages
                    if sapResponse['SAPDocNo'] is None:
                        error_messages['fatal_errors'] = sapResponse[
                                                             'SAPMessage'] + "\n Please fix the issue and approve again"
                        return error_messages
            except:
                if form.advance_type.objects.filter(form=form.taDetail).count() > 0 and approval_process_type.objects.filter(
                        stage=form.currentStage + 1, formID=form.taDetail).count() == 0:
                    # if form has a advanced application and is at last stage.
                    # Call SAP
                    try:
                        sapResponse = SAPFunctions.createAP(form.formID, form.sap_prefix)
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages[
                            'fatal_errors'] = "SAP Server inaccessible. Please try approving the form another time."
                        return error_messages
                    if sapResponse['SAPDocNo'] is None:
                        error_messages['fatal_errors'] = sapResponse[
                                                             'SAPMessage'] + "\n Please fix the issue and approve again"
                        return error_messages

    # Delete modified field objects:
    modified_fields_to_delete = modified_fields_type.objects.filter(formID=form.formID)
    for field in modified_fields_to_delete:
        field.delete()

    try:
        forms_creator = form.employee
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error retreiving form's creator's data, please try reloading the page or contacting IT."
        return error_messages

    try:
        stage_to_update = approval_process_type.objects.get(formID=form,
                                                            approverID=forms_creator,
                                                            stage=form.currentStage)
        stage_to_update.set_action_taken('Approved Modifications')
        stage_to_update.count += 1
        stage_to_update.comments = request.POST.get('comment')
        stage_to_update.date = datetime.now()
        stage_to_update.save()

        form.currentStage = next
        form.save()
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error updating approval process, please try reloading the page or contacting IT."
        return error_messages

    next_stages = approval_process_type.objects.filter(stage=form.currentStage,
                                                       formID=form, actionTaken=None)
    for stage in next_stages:
        try:
            next_approver = stage.approverID
            stage.dayAssigned = datetime.today()
            stage.save()
            error_messages = merge_dictionaries(error_messages, notify_approver(employee=next_approver, form=form,
                                                                                message_type='next_approver',
                                                                                module=form.module, request=request))
        except:
            try:
                next_approver = Employee.objects.get(email="dylan.vincent@fii-usa.com")
            except:
                try:
                    next_approver = EmployeeDepartment.objects.filter(
                        departmentID__name='Supporting - General Service').first().associateID
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages[
                        'other_errors'] = "Error sending email notifying general service to book tickets, please contacting IT and notify your general service to book tickets."
            if next_approver:
                error_messages = merge_dictionaries(error_messages, notify_approver(employee=next_approver, form=form, message_type='book_tickets', module=form.module, request=request))

    return error_messages



'''
This function will approve modifications to a form
Author: Corrina Barr
:param request: the webpage request
:param form: the specific form that is being modified
:param approvel_process_type: The modal the the form is using for its approval process ex: TRApprovalProcess
:param modified_fields_type: The modal the form is using to store it's modified fields ex: TRModifiedFields
:return: returns nothing
'''


def decline_modifications(request, form, approval_process_type, modified_fields_type):
    from travel.models import TravelDetailCompany

    error_messages = {'fatal_errors': '', 'minor_errors': []}

    # Delete modified field objects:
    try:
        modified_fields_to_delete = modified_fields_type.objects.filter(formID=form.formID)
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error removing modifications. Please contact IT."
        return error_messages

    for field in modified_fields_to_delete:
        field.delete()

    # If form is Employee Information will have to delete an employee detail
    if form.form_type == "Travel Application":
        try:
            rows_to_delete = TravelDetailCompany.objects.filter(modifiedField=True, detailID__formID=form)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error removing modifications. Please contact IT."
            return error_messages
        for row in rows_to_delete:
            row.delete()

    try:
        stage_to_update = approval_process_type.objects.get(formID=form,
                                                            approverID=Employee.objects.get(associateID=request.session['user_id']),
                                                            stage=form.currentStage)
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error retrieving approval stage data. This sometimes happens if you are no longer on the current stage of the form. " \
                                         "Please reload the page and check. Otherwise please contact IT."
        return error_messages
    try:
        stage_to_update.set_action_taken('Declined Modifications')
        stage_to_update.count += 1
        stage_to_update.comments = request.POST.get('comment')
        stage_to_update.date = datetime.now()
        stage_to_update.save()
        form.currentStage -= 1
        form.save()
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error uploading. Please contact IT."
        return error_messages

    employees_to_email = []
    modication_requestor = None
    try:
        modication_requestor = approval_process_type.objects.get(stage=form.currentStage, formID=form.formID, actionTaken='Requested Modifications').approverID
        employees_to_email.append(modication_requestor)
    except:
        error_messages['other_errors'].append("Error sending email to modification requestor. Please contact IT.")

    for employee_to_email in employees_to_email:
        if employee_to_email == modication_requestor:
            error_messages = merge_dictionaries(error_messages, notify_approver(employee=employee_to_email, form=form, message_type="modification_declined", module=form.module, request=request))
        else:
            error_messages = merge_dictionaries(error_messages, notify_approver(employee=employee_to_email, form=form,
                                                                                message_type="next_approver",
                                                                                module=form.module, request=request))
    return error_messages


'''
This function will update the approval process when a modification request is sent
Author: Corrina Barr
:param request: the webpage request
:param form: the specific form that is being modified
:param approvel_process_type: The modal the the form is using for its approval process ex: TRApprovalProcess
:return: returns nothing
'''


def update_stages_for_modification_request(request, form, approval_process_type):
    error_messages = {'fatal_errors': '', 'minor_errors': []}

    try:
        stage_to_update = approval_process_type.objects.get(formID=form,
                                                            approverID=Employee.objects.get(
                                                                associateID=request.session['user_id']),
                                                            stage=form.currentStage)
        stage_to_update.set_action_taken('Requested Modifications')
        stage_to_update.comments = request.POST.get('comment')
        stage_to_update.date = datetime.now()
        stage_to_update.save()
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error updating your stage of the form. This sometimes happens if you are no longer on the current stage of the form. " \
                                         "Please reload the page and check. Otherwise please contact IT."
        return error_messages

    # Create a new approval stage for the user:
    try:
        all_stages_for_this_form = approval_process_type.objects.filter(formID=form).order_by(
            '-stage')
    except:
        stage_to_update.set_action_taken(None)
        stage_to_update.comments = request.POST.get('comment')
        stage_to_update.date = None
        stage_to_update.save()
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error retrieving approval process data. Please contact IT."
        return error_messages

    for stage in all_stages_for_this_form:
        if stage.stage > form.currentStage:
            stage.stage += 1
            stage.save()

    try:
        form.currentStage += 1
        form.save()
    except:
        stage_to_update.set_action_taken(None)
        stage_to_update.comments = request.POST.get('comment')
        stage_to_update.date = None
        stage_to_update.save()
        for stage in all_stages_for_this_form:
            if stage.stage > form.currentStage + 1:
                stage.stage -= 1
                stage.save()
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error updating form's stage. Please contact IT."
        return error_messages

    forms_creator = form.employee

    try:
        approval_process_type.objects.get(formID=form,
                                          approverID=Employee.objects.get(associateID=forms_creator.associateID)).delete()
    except:
        print("No old modification request approval stage to delete")

    try:
        new_stage = approval_process_type()
        new_stage.create_approval_stage(formID=form,
                                          approverID=Employee.objects.get(associateID=forms_creator.associateID),
                                          stage=form.currentStage,
                                          count=0)
        new_stage.dayAssigned = datetime.today()
        new_stage.save()
    except:
        stage_to_update.set_action_taken(None)
        stage_to_update.comments = request.POST.get('comment')
        stage_to_update.date = None
        stage_to_update.save()
        for stage in all_stages_for_this_form:
            if stage.stage > form.currentStage + 1:
                stage.stage -= 1
                stage.save()
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['fatal_errors'] = "Error sending modification request to form's creator. Please contact IT."
        return error_messages



    # Create Notification
    error_messages = merge_dictionaries(error_messages, notify_approver(employee=forms_creator, form=form, message_type="modification_request", module=form.module, request=request))
    return error_messages

# endregion


# region Other Useful things
'''
This function converts an html message to a text message, replacing <br> with \n and turns links into 
just the url
Author: Corrina Barr
:param html_message: the html string that will be converted to text
:return: returns the html_message as text
'''
def convert_html_message_to_text(html_message):
    html_message = html_message.replace('<br>', '\n')
    html_message = html_message.replace("<a href='", '')
    html_message = html_message.replace('<a href="', '')
    html_message = html_message.replace("/'>Smart Office</a>", '')
    html_message = html_message.replace('/">Smart Office</a>', '')
    html_message = html_message.replace("<b>", '*')
    html_message = html_message.replace("</b>", '')
    return html_message



'''
This function merges two dictionaries. If they have the same key, it will merge both the values. 
If one has a key that the other doesn't, the new one will keep that key too.
Author: Corrina Barr
:param dict1: The dictionary that will be merged with dict2
:param dict2: The dictionary that will be merged with dict1
:return: returns the merged dictionary
'''
def merge_dictionaries(dict1, dict2):
    merged_dict = dict1

    # Get key list for each dictionary
    #print(f"dictionary 1: {dict1} \ndictonary 2: {dict2}")
    dict1keys = list(dict1.keys())
    dict2keys = list(dict2.keys())

    for key in dict2keys:
        if key in dict1keys:
            #print(f"merging keys {key} value {merged_dict[key]} to {dict2[key]}")
            merged_dict[key] += dict2[key]
        else:
            merged_dict.update({key: dict2[key]})

    return merged_dict

# endregion



# # region Notification Handling
'''
This creates a notification and email
:param employee: the employee receiving the message
:param form: must be the object that has attributes like url and form_type
:param message_type: the type of message being sent
:param module: The module the message is coming from
'''
def notify_approver(employee, message_type, form, request, module=None, itemID=None):
    from office_app.services import EmailHandler
    error_messages = {'fatal_errors': '', 'other_errors': []}
    # Create Notification
    # Message types are:
    #       approved
    #       declined
    #       next_approver
    #       modification_request
    #       modification_declined
    #       book_tickets
    #       add_cosigner
    #       generate_po
    if module == None:
        module = form.module
    try:
        notification = Notification(employee=employee, is_unread=True,
                                    created_on=datetime.now().astimezone(),
                                    module=module)
        notification.title = form.form_type
        notification.body = get_notification_body(message_type, form)
        notification.link = form.form_url_without_base_url
        notification.save()
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        error_messages['other_errors'].append("Error sending notification to " + str(employee))

    # Email handling
    # Errors sending emails are never fatal, form will still submit whether or not email was sent correctly
    if message_type == "approved":
        error_messages['other_errors'] = EmailHandler.send_form_approved_email(formType=form.sap_prefix, formID=form.formID, originalRequester=form.employee)
    elif message_type == "declined":
        error_messages['other_errors'] = EmailHandler.send_declined_email(formType=form.sap_prefix, formID=form.formID, requester=form.employee, approvers=[form.employee], decliningUser=Employee.objects.filter(associateID=request.user.associateID).first(), itemID=itemID)
    elif message_type == "next_approver":
        error_messages['other_errors'] = EmailHandler.send_notification_email(formType=form.sap_prefix, formID=form.formID, requester=form.employee, approvers=[employee])
    elif message_type == "modification_request":
        error_messages['other_errors'] = EmailHandler.send_modification_email(form.sap_prefix, form.formID, form.employee, Employee.objects.filter(associateID=request.user.associateID))
    elif message_type == "modification_declined":
        error_messages['other_errors'] = EmailHandler.send_notification_email(formType=form.sap_prefix, formID=form.formID, requester=form.employee, approvers=[employee])
    elif message_type == "book_tickets":
        error_messages['other_errors'] = EmailHandler.send_gs_email(formType=form.sap_prefix, formID=form.formID, recipient=employee)
    elif message_type == 'add_cosigner':
        error_messages['other_errors'] = EmailHandler.send_cosigner_email(formType=form.sap_prefix, formID=form.formID, newCosigner=employee, requester=Employee.objects.filter(associateID=request.user.associateID).first())
    elif message_type == 'generate_po':
        error_messages['other_errors'] = EmailHandler.send_po_email(formType=form.sap_prefix, formID=form.formID, recipient=employee)
    return error_messages


'''
Gets body message for notification or form action on Smart-Office
'''
def get_notification_body(message_type, form):
    if message_type == 'approved':
        return "Your form # " + str(form.formID) + " has been completely approved"
    if message_type == 'declined':
        return "Your form # " + str(form.formID) + " has been declined"
    if message_type == 'next_approver':
        return "Form # " + str(form.formID) + " requires your approval"
    if message_type == 'modification_request':
        return "Modifications to your form # " + str(form.formID) + " are requested"
    if message_type == 'modification_declined':
        return "Your modifications to form # " + str(form.formID) + " have been declined"
    if message_type == 'book_tickets':
        return "Form # " + str(form.formID) + " requires travel ticket booking"
    if message_type == "add_cosigner":
        return "Form # " + str(form.formID) + " requires your approval"
    if message_type == 'generate_po':
        return "You need to generate a PO for the form # " + str(form.formID)


# endregion
