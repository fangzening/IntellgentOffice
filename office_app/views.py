from django.forms import model_to_dict
from django.shortcuts import *
from django.contrib.auth.signals import user_logged_in
from django.utils.html import strip_tags

from goods_received.models import *
from it_app.models import UserPasswordChange
from office_app.services import EmailHandler
from office_app.vendor_functions import *
from purchase.models import *
from travel.send_daily_email_reminder import *
# from it_app.models import UserPasswordChange
from .sessions import set_session


# OCR
import pytesseract
import cv2

# Set session upon successful login
user_logged_in.connect(set_session)

user_creation_allowed_departments = ['Supporting - IT', 'Supporting - HR']

#################### ADMIN PAGE VIEWS START ####################
#################### WRITTEN BY ZAAWAR EJAZ ####################



'''
    View template for REST Operation
    Written by: Zaawar Ejaz
    :param request: http header or uri data
    :param return: json or http responses
'''

# def view_name(request):
#     if request.user.is_authenticated:
#         try:
#             if request.method == "GET":
#                 return JsonResponse({})
#
#             if request.method == "POST":
#                 return HttpResponse('Added')
#
#             if (request.method == "PUT"):
#                 return HttpResponse('Updated')
#
#             if (request.method == "DELETE"):
#                 return HttpResponse('Deleted')
#
#             else:
#                 return HttpResponseBadRequest('Invalid REST Request')
#         except:
#             print('\n'.join(traceback.format_exception(*sys.exc_info())))
#             return HttpResponseServerError('Server Error. Please Contact IT Support')
#     else:
#         return redirect('login')


def admin_dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'office_app/admin/dashboard.html')
    else:
        return redirect('login')


def account(request):
    if request.user.is_authenticated and request.user.is_superuser:
        employees = Employee.objects.all().order_by('associateID')
        return render(request, 'office_app/admin/account.html', {'employees': employees})
    else:
        return redirect('login')


def account_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == "GET":
                accounts = []
                for account in Account.objects.all():
                    dict = model_to_dict(account)
                    del dict['password']
                    accounts.append(dict)
                return JsonResponse({'accounts': accounts})

            if request.method == "POST":
                data = json.loads(request.POST.get('data'))

                if Account.objects.filter(employee=data['associate_id']).exists():
                    return HttpResponse('Account Already Exists', status=409)

                account = Account()
                account.employee = Employee.objects.get(associateID=data['associate_id'])
                account.email = data['username']
                account.set_password(data['password'])
                account.is_active = data['active']
                account.is_staff = data['staff']
                account.is_superuser = data['superuser']
                account.save()

                return HttpResponse('Account Added')

            if request.method == "PUT":
                if request.GET['request_type'] == 'authorize_pwdchange':
                    account = Account.objects.get(employee=request.GET.get('associateID'))
                    error_messages = UserPasswordChange.approve_change_request(approved_user=account)

                    for error in error_messages['other_errors']:
                        messages.error(request, error)

                    return HttpResponse('Password Changed Request Authorized')

                else:
                    if request.GET.get('associateID') == 'administrator':
                        return HttpResponseForbidden('Administrator Account Cannot Be Modified')

                    print(request.GET.get('data'))
                    data = json.loads(request.GET.get('data'))
                    account = Account.objects.get(employee=data['associate_id'])
                    account.is_active = data['active']
                    account.is_staff = data['staff']
                    account.is_superuser = data['superuser']
                    account.save()

                    return HttpResponse('Account Modified')

            if request.method == "DELETE":
                if request.GET.get('associateID') == 'administrator':
                    return HttpResponseForbidden('Administrator Account Cannot Be Deleted')

                Account.objects.get(employee=request.GET.get('associateID')).delete()
                return HttpResponse('Account Deleted')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')
    else:
        return redirect('login')


def employee(request):
    if request.user.is_authenticated and request.user.is_superuser:
        employees = Employee.objects.all().order_by('associateID')
        departments = CostCenter.objects.all().order_by('costCenterName')
        roles = Role.objects.all().order_by('title')

        return render(request, 'office_app/admin/employee.html', {'employees': employees,
                                                                  'departments': departments,
                                                                  'roles': roles})
    else:
        return redirect('login')


def employee_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == "GET":
                employees = []
                for employee in Employee.objects.all():
                    employees.append(model_to_dict(employee))

                return JsonResponse({'employees': employees})

            if request.method == "POST":
                data = json.loads(request.POST.get('data'))

                if Employee.objects.filter(firstName=data['firstname'], lastName=data['lastname'], email=data['primaryemail']).exists():
                    return HttpResponse('Employee Already Exists', status=409)

                employee = Employee()
                employeedepartment = EmployeeDepartment()
                employee.firstName = data['firstname']
                employee.middleName = data['middlename']
                employee.lastName = data['lastname']
                employee.otherName = data['preferredname']
                employee.email = data['primaryemail']
                employee.secondaryEmail = data['secondaryemail']
                if data['dateofhire'] not in ["", None]:
                    employee.doh = data['dateofhire']
                employee.mainPhone = data['primaryphone']
                employee.otherPhone = data['secondaryphone']
                employee.city = data['city']
                employee.country = data['country']
                employee.title = data['jobtitle']
                employee.reportsToGM = data['reportstogm']

                employeedepartment.associateID = employee
                employeedepartment.departmentID = CostCenter.objects.get(costCenterCode=data['department'])
                if data['role'] not in ["", None]:
                    employeedepartment.roleID = Role.objects.get(roleID=data['role'])
                if data['joiningdate'] not in ["", None]:
                    employeedepartment.joiningDate = data['joiningdate']
                if data['leavingdate'] not in ["", None]:
                    employeedepartment.leavingDate = data['leavingdate']

                employee.save()
                employeedepartment.save()

                return HttpResponse('Employee Added')

            if request.method == "PUT":

                if request.GET.get('associate_id') == 'administrator':
                    return HttpResponseForbidden('Administrator Cannot Be Modified')

                data = json.loads(request.GET.get('data'))

                employee = Employee.objects.get(associateID=data['associate_id'])
                employee.firstName = data['firstname']
                employee.middleName = data['middlename']
                employee.lastName = data['lastname']
                employee.otherName = data['preferredname']
                employee.email = data['primaryemail']
                employee.secondaryEmail = data['secondaryemail']
                employee.doh = data['dateofhire']
                employee.mainPhone = data['primaryphone']
                employee.otherPhone = data['secondaryphone']
                employee.city = data['city']
                employee.country = data['country']
                employee.title = data['jobtitle']
                employee.reportsToGM = data['reportstogm']
                employee.save()

                return HttpResponse('Account Modified')

            if request.method == "DELETE":
                if request.GET.get('associateID') == 'administrator':
                    return HttpResponseForbidden('Administrator Account Cannot Be Deleted')

                Employee.objects.get(associateID=request.GET.get('associateID')).delete()
                return HttpResponse('Employee Deleted')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')
    else:
        return redirect('login')


def costcenter(request):
    if request.user.is_authenticated and request.user.is_superuser:
        businessunits = BusinessUnit.objects.all().order_by('buName')
        employees = Employee.objects.all().order_by('firstName', 'lastName')
        return render(request, 'office_app/admin/costcenter.html', {'businessunits': businessunits,
                                                                    'employees': employees})
    else:
        return redirect('login')


def costcenter_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == "GET":
                costcenters = []
                for costcenter in CostCenter.objects.all():
                    costcenters.append({
                        'costCenterCode': costcenter.costCenterCode,
                        'costCenterName': costcenter.costCenterName,
                        'businessUnit': costcenter.businessUnit.buName if costcenter.businessUnit else "",
                        'managedBy': costcenter.managedBy.full_name if costcenter.managedBy else "",
                        'accountant': costcenter.accountant.full_name if costcenter.accountant else "",
                        'costManager': costcenter.costManager.full_name if costcenter.costManager else ""
                    })

                businessunits = []
                for businessunit in BusinessUnit.objects.values('buName'):
                    businessunits.append(businessunit)

                employees = []
                for employee in Employee.objects.all():
                    employees.append({
                        'associate_id': employee.associateID,
                        'name': employee.full_name,
                    })

                return JsonResponse({'costcenters': costcenters,
                                     'businessunits': businessunits,
                                     'employees': employees})

            if request.method == "POST":
                data = json.loads(request.POST.get('data'))

                if CostCenter.objects.filter(costCenterName=data['costcentername']).exists() or CostCenter.objects.filter(costCenterCode=data['costcentercode']).exists():
                    return HttpResponse('Cost Center Already Exists', status=409)

                costcenter = CostCenter()
                costcenter.costCenterCode = data['costcentercode']
                costcenter.costCenterName = data['costcentername']
                costcenter.businessUnit = BusinessUnit.objects.get(buName=data['businessunit'])
                costcenter.costManager = Employee.objects.get(associateID=data['costmanager'])
                costcenter.accountant = Employee.objects.get(associateID=data['accountant'])
                costcenter.managedBy = Employee.objects.get(associateID=data['manager'])
                costcenter.save()

                return HttpResponse('Cost Center Added')

            if request.method == "PUT":
                data = json.loads(request.GET.get('data'))
                costcenter = CostCenter.objects.get(costCenterCode=data['costcentercode'])
                costcenter.costCenterName = data['costcentername']
                costcenter.businessUnit = BusinessUnit.objects.get(buName=data['businessunit'])
                costcenter.costManager = Employee.objects.get(associateID=data['costmanager'])
                costcenter.accountant = Employee.objects.get(associateID=data['accountant'])
                costcenter.managedBy = Employee.objects.get(associateID=data['manager'])
                costcenter.save()

                return HttpResponse('Account Modified')

            if request.method == "DELETE":
                CostCenter.objects.get(costCenterCode=request.GET.get('costCenterCode')).delete()
                return HttpResponse('Cost Center Deleted')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')
    else:
        return redirect('login')


def businessunit(request):
    if request.user.is_authenticated and request.user.is_superuser:
        businessgroups = BusinessGroup.objects.all().order_by('name')
        employees = Employee.objects.all().order_by('firstName', 'lastName')
        return render(request, 'office_app/admin/businessunit.html', {'businessgroups': businessgroups,
                                                                    'employees': employees})
    else:
        return redirect('login')


def businessunit_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == "GET":
                businessunits = []
                for businessunit in BusinessUnit.objects.all():
                    businessunits.append({
                        'businessUnit': businessunit.buName,
                        # 'plantCode': businessunit.plantCode,
                        'businessGroup': businessunit.businessGroup.name if businessunit.businessGroup else "",
                        'managedBy': businessunit.managedBy.full_name if businessunit.managedBy else "",
                        'buBuyer': businessunit.buBuyer.full_name if businessunit.buBuyer else "",
                        'costManager': businessunit.costManager.full_name if businessunit.costManager else ""
                    })

                businessgroups = []
                for businessgroup in BusinessGroup.objects.values('name'):
                    businessgroups.append(businessgroup)

                employees = []
                for employee in Employee.objects.all():
                    employees.append({
                        'associate_id': employee.associateID,
                        'name': employee.full_name,
                    })

                return JsonResponse({'businessunits': businessunits,
                                     'businessgroups': businessgroups,
                                     'employees': employees})

            if request.method == "POST":
                data = json.loads(request.POST.get('data'))

                if BusinessUnit.objects.filter(buName=data['buname']).exists():
                    return HttpResponse('Business Unit Already Exists', status=409)

                businessunit = BusinessUnit()
                businessunit.buName = data['buname']
                businessunit.businessGroup = BusinessGroup.objects.get(name=data['businessgroup'])
                # businessunit.plantCode = data['plantcode']
                businessunit.costManager = Employee.objects.get(associateID=data['costmanager'])
                businessunit.buBuyer = Employee.objects.get(associateID=data['bubuyer'])
                businessunit.managedBy = Employee.objects.get(associateID=data['manager'])
                businessunit.save()

                return HttpResponse('Business Unit Added')

            if request.method == "PUT":
                data = json.loads(request.GET.get('data'))

                print(data)

                businessunit = BusinessUnit.objects.get(buName=data['buname'])
                businessunit.businessGroup = BusinessGroup.objects.get(name=data['businessgroup'])
                # businessunit.plantCode = data['plantcode']
                businessunit.costManager = Employee.objects.get(associateID=data['costmanager'])
                businessunit.buBuyer = Employee.objects.get(associateID=data['bubuyer'])
                businessunit.managedBy = Employee.objects.get(associateID=data['manager'])
                businessunit.save()

                return HttpResponse('Business Unit Modified')

            if request.method == "DELETE":
                BusinessUnit.objects.get(buName=request.GET.get('businessunit')).delete()
                return HttpResponse('Business Unit Deleted')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')
    else:
        return redirect('login')


def businessgroup(request):
    if request.user.is_authenticated and request.user.is_superuser:
        legalentities = LegalEntity.objects.all().order_by('entityName')
        employees = Employee.objects.all().order_by('firstName', 'lastName')
        return render(request, 'office_app/admin/businessgroup.html', {'legalentities': legalentities,
                                                                    'employees': employees})
    else:
        return redirect('login')


def businessgroup_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == "GET":
                businessgroups = []
                for businessgroup in BusinessGroup.objects.all():
                    businessgroups.append({
                        'businessGroup': businessgroup.name,
                        'generalManager': businessgroup.generalManager.full_name if businessgroup.generalManager else "",
                        'costManager': businessgroup.costManager.full_name if businessgroup.costManager else "",
                        'legalEntity': businessgroup.legalEntity.entityName
                    })

                legalentities = []
                for legalentity in LegalEntity.objects.values('entityName'):
                    legalentities.append(legalentity)

                employees = []
                for employee in Employee.objects.all():
                    employees.append({
                        'associate_id': employee.associateID,
                        'name': employee.full_name,
                    })

                return JsonResponse({'businessgroups': businessgroups,
                                     'legalentities': legalentities,
                                     'employees': employees})

            if request.method == "POST":
                data = json.loads(request.POST.get('data'))

                if BusinessGroup.objects.filter(name=data['bgname']).exists():
                    return HttpResponse('Business Group Already Exists', status=409)

                businessgroup = BusinessGroup()
                businessgroup.name = data['bgname']
                businessgroup.legalEntity = LegalEntity.objects.get(entityName=data['legalentity'])
                businessgroup.costManager = Employee.objects.get(associateID=data['costmanager'])
                businessgroup.generalManager = Employee.objects.get(associateID=data['generalmanager'])
                businessgroup.save()

                return HttpResponse('Business Group Added')

            if request.method == "PUT":
                data = json.loads(request.GET.get('data'))

                businessgroup = BusinessGroup(name=data['bgname'])
                businessgroup.legalEntity = LegalEntity.objects.get(entityName=data['legalentity'])
                businessgroup.costManager = Employee.objects.get(associateID=data['costmanager'])
                businessgroup.generalManager = Employee.objects.get(associateID=data['generalmanager'])
                businessgroup.save()

                return HttpResponse('Business Group Modified')

            if request.method == "DELETE":
                BusinessGroup.objects.get(name=request.GET.get('bgname')).delete()
                return HttpResponse('Business Group Deleted')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')
    else:
        return redirect('login')

def legalentity(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'office_app/admin/legalentity.html')
    else:
        return redirect('login')


def legalentity_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == "GET":
                legalentities = []
                for legalentity in LegalEntity.objects.all():
                    legalentities.append(model_to_dict(legalentity))

                return JsonResponse({'legalentities': legalentities})

            if request.method == "POST":
                data = json.loads(request.POST.get('data'))

                if LegalEntity.objects.filter(entityName=data['legalentity']).exists():
                    return HttpResponse('Legal Entity Already Exists', status=409)

                legalentity = LegalEntity()
                legalentity.entityName = data['legalentity']
                legalentity.sapCompCode = data['sapcompcode']
                legalentity.save()

                return HttpResponse('Legal Entity Added')

            if request.method == "PUT":
                data = json.loads(request.GET.get('data'))

                legalentity = LegalEntity.objects.get(entityName=data['legalentity'])
                legalentity.sapCompCode = data['sapcompcode']
                legalentity.save()

                return HttpResponse('Legal Entity Modified')

            if request.method == "DELETE":
                LegalEntity.objects.get(entityName=request.GET.get('legalentity')).delete()
                return HttpResponse('Legal Entity Deleted')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')
    else:
        return redirect('login')


def approver(request):
    if request.user.is_authenticated and request.user.is_superuser:
        roles = Role.objects.all()
        return render(request, 'office_app/admin/approver.html', {'roles': roles})
    else:
        return redirect('login')


def approver_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == "GET":
                approvers = []
                for approver in ProcessApprover.objects.all():
                    approvers.append({
                        'id': approver.id,
                        'approver': approver.approverRole.title
                    })
                return JsonResponse({'approvers': approvers})

            if request.method == "POST":
                role_id = request.POST.get('role_id')
                if (ProcessApprover.objects.filter(approverRole__roleID=role_id).exists()):
                    return HttpResponse('Approver Already Exists', status=409)

                ProcessApprover(approverRole=Role.objects.get(roleID=role_id)).save()
                return HttpResponse('Success')

            if request.method == "DELETE":
                approver = ProcessApprover.objects.get(id=request.GET.get('approver_id'))
                approver.delete()
                return HttpResponse('Success')

            else:
                return HttpResponseBadRequest('Invalid REST Request')

        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')

    else:
        return redirect('login')


def combination(request):
    # This view shows the Event_Bugdet.html page:
    if request.user.is_authenticated and request.user.is_superuser:
        processTypes = ProcessType.objects.all()
        businessUnits = BusinessUnit.objects.all()
        form_true_names = EmailHandler.form_true_name

        forms = []

        for form_short in form_true_names.keys():
            forms.append([form_short, form_true_names[form_short]])

        return render(request, 'office_app/admin/combination.html', {'processTypes': processTypes,
                                                                     'businessUnits': businessUnits,
                                                                     'forms': forms})
    else:
        return redirect('login')


def combination_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == "GET":
                combinations = []
                for combination in Combination.objects.all():
                    combinations.append(model_to_dict(combination))
                return JsonResponse({'combinations': combinations})

            if request.method == "POST":
                print("all post data: " + str(dict(request.POST)))
                if Combination.objects.filter(buName=request.POST.get('buName'),
                                              formType=request.POST.get('formType')).exists():
                    return HttpResponse('Combination Already Exists', status=409)

                combination = Combination()
                combination.formType = request.POST.get('formType')
                if request.POST.get('buName') != 'Default':
                    combination.buName = BusinessUnit.objects.get(buName=request.POST.get('buName'))
                # combination.reportsToGM = (request.POST['reportsToGM']).capitalize()
                combination.processType = ProcessType.objects.get(processCode=request.POST.get('processType'))

                if request.POST.get('reportsToGM') == 'true':
                    combination.reportsToGM = True
                else:
                    combination.reportsToGM = False

                print(f"Reports to GM: {request.POST.get('reportsToGM')} \nCombo reports: {combination.reportsToGM}")

                combination.save()
                return HttpResponse('Combination Added')

            if (request.method == "DELETE"):
                Combination.objects.get(id=request.GET.get('combination_id')).delete()
                return HttpResponse('Combination Deleted')

            else:
                return HttpResponseBadRequest('Invalid REST Request')

        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')

    else:
        return redirect('login')

def approval_process(request):
    if request.user.is_authenticated and request.user.is_superuser:
        processApprovers = ProcessApprover.objects.all()
        employees = Employee.objects.all().order_by('firstName', 'lastName')
        operator_options = ['is the same as', 'is not the same as', 'is less than', 'is greater than', 'is greater than or equal to', 'is less than or equal to']

        return render(request, 'office_app/admin/approval_process.html', {'processApprovers': processApprovers,
                                                                          'formTypes': EmailHandler.form_link_list,
                                                                          'operator_options': operator_options,
                                                                          'employees': employees})
    else:
        return redirect('login')

def get_information_to_edit_approval_process(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == "POST":
            # ok so for each item i get i have to have a dictionary passed instead of the object
            js_context = ProcessType.get_context_for_editing_process(request)
            return JsonResponse({'js_context': js_context})

def approval_process_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == "GET":
                process_stages = []

                for process in ProcessType.objects.all().distinct('processCode'):
                    stages = []
                    for stage in ProcessStages.objects.filter(processType__processCode=process.processCode).order_by('stage'):
                        stages.append({
                            'stage': stage.stage,
                            'approverRoleId': stage.stageApprover.approverRole.roleID,
                            'approver': stage.stageApprover.approverRole.title
                        })

                    process_stages.append({
                        'processName': process.processCode,
                        'processDesc': process.processDescription,
                        'stages': stages
                    })

                approvers = []
                for approver in ProcessApprover.objects.all():
                    approvers.append({
                        'roleId': approver.approverRole.roleID,
                        'role': approver.approverRole.title
                    })

                return JsonResponse({'approval_process': process_stages, 'approvers': approvers})

            if request.method == "POST":
                all_post_data = dict(request.POST)
                print("all POST data: " + str(all_post_data))

                process_type = ProcessType()

                # If process name already exists, give a warning that you will be overwriting the current process
                types_with_existing_name = ProcessType.objects.filter(processCode=request.POST.get('processName'))
                if types_with_existing_name.exists():
                    if 'undefined' not in all_post_data:
                        return HttpResponse('Process Name already exists. Do you want to overwrite?', status=409) # Have to add ok and cancel button functions
                    else:
                        process_type = types_with_existing_name.first()

                process_type.create_process(request)
                return HttpResponse('Approval Process Added')

            if (request.method == "PUT"):
                stageDict = json.loads(request.GET.get('processStageApprover'))

                if not bool(stageDict):
                    return HttpResponseForbidden('At Least One Process Stages Is Required')

                processType = ProcessType.objects.get(processCode=request.GET.get('processName'))
                ProcessStages.objects.filter(processType__processCode=processType).delete()

                for stage in stageDict:
                    processStages = ProcessStages()
                    processStages.processType = processType
                    processStages.stage = stage
                    processStages.stageApprover = ProcessApprover.objects.get(approverRole__roleID=stageDict[stage])
                    processStages.save()

                return HttpResponse('Approval Process Updated')

            if (request.method == "DELETE"):
                # Change this to check to see if Combination business unit is empty. If it is, then it is a default.
                defaultAP = Combination.objects.filter(buName=None).values('processType__processCode')
                if request.GET.get('processName') in defaultAP:
                    return HttpResponseForbidden('Default Approval Process Cannot Be Deleted')

                # region deleting process and all objects accociated with it
                process_to_delete = ProcessType.objects.get(processCode=request.GET.get('processName'))
                process_stages_to_delete = ProcessStages.objects.filter(processType=process_to_delete)
                for obj in process_stages_to_delete:
                    conditions_to_delete = obj.conditions.all()
                    for cond in conditions_to_delete:
                        cond.delete()
                    obj.delete()
                process_to_delete.delete()
                # endregion

                return HttpResponse('Approval Process Deleted')
            else:
                return HttpResponseBadRequest('Invalid REST Request')

        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')

    else:
        return redirect('login')



'''
    This function renders admin process tracking page
    Written by: Zaawar Ejaz
    :param request: http data
    :param return: http responses (html page)
'''


def ta_ap_tracker(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'office_app/admin/ta_ap_tracker.html')
    else:
        return redirect('login')


def ta_ap_tracker_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == 'GET':
                if request.GET.get('request_type') == 'gantt_chart':
                    gantt_data = []
                    for form in TemporaryApprovalStage.objects.filter(formID=request.GET.get('form_id'), stage__gte=1).order_by('stage'):
                        from_date = form.dayAssigned
                        to_date = form.date
                        action_taken = form.actionTaken
                        custom_class = ""

                        if from_date is None:
                            from_date = ""
                            to_date = ""
                        else:
                            if to_date is None:
                                to_date = datetime.today()
                                if action_taken is None:
                                    action_taken = "Pending Approval"
                                    custom_class = "ganttBlue"
                            else:
                                if action_taken == "Declined":
                                    custom_class = "ganttRed"
                                elif action_taken == "Approved":
                                    custom_class = "ganttGreen"
                                else:
                                    custom_class = "ganttOrange"


                        gantt_data.append({
                            "name": "Stage " + str(form.stage),
                            "desc": form.approverID.firstName + " " + form.approverID.lastName,
                            "values": [{
                                "from": from_date,
                                "to": to_date,
                                "label": action_taken,
                                "customClass": custom_class,
                            }]
                        })
                    return JsonResponse({'gantt_data': gantt_data})

                else:
                    ta_forms = []
                    for ta_form in EmployeeInformation.objects.filter(currentStage__gte=1):
                        ta_forms.append({
                            'formID': ta_form.formID,
                            'applicant': ta_form.employee.full_name,
                            'budgetSC': CostCenter.objects.get(costCenterCode=ta_form.budgetSourceCode).costCenterName,
                            'currentStage': ta_form.currentStage,
                            'totalStages': TemporaryApprovalStage.objects.filter(formID=ta_form.formID).count(),
                            'travelType': ta_form.travelType,
                            'isApproved': ta_form.isApproved,
                            'isDeclined': ta_form.isDeclined,
                        })
                    return JsonResponse({'ta_forms': ta_forms})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')

    else:
        return redirect('login')


def tr_ap_tracker(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'office_app/admin/tr_ap_tracker.html')
    else:
        return redirect('login')


def tr_ap_tracker_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == 'GET':
                if request.GET.get('request_type') == 'gantt_chart':
                    gantt_data = []
                    for form in TRApprovalProcess.objects.filter(formID__taDetail__formID=request.GET.get('form_id'), stage__gte=1).order_by('stage'):
                        from_date = form.dayAssigned
                        to_date = form.date
                        action_taken = form.actionTaken
                        custom_class = ""

                        if from_date is None:
                            from_date = ""
                            to_date = ""
                        else:
                            if to_date is None:
                                to_date = datetime.today()
                                if action_taken is None:
                                    action_taken = "Pending Approval"
                                    custom_class = "ganttBlue"
                            else:
                                if action_taken == "Declined":
                                    custom_class = "ganttRed"
                                elif action_taken == "Approved":
                                    custom_class = "ganttGreen"
                                else:
                                    custom_class = "ganttOrange"


                        gantt_data.append({
                            "name": "Stage " + str(form.stage),
                            "desc": form.approverID.firstName + " " + form.approverID.lastName,
                            "values": [{
                                "from": from_date,
                                "to": to_date,
                                "label": action_taken,
                                "customClass": custom_class,
                            }]
                        })
                    return JsonResponse({'gantt_data': gantt_data})

                else:
                    tr_forms = []
                    for tr_form in TADetails.objects.filter(currentStage__gte=1):
                        tr_forms.append({
                            'formID': tr_form.taDetail.formID,
                            'applicant': tr_form.taDetail.employee.full_name,
                            'budgetSC': CostCenter.objects.get(costCenterCode=tr_form.taDetail.budgetSourceCode).costCenterName,
                            'currentStage': tr_form.currentStage,
                            'totalStages': TRApprovalProcess.objects.filter(formID=tr_form.taDetail.formID).count(),
                            'travelType': tr_form.taDetail.travelType,
                            'isApproved': tr_form.isApproved,
                            'isDeclined': tr_form.isDeclined,
                        })
                    return JsonResponse({'tr_forms': tr_forms})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')

    else:
        return redirect('login')

'''
    This function renders admin process tracking page for pr
    Written by: Corrina Barr (based on Zaawar Ejaz)
    :param request: http data
    :param return: http responses (html page)
'''

def pr_ap_tracker(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'office_app/admin/pr_ap_tracker.html')
    else:
        return redirect('login')


def pr_ap_tracker_api(request):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            if request.method == 'GET':
                if request.GET.get('request_type') == 'gantt_chart':
                    gantt_data = []

                    for form in PRApprovalProcess.objects.filter(formID=request.GET.get('form_id'), stage__gte=1).order_by('stage'):
                        from_date = form.dayAssigned
                        to_date = form.date
                        action_taken = form.actionTaken
                        custom_class = ""

                        if from_date is None:
                            from_date = ""
                            to_date = ""
                        else:
                            if to_date is None:
                                to_date = datetime.today()
                                if action_taken is None:
                                    action_taken = "Pending Approval"
                                    custom_class = "ganttBlue"
                            else:
                                if action_taken == "Declined":
                                    custom_class = "ganttRed"
                                elif action_taken == "Approved":
                                    custom_class = "ganttGreen"
                                else:
                                    custom_class = "ganttOrange"

                        gantt_data.append({
                            "name": "Stage " + str(form.stage),
                            "desc": form.approverID.firstName + " " + form.approverID.lastName,
                            "values": [{
                                "from": from_date,
                                "to": to_date,
                                "label": action_taken,
                                "customClass": custom_class,
                            }]
                        })
                    return JsonResponse({'gantt_data': gantt_data})

                else:
                    pr_items = []
                    for pr_item in PurchaseItemDetail.objects.filter(currentStage__gte=1):
                        supplierInfo = SupplierInfo.objects.filter(form_id=pr_item.formID).first()
                        if supplierInfo != None:
                            vendor = supplierInfo.vendor
                        else:
                            vendor = None
                        if vendor != None:
                            vendorCode = vendor.vendorCode
                        else:
                            vendorCode = None
                        pr_items.append({
                            'formID': pr_item.formID,
                            'applicant': pr_item.employee.full_name,
                            'itemID': pr_item.pk,
                            'itemDesc': pr_item.itemDesc,
                            'currentStage': pr_item.currentStage,
                            'totalStages': PRApprovalProcess.objects.filter(formID=pr_item.pk).count(),
                            'vendorCode': vendorCode,
                            'isApproved': pr_item.isApproved,
                            'isDeclined': pr_item.isDeclined,
                        })
                    return JsonResponse({'pr_items': pr_items})
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')

    else:
        return redirect('login')


def vendor(request):
    if request.user.is_authenticated:
        return render(request, 'office_app/admin/vendor.html')
    else:
        return redirect('login')


def vendor_api(request):
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                vendors = []
                for vendor in Vendors.objects.all():
                    vendors.append(model_to_dict(vendor))

                return JsonResponse({"vendors": vendors})

            if (request.method == "PUT"):
                update_vendor_list()

                return HttpResponse('Successfully Updated')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')
    else:
        return redirect('login')


def module(request):
    if request.user.is_authenticated:
        return render(request, 'office_app/admin/module.html')
    else:
        return redirect('login')


def module_api(request):
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                ModuleAccess.objects.all()
                return JsonResponse({})

            if request.method == "POST":
                return HttpResponse('Added')

            if (request.method == "PUT"):
                return HttpResponse('Updated')

            if (request.method == "DELETE"):
                return HttpResponse('Deleted')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact IT Support')
    else:
        return redirect('login')

#################### ADMIN PAGE VIEWS END ####################

'''
    This function renders dashboard page
    Written by: Zaawar Ejaz
    :param request: http data
    :param return: http responses (html page)
'''

def dashboard_view(request):
    if request.user.is_authenticated:
        context = {}
        try:
            if request.user.check_password('foxconn1') and len(UserPasswordChange.objects.filter(user=request.user)) < 1:
                UserPasswordChange.first_time_user(request.user)
        except:
            raise ValueError('There was an error with the password check.')

        if request.method == 'POST':
            employee_email = request.POST['employee_email'].lower()
            current_password = request.POST['old_password']
            context['pass_fail1'] = False
            context['pass_fail2'] = False
            context['other_error'] = ""
            if request.user.email == employee_email and request.user.check_password(current_password):
                try:
                    success = UserPasswordChange.submit_change_request(request.user)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    context['other_error'] = "There was an error that occured when requesting password change. Please contact IT."
            if request.user.email != employee_email:
                context['email_error'] = 'The email you entered is not the email assigned to this account.'
                context['pass_fail1'] = True
            if request.user.check_password(current_password) != request.user.password:
                context['password_error'] = 'The password you entered is incorrect. Please try again.'
                context['pass_fail2'] = True

            return HttpResponse(
                json.dumps(context),
                content_type="application/json"
            )

        # set_session(request)

        # Get message:
        # Reset message so same message doesn't show again:
        request.session['confirmation_message'] = ''

        try:
            context['user_dept'] = request.session['department']
        except:
            raise ValueError('user_dept cannot get session variable for department.')

        context['navId'] = "mainNav"
        context['navBg'] = "navbar-dark"
        context['title'] = "Dashboard"


        # If users BU is from mentioned BUs
        context['allowed_view'] = False
        if request.session['business_unit'] not in ['iAI', '5G', 'IIoT']:
            context['allowed_view'] = True

        return render(request, 'office_app/dashboard.html', context)
    else:
        return redirect('login')


def contact_view(request):
    if request.user.is_authenticated:
        context = {}
        subject_details = None
        # context = {'form': request.POST}
        subject_options = [
            'Requesting Password Change',
            'Report Bug',
            'Give Feedback',
            'Other'
        ]

        subject_detailed_options = [
            'Report Bug',
            'Give Feedback',
            'Other'
        ]
        context['options'] = subject_options

        sender_info = Employee.objects.get(associateID=request.session['user_id'])
        context['user'] = sender_info

        if request.method == "POST":
            subject = request.POST['subject']
            print(request.POST.get('subject'))
            if request.POST['subject'] in subject_detailed_options:
                subject_details = request.POST['subject_other']

            if subject == "":
                messages.error(request, "Please fill all required fields")
                return render(request, 'office_app/contact_us.html', context)

            try:
                # Send Message to Site Admin(s)
                full_msg = f"{subject_details} : {datetime.now()}"

                if subject_details is not None:
                    EmailHandler.send_contact_email(request.user, subject, full_msg)
                else:
                    EmailHandler.send_contact_email(request.user, subject, isPwdReq=True)
                # messages.success(request, "An email has been sent to our team. We'll get back to you!")
                return redirect('smart_office_dashboard')

            except:
                messages.error(request, "Error submitting form. Please try again")
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                return render(request, 'office_app/contact_us.html', context)

        return render(request, 'office_app/contact_us.html', context)
    else:
        return redirect('login')


def ocr(request):
    # Will be different for different OS
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

    image = cv2.imread('static/office_app/image.png')
    string = pytesseract.image_to_string(image, lang='eng')
    print(string)
    return HttpResponse(string)


def notifications(request):
    if request.user.is_authenticated:
        return render(request, 'office_app/notifications.html', {'navId': '',
                                                                 'navBg': 'navbar-light',
                                                                 'title': 'Notifications',
                                                                 })
    else:
        return redirect('login')


def notifications_api(request):
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                if request.GET.get('view') == 'unread':
                    notifications_arr = []
                    for notification in Notification.objects.filter(employee=request.session['user_id'], is_unread=True).order_by(
                            '-created_on'):
                        notifications_arr.append(model_to_dict(notification))

                    return JsonResponse({"notifications": notifications_arr})
                else:
                    notifications_arr = []
                    for notification in Notification.objects.filter(employee=request.session['user_id']).order_by(
                            '-created_on'):
                        notifications_arr.append(model_to_dict(notification))

                    return JsonResponse({"notifications": notifications_arr})

            elif request.method == "PUT":
                notification = Notification.objects.get(id=request.GET.get('notification_id'))
                notification.is_unread = False
                notification.save()
                return HttpResponse("Success")
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact IT Support')
    else:
        return redirect('login')


def messages(request):
    if request.user.is_authenticated:
        return render(request, 'office_app/messages.html', {'navId': '',
                                                            'navBg': 'navbar-light',
                                                            'title': 'Messages',
                                                            })
    else:
        return redirect('login')


def messages_api(request):
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                if request.GET.get('view') == 'recipients':
                    recipients = []
                    for recipient in Employee.objects.all():
                        recipients.append({
                            'id': recipient.associateID,
                            'fullName': recipient.full_name,
                            'email': recipient.email,
                        })
                    return JsonResponse(recipients, safe=False)

                elif request.GET.get('view') == 'unread_messages':
                    messages = []
                    for message in Messages.objects.filter(employee=request.session['user_id'], is_unread=True).order_by('-sent_on'):
                        messages.append({
                            'id': message.id,
                            'sender_id': message.sender.associateID,
                            'sender_name': message.sender.full_name,
                            'sent_on': message.sent_on.astimezone(),
                            'message': message.message.replace('\n', ' '),
                            'is_unread': message.is_unread
                        })
                    return JsonResponse({'messages': messages})

                elif request.GET.get('view') == 'sent_messages':
                    messages = []
                    for message in Messages.objects.filter(sender=request.session['user_id']).order_by('-sent_on'):
                        # Sender name is the receiver name in sent messages.(to make it easy datatable re-render)
                        messages.append({
                            'id': message.id,
                            'sender_id': message.employee.associateID,
                            'sender_name': message.employee.full_name,
                            'date': message.sent_on.astimezone(),
                            'message': message.message.replace('\n', ' '),
                            'is_unread': message.is_unread
                        })
                    return JsonResponse({'messages': messages})
                else:
                    messages = []
                    for message in Messages.objects.filter(employee=request.session['user_id']).order_by('-sent_on'):
                        messages.append({
                            'id': message.id,
                            'sender_id': message.sender.associateID,
                            'sender_name': message.sender.firstName + " " + message.sender.lastName,
                            'date': message.sent_on.astimezone(),
                            'message': message.message.replace('\n', ' '),
                            'is_unread': message.is_unread
                        })
                    return JsonResponse({'messages': messages})

            if request.method == "POST":
                for recipient_id in (request.POST.get('recipients_id')).split(','):
                    message = Messages()
                    message.employee = Employee.objects.get(associateID=recipient_id)
                    message.sender = Employee.objects.get(associateID=request.session['user_id'])
                    message.message = strip_tags(request.POST['message'].replace('\n', ' '))
                    message.is_unread = True
                    message.sent_on = datetime.now().astimezone()
                    message.save()
                return HttpResponse('Message Sent')

            if request.method == "PUT":
                message = Messages.objects.get(id=request.GET.get('message_id'))
                if message.employee.associateID == request.session['user_id']:
                    message.is_unread = False
                    message.save()
                return HttpResponse('Message Read')

            if request.method == "DELETE":
                Messages.objects.get(id=request.GET.get('message_id')).delete()
                return HttpResponse('Message Deleted')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact IT Support')
    else:
        return redirect('login')


def chat_api(request):
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                messages = []
                for message in FormChat.objects.filter(formID=request.GET.get('formId'),
                                                       formType=request.GET.get('formType'),
                                                       id__gt=request.GET.get('lastMessageId')).order_by('sentOn'):
                    messages.append({
                        'message_id': message.id,
                        'sender_id': message.sender.associateID,
                        'sender_name': message.sender.firstName + " " + message.sender.lastName,
                        'sent_on': message.sentOn.astimezone().strftime("%Y-%m-%d %I:%M %p"),
                        'message': message.message,
                    })
                return JsonResponse({'messages': messages})

            elif request.method == "POST":
                formId = request.POST.get('formId')
                formType = request.POST.get('formType')

                new_message = FormChat()
                new_message.formID = formId
                new_message.formType = formType
                new_message.sender = Employee.objects.get(associateID=request.session['user_id'])
                new_message.message = request.POST.get('message')
                new_message.sentOn = datetime.now().astimezone()
                new_message.save()

                mentions = []
                for mention in json.loads(request.POST.get('mentions')):
                    mentions.append(Employee.objects.get(associateID=mention['id']))

                # Create notification for approvers
                if formType == "TA":
                    form = EmployeeInformation.objects.get(formID=formId)

                    for recipent in mentions:
                        try:
                            old_notification = Notification.objects.get(employee=recipent,
                                                                       module='Chat-TA-' + str(formId))
                            old_notification.created_on = datetime.now().astimezone()
                            old_notification.is_unread = True
                            old_notification.save()

                        except Notification.DoesNotExist:
                            notification = Notification()
                            notification.employee = recipent
                            notification.created_on = datetime.now().astimezone()
                            notification.module = 'Chat-TA-' + str(formId)
                            notification.title = "Chat"
                            notification.body = "You are mentioned in TA form # " + str(formId)
                            notification.link = "/travel/travel_application/" + str(formId)
                            notification.is_unread = True
                            notification.save()

                elif formType == "TR":
                    form = TADetails.objects.get(taDetail=EmployeeInformation.objects.get(formID=formId))

                    for recipent in mentions:
                        try:
                            old_notification = Notification.objects.get(employee=recipent,
                                                                       module='Chat-TR-' + str(formId))
                            old_notification.created_on =  datetime.now().astimezone()
                            old_notification.is_unread = True
                            old_notification.save()

                        except Notification.DoesNotExist:
                            notification = Notification()
                            notification.employee = recipent
                            notification.created_on = datetime.now().astimezone()
                            notification.module = 'Chat-TR-' + str(formId)
                            notification.title = "Chat"
                            notification.body = "You are mentioned in TR form # " + str(formId)
                            notification.link = "/travel/travel_reimbursement/" + str(formId)
                            notification.is_unread = True
                            notification.save()

                elif formType == "PR":
                    form = PurchaseRequestForm.objects.get(formID=formId)

                    for recipent in mentions:
                        try:
                            old_notification = Notification.objects.get(employee=recipent,
                                                                       module='Chat-PR-' + str(formId))
                            old_notification.created_on = datetime.now().astimezone()
                            old_notification.is_unread = True
                            old_notification.save()

                        except Notification.DoesNotExist:
                            notification = Notification()
                            notification.employee = recipent
                            notification.created_on = datetime.now().astimezone()
                            notification.module = 'Chat-PR-' + str(formId)
                            notification.title = "Chat"
                            notification.body = "You are mentioned in PR form # " + str(formId)
                            notification.link = "/purchase_request/" + str(formId)
                            notification.is_unread = True
                            notification.save()

                elif formType == "GR":
                    form = GRForm.objects.get(formID=formId)

                    for recipent in mentions:
                        try:
                            old_notification = Notification.objects.get(employee=recipent,
                                                                       module='Chat-GR-' + str(formId))
                            old_notification.created_on = datetime.now().astimezone()
                            old_notification.is_unread = True
                            old_notification.save()

                        except Notification.DoesNotExist:
                            notification = Notification()
                            notification.employee = recipent
                            notification.created_on = datetime.now().astimezone()
                            notification.module = 'Chat-GR-' + str(formId)
                            notification.title = "Chat"
                            notification.body = "You are mentioned in GR form # " + str(formId)
                            notification.link = "/goods_received/" + str(formId)
                            notification.is_unread = True
                            notification.save()

                return HttpResponse('200')

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')
    else:
        return redirect('login')


# Get approver for forms (for chat only)
def get_form_approvers_api(request):
    if request.user.is_authenticated:
        try:
            if request.method == "GET":
                formType = request.GET.get('formType')
                formId = request.GET.get('formId')

                if formId is None or formType is None:
                    return HttpResponseBadRequest("Form Type or Form Id Not Provided")

                if formType == "TA":
                    form = EmployeeInformation.objects.get(formID=formId)
                    approvers = []

                    # Add applicant
                    if form.employee.associateID != request.session['user_id']:
                        approvers.append({
                            'id': form.employee.associateID,
                            'name': form.employee.full_name,
                            'icon': 'fas fa-user',
                        })

                    # Add approvers
                    for approver in get_approvers_for_form_at_current_stage_or_lower(form, TemporaryApprovalStage):
                        approvers.append({
                            'id': approver.associateID,
                            'name': approver.full_name,
                            'icon': 'fas fa-user',
                        })

                    return JsonResponse({'approvers': approvers})

                elif formType == "TR":
                    form = TADetails.objects.get(taDetail=formId)
                    approvers = []

                    # Add applicant
                    if form.employee.associateID != request.session['user_id']:
                        approvers.append({
                            'id': form.employee.associateID,
                            'name': form.employee.full_name,
                            'icon': 'fas fa-user',
                        })

                    # Add approvers
                    for approver in get_approvers_for_form_at_current_stage_or_lower(form, TRApprovalProcess):
                        approvers.append({
                            'id': approver.associateID,
                            'name': approver.full_name,
                            'icon': 'fas fa-user',
                        })

                    return JsonResponse({'approvers': approvers})

                elif formType == "PR":
                    form = PurchaseRequestForm.objects.get(formID=formId)
                    approvers = []

                    # Add applicant
                    if form.employee.associateID != request.session['user_id']:
                        approvers.append({
                            'id': form.employee.associateID,
                            'name': form.employee.full_name,
                            'icon': 'fas fa-user',
                        })

                    # Add approvers
                    approvers_added = []
                    for item in PurchaseItemDetail.objects.filter(form=form):
                        for approver in PRApprovalProcess.objects.filter(formID=item, stage__lte=item.currentStage):
                            if approver.approverID not in approvers_added:
                                approvers_added.append(approver.approverID)
                                approvers.append({
                                    'id': approver.approverID.associateID,
                                    'name': approver.approverID.full_name,
                                    'icon': 'fas fa-user',
                                })

                    return JsonResponse({'approvers': approvers})

                elif formType == "GR":
                    form = GRForm.objects.get(formID=formId)
                    approvers = []

                    # Add approvers
                    for approver in GRApproversProcess.objects.filter(grForm=form):
                        approvers.append({
                            'id': approver.approver.associateID,
                            'name': approver.approver.full_name,
                            'icon': 'fas fa-user',
                        })

                    return JsonResponse({'approvers': approvers})

                return HttpResponse(200)

            else:
                return HttpResponseBadRequest('Invalid REST Request')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponseServerError('Server Error. Please Contact I.T Support')
    else:
        return redirect('login')


# def add_chat_user(request):
#     if request.user.is_authenticated:
#
#         chat_permission = Permissions()
#
#         # Check if the chat permission already exists, create otherwise
#         try:
#             chat_permission = Permissions.objects.get(key="TA-Chat-" + request.POST.get['form_id'],
#                                                       moduleCode="TA-Chat")
#
#         except Permissions.DoesNotExist:
#             chat_permission.key = "TA-Chat-" + request.POST.get['form_id']
#             chat_permission.description = "Chat permission for TA: " + request.POST.get['form_id']
#             chat_permission.moduleCode = "TA-Chat"
#             chat_permission.save()
#
#         # Assign chat permission to user
#         user_permission = UserPermissions()
#         user_permission.permission = chat_permission
#         user_permission.user = Employee.objects.get(associateID=request.POST.get['recipient_id'])
#
#         return HttpResponse('200')
#     else:
#         return redirect('login')


# def create_visitor(request):
#     if request.user.is_authenticated:
#         if request.method == 'POST':
#             visitor_data = dict(request.POST)
#             print("VisitorData: ", visitor_data)
#
#             # Render the page
#         return render(request, 'visitor_application/index.html')
#     else:
#         return redirect('../../accounts/login/?next=/vistor_application/')
