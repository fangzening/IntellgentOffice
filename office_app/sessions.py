from .models import *
from django.shortcuts import redirect

'''
    This function creates session variable for employee
    Written by: Zaawar Ejaz
    :param request: http data
    :param employee: employee object
'''


def set_session(request, **kwargs):
    if request.user.is_authenticated:
        # Check if session not already set
        if not request.session.has_key('id'):
            employee = Employee.objects.filter(associateID=request.user.associateID)
            print(f'User: {request.user.associateID} : {employee[0].email}')
            # Get employee object using django user information
            # employee = Employee.objects.filter(firstName=request.user.first_name, lastName=request.user.last_name,
            #                                    personalEmail=request.user.email).first()
            # if employee:
            #     print("Employee Found!")
            # else:
            #     employee = Employee.objects.filter(firstName=request.user.first_name, lastName=request.user.last_name,
            #                                        companyEmail=request.user.email).first()
            # Check if employee exist with same details then set sessions with employee data
            if employee:
                request.session['message'] = ''
                request.session['user_id'] = request.user.associateID

                temp = Employee.objects.get(associateID=request.user.associateID)
                request.session['id'] = temp.pk

                request.session['legal_entity_name'] = EmployeeDepartment.objects.filter(
                    associateID=temp.associateID).first().departmentID.businessUnit.businessGroup.legalEntity.entityName

                request.session['business_group'] = EmployeeDepartment.objects.filter(
                    associateID=temp.associateID).first().departmentID.businessUnit.businessGroup.name

                request.session['business_unit'] = EmployeeDepartment.objects.filter(
                    associateID=temp.associateID).first().departmentID.businessUnit.buName

                request.session['business_unit_code'] = EmployeeDepartment.objects.filter(
                    associateID=temp.associateID).first().departmentID.profitCenterCode

                request.session['department'] = EmployeeDepartment.objects.filter(
                    associateID=temp.associateID).first().departmentID.costCenterName

                request.session['department_code'] = EmployeeDepartment.objects.filter(
                    associateID=temp.associateID).first().departmentID.costCenterCode

                request.session['full_name'] = temp.full_name

                if CostCenter.objects.filter(managedBy=employee.model.associateID).first():
                    request.session['is_manager'] = True
                else:
                    request.session['is_manager'] = False

                # Set user permissions
                user_perm = []
                for perm in UserPermissions.objects.filter(user=employee.first()):
                    user_perm.append(perm.permission.key)

                request.session['user_perm'] = user_perm

            # Otherwise set session to empty
            else:
                request.session['department'] = ''
                request.session['id'] = ''
                request.session['user_id'] = request.user.id
                request.session['business_unit'] = ''
                request.session['middle_name'] = ''
                request.session['full_name'] = str(request.user.first_name + " " + request.user.last_name)
                request.session['is_manager'] = False
                request.session['business_unit_code'] = ''
                request.session['permissions'] = []

    else:
        return redirect('login')
