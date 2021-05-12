import datetime
import os
import sys
import traceback
import pdfrw
import uuid
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from smart_hr.models import *
from office_app.models import *

'''
    Create new checklist
    Written by: Zaawar Ejaz
    :param request: the webpage request
    :return: returns boolean
'''


def create_checklist(request):
    # Create employee instance
    employee = Employee()

    try:
        # Get data from form
        firstName = request.POST.get("first_name")
        middleName = request.POST.get("middle_name")
        lastName = request.POST.get("last_name")
        preferredName = request.POST.get("preferred_name")
        email = request.POST.get("email")
        department = request.POST.get("department")
        position = request.POST.get("position")
        manager = request.POST.get("manager")
        hire_date = request.POST.get("hire_date")
        if hire_date is "": hire_date = None

        # Validate the data
        required = []
        if firstName == "": required.append("Employee First Name is Required")
        if lastName == "": required.append("Employee Last Name is Required")
        if email == "": required.append("E-mail Address is Required")
        if department is None: required.append("Department is Required")
        if manager is None: required.append("Manager is Required")
        if position == "": required.append("Position is Required")
        if hire_date is None: required.append("Hire Date is Required")

        for task in ChecklistTask.objects.filter(status=True):
            if request.POST.get("assignee_" + str(task.taskID)) == "":
                required.append("Assignee is Required")
                break

        # Return false is any required field is missing
        if len(required) > 0:
            for msg in required: messages.error(request, msg)
            return False

        # Check if new checklist already exist
        query = Employee.objects.filter(email=email)
        if query.count() > 0:
            messages.error(request, "Employee with this email already exist.")
            return False

        # Create new employee information
        employee.firstName = firstName
        employee.middleName = middleName
        employee.lastName = lastName
        employee.otherName = preferredName
        employee.email = email
        employee.doh = hire_date
        employee_department = EmployeeDepartment()
        employee_department.joiningDate = hire_date

        try:
            employee_department.departmentID = CostCenter.objects.get(costCenterCode=department)
        except:
            messages.error(request, "Department not found. Please contact the I.T Department")
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return False

        try:
            employee_department.managerID = Employee.objects.get(associateID=manager)
        except:
            messages.error(request, "Manager not found. Please contact the I.T Department")
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return False

        # If role doesn't exists, create one.
        try:
            employee_department.roleID = Role.objects.get(roleID=position)
        except:
            role = Role(title=position, description=request.POST.get("position_desc"))
            role.save()
            employee_department.roleID = role

        employee.associateID = "temp_" + str(uuid.uuid1())
        employee_department.associateID = employee
        employee.save()
        employee_department.save()

        # Store task Assignees for email
        taskAssignees = []

        # Create checklist for the new employee
        for task in ChecklistTask.objects.filter(status=True):
            checklist_item = NewHireChecklist()
            checklist_item.empID = employee
            checklist_item.taskID = task
            dueDate = request.POST.get("date_" + str(task.taskID))
            if dueDate: checklist_item.dueDate = dueDate
            checklist_item.taskAssignee = Employee.objects.get(associateID=request.POST.get("assignee_" + str(task.taskID)))
            checklist_item.completed = False
            checklist_item.dateCompleted = None
            checklist_item.save()

            # Add task assignee to array if not exist
            if checklist_item.taskAssignee not in taskAssignees:
                taskAssignees.append(checklist_item.taskAssignee)

        # Send email to assignee and create notification
        message = "This is an email to inform you that there is a pending New Hire Requirements that needs your attention."
        for assignee in taskAssignees:
            notification = Notification(employee=assignee, is_unread=True, created_on=datetime.today(), module="smart_hr")
            notification.title = "New Hire Checklist"
            notification.body = "You have a pending task for the checklist"
            notification.link = "/smart_hr/checklist_detail/" + str(employee.associateID)
            notification.save()

            send_email_to_recipents(request, assignee, employee, message)

        messages.success(request, "Checklist has been created successfully.")
        return True

    except:
        messages.error(request, "Error creating checklist. Please contact the I.T department.")
        if employee.id is not None:
            employee.delete()
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        return False

'''
    Send email to then email receipents
    Written by: Zaawar Ejaz
    :param request: the webpage request, email array, employee object
    :return: returns boolean
'''

def send_email_to_recipents(request, assignee, employee, message):
    try:
        newemp = EmployeeDepartment.objects.get(associateID=employee)
        assigneeTasks = []
        for task in NewHireChecklist.objects.filter(empID=employee, taskAssignee=assignee).order_by('completed'):
            assigneeTasks.append(task)

        from_email = settings.EMAIL_HOST_USER
        to_email = [assignee.email]
        subject = "Smart HR | New Hire Requirements Checklist"
        html_message = render_to_string('smart_hr/email_template/checklist_email.html', {'request': request, 'newemp': newemp, 'assigneeTasks':assigneeTasks, 'message':message})
        plain_message = strip_tags(html_message)

        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        return True

    except:
        messages.error(request, "Email not sent to some recipients. Please contact the I.T department.")
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        return False

'''
    Update the current checklist
    Written by: Zaawar Ejaz
    :param request: the webpage request, employee id
    :return: returns boolean
'''


def edit_checklist(request, employee):
    try:
        # Get employee's checklist
        checklist = NewHireChecklist.objects.filter(empID=employee)

        # Return false if assignee is not set
        for task in checklist:
            if request.POST.get("assignee_" + str(task.taskID)) == "":
                messages.error(request, "Assignee is Required")
                return False

        # Email Array
        taskAssignees = []
        previousAssignees = []

        # Go through each tasks
        for task in checklist:
            # Get assignee ID from the form
            assignee_id = request.POST.get("assignee_" + str(task.taskID))

            # if the new assignee is different then the old assignee
            if str(assignee_id) != str(task.taskAssignee.associateID):
                # Add new employee's email to email recipients
                taskAssignees.append(Employee.objects.get(associateID=assignee_id))
                previousAssignees.append(task.taskAssignee)

            # Set task information
            task.taskAssignee = Employee.objects.get(associateID=assignee_id)

            date = request.POST.get("date_" + str(task.taskID))
            if date != "": task.dueDate = date

            check = request.POST.get("check_" + str(task.taskID))

            if task.completed:
                if check is None:
                    task.dateCompleted = None
                    task.completed = False
            else:
                if check == "on":
                    task.dateCompleted = datetime.today().date()
                    task.completed = True

            task.save()

        # Send email to assignees
        message = "This is an email to inform you that there is a pending New Hire Requirements that needs your attention."
        for assignee in set(taskAssignees):
            notification = Notification(employee=assignee, is_unread=True, created_on=datetime.today(), module="smart_hr")
            notification.title = "New Hire Checklist"
            notification.body = "You have a pending task for the checklist"
            notification.link = "/smart_hr/checklist_detail/" + str(employee.associateID)
            notification.save()

            send_email_to_recipents(request, assignee, employee, message)

        # Send email to assignees
        message = "This is an email to inform you that you are removed from one of the requirements for the New " \
                  "Hire Checklist. Below is the list of tasks assigned to you (if any)."
        for previousAssignee in set(previousAssignees):
            notification = Notification(employee=previousAssignee, is_unread=True, created_on=datetime.today(), module="smart_hr")
            notification.title = "New Hire Checklist"
            notification.body = "You are removed from one or more tasks"
            notification.link = "/smart_hr/checklist_detail/" + str(employee.associateID)
            notification.save()

            send_email_to_recipents(request, previousAssignee, employee, message)

        if NewHireChecklist.objects.filter(empID=employee,completed=False).count() == 0:
            for userperm in UserPermissions.objects.filter(permission__key="view_all_tasks"):
                notification = Notification(employee=userperm.user, is_unread=True, created_on=datetime.today(), module="smart_hr")
                notification.title = "New Hire Checklist"
                notification.body = "All tasks are completed in the checklist"
                notification.link = "/smart_hr/checklist_detail/" + str(employee.associateID)
                notification.save()

        messages.success(request, "Checklist has been updated successfully.")
        return True

    except:
        messages.error(request, "Error submitting form. Please contact the I.T department.")
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        return False


'''
    Update the current checklist
    Written by: Zaawar Ejaz
    :param request: the webpage request, employee id
    :return: returns boolean
'''


def update_checklist(request, employee):
    try:
        checklist = NewHireChecklist.objects.filter(empID=employee)
        for task in checklist:
            check = request.POST.get("check_" + str(task.taskID))

            if task.completed:
                if check is None:
                    task.completed = False
                    task.dateCompleted = ""
            else:
                if check == 'on' and task.taskAssignee.associateID == request.session['user_id']:
                    task.dateCompleted = datetime.today().date()
                    task.completed = True

            task.save()

        if NewHireChecklist.objects.filter(empID=employee,completed=False).count() == 0:
            for userperm in UserPermissions.objects.filter(permission__key="view_all_tasks"):
                notification = Notification(employee=userperm.user, is_unread=True, created_on=datetime.today(), module="smart_hr")
                notification.title = "New Hire Checklist"
                notification.body = "All tasks are completed in the checklist"
                notification.link = "/smart_hr/checklist_detail/" + str(employee.employeeID)
                notification.save()

        messages.success(request, "Your response have been submitted successfully.")
        return True

    except:
        messages.error(request, "Error submitting form. Please contact the I.T department.")
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        return False


'''
    This function will take all the data from the PAF form and save it in the models.
    Author: Corrina Barr, Zaawar Ejaz
    :param request: The webpage request
    :return: Boolean
'''


def post_PAF(request):
    # Create paf object
    paf = PAF()

    try:
        # Gather data from form
        actionType = request.POST.get('personnel_actions')
        emp_firstName = request.POST.get('employee_fname')
        emp_middleName = request.POST.get('employee_mname')
        emp_lastName = request.POST.get('employee_lname')
        emp_otherName = request.POST.get('employee_oname')
        emp_phone = request.POST.get('phone_number')
        emp_email = request.POST.get('email')
        emp_homeAddress = request.POST.get('address')
        department = request.POST.get('department')
        unit = request.POST.get('business_unit')
        position = request.POST.get('position')
        employmentType = request.POST.get('employment_type')
        dateOfHire = str(request.POST.get('date_of_hire'))
        if dateOfHire is "": dateOfHire = None
        salary_from = request.POST.get('from_salary')
        salary_to = request.POST.get('to_salary')
        salary_changeCode = request.POST.get('change_code')
        salary_changePercent = request.POST.get('change')
        salary_effectiveDate = str(request.POST.get('effective_date'))
        if salary_effectiveDate is "": salary_effectiveDate = None
        salary_from1 = request.POST.get('from_salary1')
        salary_to1 = request.POST.get('to_salary1')
        salary_changeCode1 = request.POST.get('change_code1')
        salary_changePercent1 = request.POST.get('change1')
        salary_effectiveDate1 = str(request.POST.get('effective_date1'))
        if salary_effectiveDate1 is "": salary_effectiveDate1 = None
        salary_from2 = request.POST.get('from_salary2')
        salary_to2 = request.POST.get('to_salary2')
        salary_changeCode2 = request.POST.get('change_code2')
        salary_changePercent2 = request.POST.get('change2')
        salary_effectiveDate2 = str(request.POST.get('effective_date2'))
        if salary_effectiveDate2 is "": salary_effectiveDate2 = None
        position_from = request.POST.get('position_from')
        position_to = request.POST.get('position_to')
        position_chcode = request.POST.get('position_chcode')
        position_effectivedate = str(request.POST.get('position_effectivedate'))
        if position_effectivedate is "": position_effectivedate = None
        department_from = request.POST.get('department_from')
        department_to = request.POST.get('department_to')
        department_chcode = request.POST.get('department_chcode')
        department_effectivedate = str(request.POST.get('department_effectivedate'))
        if department_effectivedate is "": department_effectivedate = None
        reportsTo_from = request.POST.get('reportsTo_from')
        reportsTo_to = request.POST.get('reportsTo_to')
        reportsTo_chcode = request.POST.get('reportsTo_chcode')
        reportsTo_effectivedate = str(request.POST.get('reportsTo_effectivedate'))
        if reportsTo_effectivedate == "":
            reportsTo_effectivedate = None
        comments = request.POST.get('comments')
        relocation = request.POST.get('relocation_package')
        approver1 = request.POST.get('approved1_name')
        approver2 = request.POST.get('approved2_name')
        approver3 = request.POST.get('approved3_name')
        approver4 = request.POST.get('approved4_name')
        approver5 = request.POST.get('approved5_name')
        approver6 = request.POST.get('approved6_name')

        # Validate the data
        required = []
        if actionType is None: required.append("Action Type is required")
        if employmentType is None: required.append("Employee Status is required")
        if unit is None: required.append("Business Unit is required")
        if department is None: required.append("Department is required")
        if emp_firstName == "": required.append("Employee First Name is Required")
        if emp_lastName == "": required.append("Employee Last Name is Required")
        if emp_phone == "": required.append("Phone Number is Required")
        if emp_email == "": required.append("E-mail Address is Required")
        if emp_homeAddress == "": required.append("Address is Required")
        if position == "": required.append("Position is Required")
        if actionType == "New Hire" and dateOfHire is None: required.append("Date of Hire is Required")

        # Return false is any required field is missing
        if len(required) > 0:
            for msg in required:
                messages.error(request, msg)
            return False

        # Make data dictionary for PDF
        data_dict = {
            'businessunit': unit,
            'department': department,
            'employeename': emp_lastName + " " + emp_firstName + " " + emp_middleName,
            'othername': emp_otherName,
            'address': emp_homeAddress,
            'phonenumber': emp_phone,
            'emailaddress': emp_email,
            'position': position,
            'dateofhire': dateOfHire,
            'salary_from': salary_from,
            'salary_to': salary_to,
            'salary_chcode': salary_changeCode,
            'salary_change': salary_changePercent,
            'salary_effectivedate': salary_effectiveDate,
            'pre1_from': salary_from1,
            'pre1_to': salary_to1,
            'pre1_chcode': salary_changeCode1,
            'pre1_change': salary_changePercent1,
            'pre1_effectivedate': salary_effectiveDate1,
            'pre2_from': salary_from2,
            'pre2_to': salary_to2,
            'pre2_chcode': salary_changeCode2,
            'pre2_change': salary_changePercent2,
            'pre2_effectivedate': salary_effectiveDate2,
            'position_from': position_from,
            'position_to': position_to,
            'position_chcode': position_chcode,
            'position_effectivedate': position_effectivedate,
            'department_from': department_from,
            'department_to': department_to,
            'department_chcode': department_chcode,
            'department_effectivedate': department_effectivedate,
            'reportsto_from': reportsTo_from,
            'reportsto_to': reportsTo_to,
            'reportsto_chcode': reportsTo_chcode,
            'reportsto_effectivedate': reportsTo_effectivedate,
            'comments': comments,
            'sign1_name': approver1,
            'sign2_name': approver2,
            'sign3_name': approver3,
            'sign4_name': approver4,
            'sign5_name': approver5,
            'sign6_name': approver6,
        }

        if actionType == "New Hire":
            data_dict['action_newhire'] = "X"
        elif actionType == "Transfer":
            data_dict['action_transfer'] = "X"
        elif actionType == "Salary Change":
            data_dict['action_salarychange'] = "X"
        elif actionType == "Position/Department Change":
            data_dict['action_positionchange'] = "X"
        elif actionType == "Termination":
            data_dict['action_termination'] = "X"

        if employmentType == "Exempt/Salaried":
            data_dict['status_salaried'] = "X"
        elif employmentType == "Non-Excempt/Hourly":
            data_dict['status_hourly'] = "X"
        elif employmentType == "Full-Time":
            data_dict['status_fulltime'] = "X"
        elif employmentType == "Part-Time":
            data_dict['status_parttime'] = "X"
        elif employmentType == "Temporary":
            data_dict['status_temporary'] = "X"

        if relocation == "yes":
            data_dict['relocation_yes'] = "X"
        elif relocation == "no":
            data_dict['relocation_no'] = "X"

        # Add PAF data to database
        createdBy = str(request.session['id'])
        paf.createPAF(emp_firstName, emp_middleName, emp_lastName, emp_otherName, emp_email, emp_phone, emp_homeAddress,
                      dateOfHire, position, unit, department, actionType, employmentType, createdBy)

        # Generate PDF file
        pdf_file = generate_pdf(data_dict)

        # Create file download response
        if os.path.exists(pdf_file):
            with open(pdf_file, 'rb') as f:
                file = f.read()
            response = HttpResponse(file, content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=PAF-' + os.path.basename(pdf_file)
        else:
            raise FileNotFoundError

    except:
        paf.delete()
        messages.error(request, "Error submitting form. Please contact the I.T Department.")
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        return False

    # Email PDF file
    email = EmailMessage()
    email.from_email = settings.EMAIL_HOST_USER
    email.to = [request.user.email]
    email.subject = "PAF you have created - Smart HR | FII USA"
    email.body = "Attached is the PAF you have created using PAF Generator."
    email.attach_file(pdf_file)
    email.send()

    # Delete the file
    os.remove(pdf_file)

    # Create success message
    messages.success(request, "PAF has been created successfully.")
    return response


'''
    This function will generate pdf form from the data provided and return file response
    Written By: Zaawar Ejaz
    :param dict: Dictionary
    :return: File response
'''


def generate_pdf(data_dict):
    try:
        # Read PDF Template
        template_pdf = pdfrw.PdfReader(os.path.join(settings.STATIC_ROOT, 'smart_hr\\paf_template.pdf'))
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
        pdf_file = 'media/pafs/' + data_dict['employeename'].replace(" ", "-") + '.pdf'
        pdfrw.PdfWriter().write(pdf_file, template_pdf)

        return pdf_file

    except:
        raise Exception("Error generating PDF File")


# """
# This function takes a checkbox value (on or None) and returns True for on and False for None
# Author: Corrina Barr
# :param check_value: checkbox value (on or None)
# :return: returns either True or False
# """
#
#
# def convert_check_to_bool(check_value):
#     if str(check_value) == 'on':
#         return True
#     else:
#         return False
#

# '''
# This function updates the message that will display on the index page validating that the user has submitted their form,
# IF the user has actually submitted a form. If not, the message will be set to an empty string.
# Author: Corrina Barr
# :param request: The webpage request
# :param message: A string variable that is the message that will appear telling the user that they have sucessfully
#                 submitted their form if they have submitted a form. If the request is post, this string will then be
#                 stored as a session variable, otherwise the variable will be set to an empty string.
# :return: returns no variables
# '''
#
#
# def update_message(request, message):
#     if request.method == "POST":
#         request.session['message'] = message
#     else:
#         request.session['message'] = ''
#
#
# # endregion


# # region Slicing Full Name
# '''
# This function will take a full name in format "Last First Middle" and return the first name
# Author: Corrina Barr
# :param full_name: A string that represents a full name in the format "Last First Middle"
# :return: Returns the first name as a string
# '''
#
#
# def get_first_name(full_name):
#     space_between_first_and_last_name = full_name.find(' ')
#     space_between_first_and_middle_name = full_name.find(' ', space_between_first_and_last_name + 1)
#     indexes = slice(space_between_first_and_last_name, space_between_first_and_middle_name)
#     first_name = full_name[indexes]
#     return first_name


# '''
# This function will take a full name in format "Last First Middle" and return the last name
# Author: Corrina Barr
# :param full_name: A string that represents a full name in the format "Last First Middle"
# :return: Returns the last name as a string
# '''
#
#
# def get_last_name(full_name):
#     space_between_first_and_last_name = full_name.find(' ')
#     indexes = slice(None, space_between_first_and_last_name)
#     last_name = full_name[indexes]
#     return last_name
#
#
# '''
# This function will take a full name in format "Last First Middle" and return the middle name
# Author: Corrina Barr
# :param full_name: A string that represents a full name in the format "Last First Middle"
# :return: Returns the middle name as a string
# '''
#
#
# def get_middle_name(full_name):
#     space_between_first_and_last_name = full_name.find(' ')
#     space_between_first_and_middle_name = full_name.find(' ', space_between_first_and_last_name + 1)
#     indexes = slice(space_between_first_and_middle_name + 1, None)
#     middle_name = full_name[indexes]
#     print(middle_name)
#     return middle_name
#
#
# # endregion
#
#
# # region Turning Models into Dictionaries
# # region smart_hr models
# '''
# This function returns a list of dictionaries that represents PAFAUthorizor objects.
# It it used to help compare values with PAF objects who go through the get_PAF_for_checklist function
# Author: Corrina Barr
# :return: returns a list of dictionaries. Each dictionary represents a PAFAuthorizor object
# '''
#
#
# def get_PAFAuthorizors_for_checklist():
#     managers = PAFAuthorizer.get_Paf_Managers()
#     managers_list = []
#
#     for obj in managers:
#         manager = PAFAuthorizer.get_string_version(obj, obj.pafID)
#         managers_list.append({
#
#             'pafID': manager,
#             'fullName': PAF.get_string_version(obj, obj.fullName),
#             'signature_number': PAF.get_string_version(obj, obj.signature_number),
#             'dateSigned': PAF.get_string_version(obj, obj.dateSigned),
#         })
#
#     return managers_list
#
#
# '''
# This function returns a list of dictionaries that represents PAF objects.
# It it used to help compare values with PAF objects who go through the get_PAFAuthorizors_for_checklist function
# Author: Corrina Barr
# :return: returns a list of dictionaries. Each dictionary represents a PAF object
# '''
#
#
# def get_PAFs_for_checklist():
#     pafs = PAF.objects.all()
#     paf_list = []
#
#     for obj in pafs:
#         paf = PAF.get_string_version(obj, obj.pafID)
#         paf_list.append(
#             {
#                 'pafID': PAF.get_string_version(obj, obj.pafID),
#                 'position': PAF.get_string_version(obj, obj.position),
#                 'dateOfHire': PAF.get_string_version(obj, obj.dateOfHire),
#                 'emp_firstName': PAF.get_string_version(obj, obj.emp_firstName),
#                 'emp_lastName': PAF.get_string_version(obj, obj.emp_lastName),
#                 'emp_middleName': PAF.get_string_version(obj, obj.emp_middleName),
#                 'department': PAF.get_string_version(obj, obj.department),
#                 'emp_otherName': PAF.get_string_version(obj, obj.emp_otherName),
#                 'emp_email': PAF.get_string_version(obj, obj.emp_email),
#                 'emp_phone': PAF.get_string_version(obj, obj.emp_phone),
#                 'emp_homeAddress': PAF.get_string_version(obj, obj.emp_homeAddress),
#                 'unit': PAF.get_string_version(obj, obj.unit),
#                 'actionType': PAF.get_string_version(obj, obj.actionType),
#                 'employmentType': PAF.get_string_version(obj, obj.employmentType),
#                 'salary_from': PAF.get_string_version(obj, obj.salary_from),
#                 'salary_to': PAF.get_string_version(obj, obj.salary_to),
#                 'salary_changeCode': PAF.get_string_version(obj, obj.salary_changeCode),
#                 'salary_changePercent': PAF.get_string_version(obj, obj.salary_changePercent),
#                 'salary_effectiveDate': PAF.get_string_version(obj, obj.salary_effectiveDate),
#             }
#         )
#     return paf_list
#
#
# '''
# This function returns a dictionary that represents PAFAuthorizor objects. It gets
# It it used to help compare values with PAF objects who go through the get_PAF_as_Dictionary function
# Author: Corrina Barr
# :param id: used to decide which PAFAuthoizor object to get. It is the pafID of the object you want.
# :param sig_num: used to decide which PAFAuthorizor object to get. It is the signature_number of the object you want.
# :return: returns a dictionary that represents a PAFAuthorizor object
# '''
#
#
# def get_PAFAuthorizors_as_dictionary(id, sig_num):
#     try:
#         obj = PAFAuthorizer.objects.get(pafID=id, signature_number=sig_num)
#     except:
#         print("PAF Authorizor Object with PAF id " + str(id) + " and signature number " + str(
#             sig_num) + " does not exist")
#         return {}
#
#     signature_dictionary = {
#         'pafID': PAF.get_string_version(obj, obj.pafID),
#         'fullName': PAF.get_string_version(obj, obj.fullName),
#         'signature_number': PAF.get_string_version(obj, obj.signature_number),
#         'dateSigned': PAF.get_string_version(obj, obj.dateSigned)
#     }
#
#     return signature_dictionary
#
#
# '''
# This function returns a dictionary that represents a PAF object.
# It it used to help compare values with PAF objects who go through the get_PAFAuthorizor_as_dictionary function
# Author: Corrina Barr
# :param id: used to decide which PAF object to get. It is the pafID of the object you want.
# :return: returns a dictionary that represents a PAF object
# '''
#
#
# def get_PAF_as_dictionary(id):
#     try:
#         obj = PAF.objects.get(pafID=id)
#     except:
#         print("PAF Object " + str(id) + " does not exist")
#         return {}
#     # Necessary Fields
#     paf_dictionary = {
#         'pafID': PAF.get_string_version(obj, obj.pafID),
#         'position': PAF.get_string_version(obj, obj.position),
#         'dateOfHire': PAF.get_string_version(obj, obj.dateOfHire),
#         'emp_firstName': PAF.get_string_version(obj, obj.emp_firstName),
#         'emp_lastName': PAF.get_string_version(obj, obj.emp_lastName),
#         'emp_middleName': PAF.get_string_version(obj, obj.emp_middleName),
#         'department': PAF.get_string_version(obj, obj.department),
#         'emp_otherName': PAF.get_string_version(obj, obj.emp_otherName),
#         'emp_email': PAF.get_string_version(obj, obj.emp_email),
#         'emp_phone': PAF.get_string_version(obj, obj.emp_phone),
#         'emp_homeAddress': PAF.get_string_version(obj, obj.emp_homeAddress),
#         'unit': PAF.get_string_version(obj, obj.unit),
#         'actionType': PAF.get_string_version(obj, obj.actionType),
#         'employmentType': PAF.get_string_version(obj, obj.employmentType),
#         'salary_from': PAF.get_string_version(obj, obj.salary_from),
#         'salary_to': PAF.get_string_version(obj, obj.salary_to),
#         'salary_changeCode': PAF.get_string_version(obj, obj.salary_changeCode),
#         'salary_changePercent': PAF.get_string_version(obj, obj.salary_changePercent),
#         'salary_effectiveDate': PAF.get_string_version(obj, obj.salary_effectiveDate),
#     }
#     # Optional fields
#     try:
#         paf_dictionary.update({'relocationPackage': PAF.get_string_version(obj, obj.relocationPackage)})
#     except:
#         paf_dictionary.update({'relocationPackage': ''})
#     try:
#         paf_dictionary.update({'comments': PAF.get_string_version(obj, obj.comments)})
#     except:
#         paf_dictionary.update({'comments': ''})
#
#     return paf_dictionary
#
#
# '''
# This function returns a dictionary that represents a PAFChecklist object.
# It it used to help compare values with other objects of different classes that have been converted to dictionaries
# Author: Corrina Barr
# :param id: used to decide which PAFChecklist object to get. It is the pafID of the object you want.
# :return: returns a dictionary that represents a PAF object
# '''
#
#
# def get_PAFChecklist_as_dictionary(id):
#     try:
#         obj = PAF.objects.get(pafID=id)
#     except:
#         print("PAF Checklist Object " + str(id) + " does not exist")
#         return {}
#     # Necessary Fields
#     paf_checklist_dictionary = {
#         'pafID': PAFChecklist.get_string_version(obj, obj.pafID),
#         'docsToHR': PAFChecklist.get_string_version(obj, obj.docsToHR),
#         'backgroundCheck': PAFChecklist.get_string_version(obj, obj.backgroundCheck),
#         'drugScreen': PAFChecklist.get_string_version(obj, obj.drugScreen),
#         'personnelFile': PAFChecklist.get_string_version(obj, obj.personnelFile),
#         'ITSetup': PAFChecklist.get_string_version(obj, obj.ITSetup),
#         'firstDayInfo': PAFChecklist.get_string_version(obj, obj.firstDayInfo),
#         'allHandsRoom': PAFChecklist.get_string_version(obj, obj.allHandsRoom),
#         'scheduleSpeakers': PAFChecklist.get_string_version(obj, obj.scheduleSpeakers),
#         'emailNHOOutline': PAFChecklist.get_string_version(obj, obj.emailNHOOutline),
#         'conductOrientation': PAFChecklist.get_string_version(obj, obj.conductOrientation),
#         'collectHirePacket': PAFChecklist.get_string_version(obj, obj.collectHirePacket),
#         'collectI9Form': PAFChecklist.get_string_version(obj, obj.collectI9Form),
#         'collectBenefitForm': PAFChecklist.get_string_version(obj, obj.collectBenefitForm),
#         'createBadges': PAFChecklist.get_string_version(obj, obj.createBadges),
#         'assignWorkstation': PAFChecklist.get_string_version(obj, obj.assignWorkStation),
#         'processEVerify': PAFChecklist.get_string_version(obj, obj.processEVerify),
#         'createAdpAccount': PAFChecklist.get_string_version(obj, obj.createAdpAccount),
#         'adpAccessGuide': PAFChecklist.get_string_version(obj, obj.adpAccessGuide),
#         'benefitFormToAJG': PAFChecklist.get_string_version(obj, obj.benefitFormToAJG),
#         'auditPersonnel': PAFChecklist.get_string_version(obj, obj.auditPersonnel),
#     }
#
#     return paf_checklist_dictionary


# '''
# This function returns a dictionary that represents an EmployeeUser object.
# It it used to help compare values with other objects of different classes that have been converted to dictionaries
# Author: Corrina Barr
# :param id: used to decide which EmployeeUser object to get. It is the userID of the user you want.
# :return: returns a dictionary that represents an EmployeeUser object
# '''
#
#
# def get_EmployeeUser_as_dictionary(id):
#     try:
#         obj = EmployeeUser.objects.get(user=id)
#     except:
#         print("Empoyee User Object with User ID " + str(id) + " does not exist")
#         return {}
#     # Necessary Fields
#     paf_employeeUser_dictionary = {
#         'user': EmployeeUser.get_string_version(obj, obj.user),
#         'role': EmployeeUser.get_string_version(obj, obj.role),
#         'id': EmployeeUser.get_string_version(obj, obj.id),
#     }
#
#     return paf_employeeUser_dictionary
#
#
# # endregion
#
# # # endregion
# #
# #
# # # region Other Functions
#
# '''
# This function sends an email
# Author: Corrina Barr
# :param request: the webpage request
# :param subject: subject of email
# :param message: content/message of email
# :param recipient_list: list of recipient's emails
# :return: has no return statement
# '''
#
#
# def email(request, subject, message, recipient_list):
#     send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)


'''
This function takes two dates and tells you how many days apart they are
Author: Corrina Barr
:param date_one: a date or string with format YYYY-MM-DD for year, month, and date
:param date_two: a date or string with format YYYY-MM-DD for year, month, and date
:return: returns an integer that represents the how many days the dates are apart
'''


def get_difference_of_days(date_one, date_two):
    date_1_String = str(date_one)
    date_2_String = str(date_two)

    year_1 = int(date_1_String[0:4])
    year_2 = int(date_2_String[0:4])

    month_1 = int(date_1_String[5:7])
    month_2 = int(date_2_String[5:7])

    day_1 = int(date_1_String[8:10])
    day_2 = int(date_2_String[8:10])

    date_1 = datetime.date(year_1, month_1, day_1)
    date_2 = datetime.date(year_2, month_2, day_2)

    if date_1 > date_2:
        return (date_1 - date_2).days
    else:
        return (date_2 - date_1).days


'''
Tells if a day has already happened or not

Author: Corrina Barr
:param date: a date or string with format YYYY-MM-DD for year, month, and date
:return: returns true if the day has happened yet. returns false if it has not.
'''


def check_if_day_has_happened_yet(the_date):
    date_1_String = str(the_date)
    today_String = str(datetime.datetime.now())

    year_1 = int(date_1_String[0:4])
    year_today = int(today_String[0:4])

    month_1 = int(date_1_String[5:7])
    month_today = int(today_String[5:7])

    day_1 = int(date_1_String[8:10])
    day_today = int(today_String[8:10])

    date_1 = datetime.date(year_1, month_1, day_1)
    today = datetime.date(year_today, month_today, day_today)

    if date_1 > today:
        return False
    else:
        return True


'''
This function takes takes all alphabet characters out of a string and returns the string as an integer
Author: Corrina Barr
:param the_string: the string that will have all the alphabet charcters taken out of it
:return: returns an integer that has all the numbers in the string
'''


def remove_non_integers(the_string):
    the_number = ''
    try:
        for character in the_string:
            char = str(character)
            if char.isdigit():
                the_number += char
            if char == '.':
                return int(the_number)
        if the_number != '':
            return int(the_number)
        else:
            return 0
    except:
        return None

# endregion
