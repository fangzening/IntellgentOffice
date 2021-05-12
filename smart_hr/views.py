from django.shortcuts import *
# from smart_hr.custom_functions import *
from office_app.views import *
from office_app.models import *
from smart_hr.custom_functions import *
from smart_hr.models import PAF

"""
    This function renders the index page and checks if someone is logged in
    :param request: contains http data
    :return: renders html pages
"""

def index(request):
    # return HttpResponse('SO' + str(1).zfill(5))
    if request.user.is_authenticated:
        return render(request, 'smart_hr/index.html', {'user': request.user})
    else:
        return redirect('login')


"""
    This function renders the paf page
    Written by: Zaawar Ejaz
    :param request: contains http data
    :return: renders html pages
"""


def paf_create(request):
    if request.user.is_authenticated:

        departments = []
        for dept in CostCenter.objects.order_by('costCenterName'):
            departments.append(dept.costCenterName)

        units = []
        for unit in BusinessUnit.objects.order_by('buName'):
            units.append(unit.buName)

        positions = []
        for pos in Role.objects.order_by('title'):
            positions.append(pos.title)

        approvers = []
        for employee in Employee.objects.distinct('firstName', 'middleName', 'lastName', 'associateID').order_by('firstName', 'middleName', 'lastName'):
            if employee.middleName == "" or employee.middleName is None:
                approvers.append(str(employee.firstName) + " " + str(employee.lastName))
            else:
                approvers.append(str(employee.firstName) + " " + str(employee.middleName) + " " + str(employee.lastName))

        hr = []
        for employee in Employee.objects.distinct('firstName', 'middleName', 'lastName', 'associateID').order_by(
                'firstName', 'middleName', 'lastName').filter(employeedepartment__departmentID__costCenterCode="EFISPHR07"):
            if employee.middleName == "" or employee.middleName is None:
                hr.append(str(employee.firstName) + " " + str(employee.lastName))
            else:
                hr.append(str(employee.firstName) + " " + str(employee.middleName) + " " + str(employee.lastName))

        if request.method == 'POST':
            response = post_PAF(request)
            if response:
                response.set_cookie("file_received", "true")
                return response
            elif messages:
                return render(request, 'smart_hr/paf_create.html', {'form': request.POST,
                                                                    'departments': departments,
                                                                    'units': units,
                                                                    'positions': positions,
                                                                    'approvers': approvers,
                                                                    'hr': hr,
                                                                    'is_manager': request.session['is_manager']})
            else:
                return redirect('paf_create')

        return render(request, 'smart_hr/paf_create.html', {'departments': departments,
                                                            'units': units,
                                                            'positions': positions,
                                                            'approvers': approvers,
                                                            'hr': hr,
                                                            'is_manager': request.session['is_manager']})
    else:
        return redirect('login')


""" 
    This function renders the paf listing page
    Written by: Zaawar Ejaz
    :param request: contains http data
    :return: renders html pages
"""


def paf_list(request):
    if request.user.is_authenticated:
        return render(request, 'smart_hr/paf_list.html', {'is_manager': request.session['is_manager']})
    else:
        return redirect('login')


"""
    This function returns all paf in json format
    Written by: Zaawar Ejaz
    :param request: contains http data
    :return: renders html pages

"""


def paf_json(request):
    if request.user.is_authenticated:
        return JsonResponse(PAF.get_all_paf(str(request.session['user_id'])))
    else:
        return redirect('login')


"""
    This function renders the checklist listing page
    Written by: Zaawar Ejaz
    :param request: contains http data
    :return: renders html pages
"""

def checklist_create(request):
    if request.user.is_authenticated:

        # if 'create_checklist' not in request.session.get('user_perm'):
        #     return HttpResponseForbidden(render(request, '403_error.html'))

        departments = []
        for dept in CostCenter.objects.order_by('costCenterName'):
            departments.append({"label": dept.costCenterName, "value": dept.costCenterCode})

        units = []
        for unit in BusinessUnit.objects.order_by('buName'):
            units.append({"label": unit.buName, "value": unit.buName})

        positions = []
        for pos in Role.objects.order_by('title'):
            positions.append({"label": pos.title, "value": pos.roleID})

        managers = []
        for department in CostCenter.objects.distinct('managedBy__firstName', 'managedBy__lastName',
                                                      'managedBy__associateID').order_by('managedBy__firstName',
                                                                                        'managedBy__lastName'):
            if department.managedBy is not None:
                manager = department.managedBy
                managers.append({"label": manager.firstName + " " + manager.lastName, "value": manager.associateID})

        employees = []
        for employee in EmployeeDepartment.objects.distinct('associateID__firstName', 'associateID__lastName', 'associateID').order_by('associateID__firstName', 'associateID__lastName'):
            try:
                employees.append({"label": employee.associateID.firstName + " " + employee.associateID.lastName, "value": employee.associateID.associateID, "department": employee.departmentID.costCenterCode})
            except AttributeError:
                print("Attribute Error (NoneType) - Smart HR Checklist")
                continue

        if request.method == "POST":
            if create_checklist(request):
                return redirect('checklist_list')
            else:
                return render(request, 'smart_hr/checklist_create.html', {'form': request.POST,
                                                                          'user': request.user,
                                                                          'checklist_tasks': ChecklistTask.objects.filter(status=True),
                                                                          'units': units,
                                                                          'departments': departments,
                                                                          'managers': managers,
                                                                          'positions': positions,
                                                                          'employees': employees })

        return render(request, 'smart_hr/checklist_create.html', {'user': request.user,
                                                                  'checklist_tasks': ChecklistTask.objects.filter(status=True),
                                                                  'units': units,
                                                                  'departments': departments,
                                                                  'managers': managers,
                                                                  'positions': positions,
                                                                  'employees': employees})
    else:
        return redirect('login')


def checklist_list(request):
    if request.user.is_authenticated:
        return render(request, 'smart_hr/checklist_list.html', {'user': request.user,
                                                                'is_manager': request.session['is_manager']})
    else:
        return redirect('login')


"""
    This function renders the checklist page and checks if user is logged in
    :param request: contains ht data
    :return: renders html pages, also passes today's date, 
    and lists that hold dictionaries that represent PAF and PAFAuthorizor objects
    for the template to use
"""


def checklist_detail(request, empID):
    if request.user.is_authenticated:

        try:
            employee = Employee.objects.get(associateID=empID)
            empdept = EmployeeDepartment.objects.get(associateID=empID)
        except:
            return render(request, 'office_app/../office_app/templates/404.html')

        if request.method == "POST":
            if update_checklist(request, employee):
                return redirect('../checklist_detail/' + str(empID))
            else:
                return redirect(request.path)

        if "view_all_checklist" in request.session['user_perm']:
            checklist = NewHireChecklist.objects.filter(empID=employee).order_by("taskID")
        else:
            checklist = NewHireChecklist.objects.filter(empID=employee, taskAssignee=request.session['user_id']).order_by(
                "taskID")

        all_checked = True
        for task in checklist:
            if task.completed is False:
                all_checked = False
                break

        return render(request, 'smart_hr/checklist_detail.html', {'user': request.user,
                                                                  'employee':employee,
                                                                  'empdept': empdept,
                                                                  'checklist': checklist,
                                                                  'today': datetime.today().date(),
                                                                  'all_checked': all_checked})
    else:
        return redirect('login')


def checklist_edit(request, empID):
    if request.user.is_authenticated:
        # if 'edit_checklist' not in request.session.get('user_perm'):
        #     return HttpResponseForbidden(render(request, 'office_app/403_error.html'))

        try:
            employee = Employee.objects.get(associateID=empID)
            empdept = EmployeeDepartment.objects.get(associateID=empID)
        except:
            return render(request, 'office_app/../office_app/templates/404.html')

        checklist = NewHireChecklist.objects.filter(empID=empID).order_by("taskID")

        employees = []
        for emp in EmployeeDepartment.objects.distinct('associateID__firstName', 'associateID__lastName',
                                                            'associateID').order_by('associateID__firstName',
                                                                                   'associateID__lastName'):
            try:
                employees.append({"label": emp.associateID.firstName + " " + emp.associateID.lastName,
                                  "value": emp.associateID.associateID,
                                  "department": emp.departmentID.costCenterCode})

            except AttributeError:
                print("AAttributeError when getting checklist detail")
                continue

        if request.method == "POST":
            if edit_checklist(request, employee):
                return redirect('../checklist_detail/' + str(empID))
            else:
                return redirect(request.path)

        return render(request, 'smart_hr/checklist_edit.html', {'user': request.user,
                                                                'employee': employee,
                                                                'employees': employees,
                                                                'empdept': empdept,
                                                                'checklist': checklist,
                                                                'today': datetime.today().date()})
    else:
        return redirect('login')


"""
    This function returns all checklist in json format
    Written by: Zaawar Ejaz
    :param request: contains http data
    :return: renders html pages
"""


def checklist_json(request):
    if request.user.is_authenticated:
        return JsonResponse(NewHireChecklist.get_assigned_checklist(request.session['user_id']))
    else:
        return redirect('login')




