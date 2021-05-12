import math
import operator
import re
import sys
import traceback

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.utils import *
from datetime import datetime
from django.db import models, transaction, connection
from django.contrib.auth.decorators import permission_required
# from it_app.models import UserPasswordChange
from .custom_functions import *
import csv
from django.contrib.postgres.fields import ArrayField

# To encrypt or decrypt data
from django.utils import timezone

security = Fernet(settings.ENCRYPT_KEY)

def createAssociateID():
    # get last employee object
    lastEmployee = Employee.objects.all().last()

    # if no employee created, create starting id
    if not lastEmployee:
        return 'SO-' + str(1).zfill(6)
    # get id of last employee object
    last_associateID = lastEmployee.associateID
    # create new employee id by incrementing in last id
    new_associateID = 'SO-' + str(int(last_associateID[3:]) + 1).zfill(6)

    return new_associateID


class BusinessGroup(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    generalManager = models.ForeignKey('Employee', on_delete=models.CASCADE, blank=True, null=True)
    costManager = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='bgCostManager', blank=True,
                                    null=True)
    legalEntity = models.ForeignKey('LegalEntity', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_all_BG():
        return BusinessGroup.objects.all()


class LegalEntity(models.Model):
    entityName = models.CharField(max_length=64, primary_key=True)
    sapCompCode = models.CharField(max_length=8)

    @staticmethod
    def create_legal_entity(entityName, sapCompCode):
        LegalEntity.objects.create(entityName=entityName, sapCompCode=sapCompCode)

    @property
    def compShorthand(self):
        shorthand = self.entityName[0:3]
        entities = LegalEntity.objects.all().order_by('entityName')
        i = 3
        for name in entities:
            if name == shorthand:
                shorthand = shorthand[0:2] + self.entityName[i]
                i += 1
        return shorthand

    def __str__(self):
        return self.entityName

    @property
    def compShorthand(self):
        shorthand = self.entityName[0:3]
        entities = LegalEntity.objects.all().order_by('entityName')
        i = 3

        for name in entities:
            if name == shorthand:
                shorthand = shorthand[0:2] + self.entityName[i]
                i += 1
        return shorthand


class Building(models.Model):
    legalEntity = models.ForeignKey(LegalEntity, on_delete=models.CASCADE)
    locationName = models.CharField(max_length=5)
    locAddress = models.CharField(max_length=255)
    locCity = models.CharField(max_length=50)
    locState = models.CharField(max_length=25)
    locZip = models.IntegerField()
    locCountry = models.CharField(max_length=25, default='United States of America')

    # region Properties
    def __str__(self):
        return self.locationName

    @property
    def streetAddress(self):
        return f"{self.locAddress}, {self.locCity}, {self.locState} {self.locZip}"
    # endregsion Properties

    # region Functions
    @staticmethod
    def create_building(entityName, buildingName, locAddress, locCity, locState, locZip):
        LegalEntity.objects.create(legalEntity=entityName, locationName=buildingName, locAddress=locAddress,
                                   locCity=locCity, locState=locState, locZip=locZip)

    @staticmethod
    def get_all_buildings():
        return Building.objects.all()
    # endregion Functions


class Employee(models.Model):
    associateID = models.CharField(max_length=50, unique=True, primary_key=True, default=createAssociateID)
    firstName = models.CharField(max_length=50, blank=True, null=True)
    middleName = models.CharField(max_length=50, blank=True, null=True)
    lastName = models.CharField(max_length=50, blank=True, null=True)
    otherName = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    secondaryEmail = models.EmailField(blank=True, null=True)
    doh = models.DateField(blank=True, null=True)
    mainPhone = models.CharField(max_length=20, blank=True, null=True)
    otherPhone = models.CharField(max_length=20, blank=True, null=True)
    # mainPhone = models.BigIntegerField(blank=True, null=True)
    # otherPhone = models.BigIntegerField(blank=True, null=True)
    phoneExt = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=128, blank=True, null=True)
    reportsToGM = models.BooleanField(default=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, default=1, blank=True, null=True)

    # region Properties
    def __str__(self):
        if self.otherName:
            return self.otherName + " " + self.lastName
        elif self.middleName:
            return self.firstName + " " + self.middleName + " " + self.lastName
        else:
            return self.firstName + " " + self.lastName
        #return self.full_name

    @property
    def full_name(self):
        if self.otherName:
            return self.otherName + " " + self.lastName
        elif self.middleName:
            return self.firstName + " " + self.middleName + " " + self.lastName
        else:
            return self.firstName + " " + self.lastName

    @property
    def fullname(self):
        if self.otherName:
            return self.otherName + " " + self.lastName
        elif self.middleName:
            return self.firstName + " " + self.middleName + " " + self.lastName
        else:
            return self.firstName + " " + self.lastName

    @property
    def full_legal_name(self):
        if self.middleName:
            return self.firstName + " " + self.middleName + " " + self.lastName
        else:
            return self.firstName + " " + self.lastName

    @property
    def legalEntity(self):
        return CostCenter.objects.get(costCenterCode=EmployeeDepartment.objects.get(associateID=self.associateID).departmentID.costCenterCode).businessUnit.businessGroup.legalEntity

    @property
    def businessUnit(self):
        return CostCenter.objects.get(costCenterCode=EmployeeDepartment.objects.get(
            associateID=self.associateID).departmentID.costCenterCode).businessUnit

    @property
    def businessGroup(self):
        return CostCenter.objects.get(costCenterCode=EmployeeDepartment.objects.get(
            associateID=self.associateID).departmentID.costCenterCode).businessUnit.businessGroup

    @property
    def buildingAddress(self):
        return self.building.locAddress

    @property
    def sapCompCode(self):
        return self.legalEntity.sapCompCode

    @property
    def vendorName(self):
        return self.firstName.upper() + ' ' + self.lastName.upper()
    # endregion Properties

    # region Functions
    @staticmethod
    def create_employee_user(empContext):
        # print(empContext)
        if len(Account.objects.filter(email=empContext['email'])) > 0:
            print(f"{empContext['email']} already exists")
            return
        obj = Employee()
        obj.firstName = empContext['fname']
        obj.lastName = empContext['lname']
        if empContext['prefName'] == '' or empContext['prefName'] == None:
            obj.otherName = None
        if empContext['building'] == 'Hou':
            obj.building = Building.objects.filter(locationName='MPB').first()
        else:
            obj.building = Building.objects.filter(locationName=empContext['building']).first()
        obj.email = empContext['email']
        obj.title = empContext['title']
        obj.save()
        obj.assign_emp_dept(empContext['costCenter'])
        print(obj.associateID)
        acct = Account()
        acct.email = empContext['email']
        acct.employee = obj
        acct.set_password('foxconn1')
        acct.save()

        # create_user(self, email, password=None, associateID=None, is_active=False, is_staff=False, is_superuser=False):

    def assign_emp_dept(self, costCenterCode):
        temp_dept = EmployeeDepartment()
        temp_dept.associateID = Employee.objects.get(associateID=self.associateID)
        temp_dept.departmentID = CostCenter.objects.filter(costCenterCode=costCenterCode).first()
        if temp_dept.departmentID == None:
            return
        temp_dept.save()

    def update_existing(self, row):
        from it_app.views import clean_str

        self.title = clean_str(row['title'])
        temp_dept = EmployeeDepartment.objects.get(associateID=self)
        temp_dept.departmentID = clean_str(row['costCenterCode'])

        self.save()
        temp_dept.save()

    @staticmethod
    def get_all_employee_info():
        return {"data": Employee.objects.all.only('associateID', 'firstName', 'middleName', 'lastName', 'email')}

    @staticmethod
    def get_all_employees():
        return Employee.objects.all()

    @staticmethod
    def get_employee_by_associate_id(aid):
        return Employee.objects.get(associateID=aid)

    @staticmethod
    def get_employee_by_email(emp_email):
        employee = Employee.objects.get(companyEmail=emp_email)
        return employee

    # @staticmethod
    # def create_new_employee(first_name, middle_name, last_name, preferred_name, email, secondary_email,):
        # Employee.objects.create(firstName=)
    # endregion Functions


# class ProfitCenter(models.Model):
#     profitCenterCode = models.CharField(primary_key=True, max_length=50)


class BusinessUnit(models.Model):
    buName = models.CharField(primary_key=True, max_length=50)
    managedBy = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID', blank=True, null=True)
    costManager = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='buCostManager', blank=True, null=True)
    groupVp = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='buVicePres', blank=True,
                                    null=True)
    businessGroup = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, related_name='businessGroup', default='FII W')
    buBuyer = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='buBuyer', blank=True, null=True)
    # plantCode = models.CharField(max_length=10, default='FII1')

    # region Properties
    def __str__(self):
        return self.buName

    @property
    def company(self):
        return self.businessGroup.legalEntity

    @property
    def plantCode(self, company=None):
        if company != None:
            company = LegalEntity.objects.get(entityName=company)
        elif company == None:
            company = self.company
        return PlantCodeCombination.objects.get(businessUnit=self.buName, legalEntity=company).plantCode
    # endregion Properties

    @staticmethod
    def get_all_BU():
        return BusinessUnit.objects.all()

# ADDED 10/14/2020
class PlantCodeCombination(models.Model):
    combinationID = models.BigAutoField(primary_key=True)
    businessUnit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    legalEntity = models.ForeignKey(LegalEntity, on_delete=models.CASCADE)
    plantCode = models.CharField(max_length=10, blank=True, null=True)

    # region Properties
    def __str__(self):
        return f'{self.combinationID} : {self.businessUnit} and {self.legalEntity}'
    # endregion Properties

    # region Functions
    @staticmethod
    def create_entry(businessUnitName, legalEntityName):
        bu = BusinessUnit.objects.get(buName=businessUnitName)
        entity = LegalEntity.objects.get(entityName=legalEntityName)
        PlantCodeCombination.objects.create(businessUnit=bu, legalEntity=entity)
    # endregion Functions


# Department is the cost center of the company
class CostCenter(models.Model):
    costCenterCode = models.CharField(primary_key=True, max_length=50)
    businessUnit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, related_name='businessUnit', default=None)
    costCenterName = models.CharField(max_length=50)
    managedBy = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='managedBy', to_field='associateID', blank=True, null=True)
    accountant = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='accountant', blank=True, null=True)
    costManager = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='costManager', blank=True, null=True)
    profitCenterCode = models.CharField(max_length=50, blank=True, null=True)

    # region Properties
    def __str__(self):
        return str(self.costCenterName)

    @property
    def fullCC(self):
        return self.costCenterCode + ' : ' + self.costCenterName
    # endregion Properties

    # region Functions
    @staticmethod
    def get_all_by_bu(bu_name):
        return CostCenter.objects.all(businessUnit=bu_name)

    @staticmethod
    def get_all_cost_center():
            return CostCenter.objects.all()



class Role(models.Model):
    roleID = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    level = models.IntegerField(default=0)

    # region Properties
    def __str__(self):
        return self.title
    # endregion Properties

    # region Functions

    # endregion Functions


class EmployeeDepartment(models.Model):
    associateID = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    departmentID = models.ForeignKey(CostCenter, on_delete=models.CASCADE, blank=True, null=True)
    roleID = models.ForeignKey(Role, on_delete=models.CASCADE, blank=True, null=True)
    joiningDate = models.DateField(blank=True, null=True)
    leavingDate = models.DateField(blank=True, null=True)

    # region Properties
    def __str__(self):
        return f"{self.associateID} : {self.departmentID.costCenterName}"

    @property
    def costCenterManager(self):
        return self.departmentID.managedBy
    # endregion Properties

    # region Functions
    @staticmethod
    def create_employee_department(associateID, departmentID, roleID, managerID, joiningDate=datetime.now(), leavingDate=None):
        EmployeeDepartment.objects.create(associateID=associateID, departmentID=departmentID, roleID=roleID, managerID=managerID,
                                          joiningDate=joiningDate, leavingDate=leavingDate)

    @staticmethod
    # get corresponding manager according to the employee associate id
    def get_manager_by_employee_associate_id(associateID):
        manager_list = EmployeeDepartment.objects.filter(associateID=associateID)
        manager_id = manager_list[0].managerID
        return Employee.get_employee_by_associate_id(manager_id.associateID)
    # endregion Functions


class FoxconnRate(models.Model):
    hotelID = models.BigAutoField(primary_key=True)
    hotelName = models.CharField(max_length=100)
    hotelPrice = models.DecimalField(max_digits=6, decimal_places=2)
    city = models.CharField(max_length=50)


class GLAccount(models.Model):
    glCode = models.CharField(primary_key=True, max_length=50)
    glDescription = models.CharField(max_length=100)

    # region Properties
    def __str__(self):
        return self.glDescription
    # endregion Properties

    # region Functions
    @staticmethod
    def get_all_GL():
        return GLAccount.objects.all()
    # endregion Functions


class ModuleAccess(models.Model):
    department = models.ForeignKey(CostCenter, on_delete=models.CASCADE)
    employeeID = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')

    '''
        Add User
        Written by: Jacob Lattergrass
        :param department: the department the user will be linked to for viewing other modules
        :param employeeID: the ID of the employee, which links to the employee user
    '''
    # region Functions
    @staticmethod
    def add_user(department, employeeID):
        ModuleAccess.objects.create(department=department, employeeID=employeeID)
    # endregion Functions


"""
    AdminAccess is a table that will store a set number of users as administrators.
    You can add more levels of authority if needed.
"""


class AdminAccess(models.Model):
    adminID = models.IntegerField(primary_key=True)
    employeeID = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    authorityLevel = models.IntegerField(default=1)

    # region Properties
    def __str__(self):
        return self.employeeID.full_name
    # endregion Properties

    # region Functions
    '''
        Add Admin
        Written by: Jacob Lattergrass
        :param employeeID: the ID of the employee, which links to the employee user
        :param authLevel: the authority level of the admin
    '''
    @staticmethod
    def add_admin(employeeID, authLevel):
        AdminAccess.objects.create(employeeID=employeeID, authorityLevel=authLevel)
    # endregion Functions


'''
    Permission Tables
    Used for determining the level of access
    a user has in their module.
'''


class Permissions(models.Model):
    key = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    moduleCode = models.CharField(max_length=50, blank=True, null=True)

    # region Properties
    def __str__(self):
        return self.description + " | " + self.key


class UserPermissions(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    permission = models.ForeignKey(Permissions, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'User Permissions'
        verbose_name = 'Special User Permission'

    def __str__(self):
        return self.user.firstName + " " + self.user.lastName + " | " + self.permission.moduleCode + ": " + self.permission.key


class GroupPermissions(models.Model):
    groupName = models.CharField(max_length = 20)
    permission = models.ForeignKey(Permissions, on_delete=models.CASCADE)

    # region Properties
    class Meta:
        verbose_name_plural = 'Group Permissions'
        verbose_name = 'Group Permission'

    def __str__(self):
        return self.groupName
    # endregion Properties


class SecretKey(models.Model):
    keyName = models.CharField(max_length=50, primary_key=True)


class KeyAccess(models.Model):
    employeeID = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    keyName = models.ForeignKey(SecretKey, on_delete=models.CASCADE)


class Notification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=250)
    module = models.CharField(max_length=50)
    created_on = models.DateTimeField()
    link = models.CharField(max_length=250)
    is_unread = models.BooleanField(default=True)

    @staticmethod
    def new_notification(title, msg, module, viewer, link=""):
        Notification.objects.create(employee=viewer, title=title, body=msg, module=module, created_on=datetime.now(),
                                    link=link)


class Messages(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="sender", to_field='associateID')
    message = models.CharField(max_length=500)
    sent_on = models.DateTimeField(blank=True, null=True)
    is_unread = models.BooleanField(default=True)


class Vendors(models.Model):
    vendorName = models.CharField(max_length=100, blank=True, null=True)
    vendorCode = models.CharField(max_length=15, blank=True, null=True)
    companyCode = models.CharField(max_length=15, blank=True, null=True)
    supplierContact = models.CharField(max_length=100, blank=True, null=True)
    supplierAddress = models.CharField(max_length=150, blank=True, null=True)
    supplierTelephone = models.CharField(max_length=100, blank=True, null=True)
    vendorCountry = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return self.vendorName


class EmployeeVendors(models.Model):
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')

    def __str__(self):
        return str(self.employee)

    @staticmethod
    def set_current_vendors():
        empVendors = []
        emps = Employee.objects.all()
        vendors = Vendors.objects.all()
        for emp in emps:
            for vendor in vendors:
                if vendor.vendorName == emp.vendorName():
                    empVendors.append(EmployeeVendors(vendor=vendor, employee=emp))


        EmployeeVendors.objects.bulk_create(empVendors)

    @staticmethod
    def check_current_vendors():
        empVendors = []
        emps = Employee.objects.all()
        vendors = Vendors.objects.all()

        with open('EmployeeVendors.csv', 'w', newline='') as file:
            fieldnames = ['Vendor']
            writer = csv.DictWriter(file, fieldnames)
            for emp in emps:
                for vendor in vendors:
                    if vendor.vendorName == emp.vendorName():
                        empVendors.append(emp.full_name + ' : ' + vendor.vendorName)
                        writer.writerow({'Vendor': emp.full_name + ' : ' + vendor.vendorName})


class ProcessType(models.Model):
    processCode = models.CharField(max_length=10, primary_key=True)
    processDescription = models.CharField(max_length=50)

    def __str__(self):
        return self.processCode

    @staticmethod
    def initialize_approval_process(form, approval_proccess_object_type, request,
                                    businessUnit=None, url_form=None, all_post_data_index=0, starting_stage=1, base_user=None, include_base_user_in_process=False):
        from office_app.approval_functions import notify_approver, merge_dictionaries

        if base_user == None:
            base_user = Employee.objects.get(associateID=request.session['user_id'])

        error_messages = {'fatal_errors': '', 'other_errors': []}

        # region Getting Process Type / Combination
        if businessUnit == None:
            businessUnit = EmployeeDepartment.objects.get(associateID=base_user).departmentID.businessUnit
        reportsToGM = base_user.reportsToGM
        try:
            if reportsToGM:
                try:
                    process_type = Combination.objects.get(buName=businessUnit, formType=form.sap_prefix,
                                                           reportsToGM=True).processType
                except:
                    process_type = Combination.objects.get(buName=businessUnit, formType=form.sap_prefix,
                                                           reportsToGM=False).processType
            else:
                print(businessUnit)
                print(form.sap_prefix)
                process_type = Combination.objects.get(buName=businessUnit, formType=form.sap_prefix,
                                                       reportsToGM=False).processType
        except Combination.DoesNotExist:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            try:
                if reportsToGM:
                    try:
                        process_type = Combination.objects.get(buName=None, formType=form.sap_prefix, reportsToGM=True).processType
                    except:
                        process_type = Combination.objects.get(buName=None, formType=form.sap_prefix,
                                                               reportsToGM=False).processType
                else:
                    process_type = Combination.objects.get(buName=None, formType=form.sap_prefix,
                                                           reportsToGM=False).processType
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error getting process type for the form. Please contact IT."
                form.isCompleted = False
                form.currentStage = 0
                form.save()
                print(f"current stage is 0: {form.currentStage }")
                return error_messages
        # endregion

        if url_form == None:
            url_form = form
        process_stages = ProcessStages.objects.filter(processType=process_type).order_by('stage')
        stages = []
        # Add approvers from process stages into the stage
        for stage in process_stages:
            # Add approver in the stage (based on parameter above)
            try:
                stage_condition = stage.check_stage_condition(request, all_post_data_index)
                if stage_condition:
                    stage_approver = stage.get_approver(request, all_post_data_index, base_user)
                    if stage_approver:
                        stages.append(stage_approver)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = 'Error creating approval process.\n Form has been saved but not submitted'
                return error_messages

        added_approvers = []

        stage_number = starting_stage
        form.currentStage = starting_stage
        form.save()
        print(f"current stage is starting stage: {form.currentStage}")

        for approver in stages:
            if include_base_user_in_process == False:
                if approver != base_user and approver not in added_approvers and approver != None:
                    add_condition = True
                else:
                    add_condition = False
            else:
                if approver not in added_approvers and approver != None:
                    add_condition = True
                else:
                    add_condition = False
            if add_condition:
                added_approvers.append(approver)
                new_stage = approval_proccess_object_type()
                new_stage.create_approval_stage(formID=form, approverID=approver, stage=stage_number, count=0)
                new_stage.save()
                # Notify first approvers that they must look at this form
                if stage_number == starting_stage:
                    new_stage.dayAssigned = datetime.today()
                    new_stage.save()
                    error_messages = merge_dictionaries(error_messages,
                                                        notify_approver(message_type="next_approver", module=url_form.module,
                                                                        form=url_form, employee=approver,
                                                                        request=request))
                stage_number += 1
            form.currentStage = starting_stage
            form.save()
        return error_messages

    @staticmethod
    def get_context_for_editing_process(request):
        context = {}

        # region get process type
        the_process = ProcessType.objects.get(processCode=request.POST.get('processName'))
        context.update({'processType': {'processName': request.POST.get('processName'), 'processDesc': the_process.processDescription}})
        # endregion

        # region get process stages and conditions
        the_stages = ProcessStages.objects.filter(processType=the_process).order_by('stage')
        index = 0
        for stage in the_stages:
            conditions_dict = {"conditions": {}}
            inside_conditions = {}
            cond_index = 0
            for condition in stage.conditions.all().order_by('multi_condition_order'):
                inside_conditions.update({'condition-' + str(cond_index):
                          {'constant_value_1': condition.constant_value_1,
                           'constant_value_2': condition.constant_value_2,
                           'field_name_1': condition.field_name_1,
                           'field_name_2': condition.field_name_2,
                           'multi_condition_order': condition.multi_condition_order,
                           'operator': condition.comparison_operator}
                    }
                )
                cond_index += 1
            stage_dict = {'stage-'+str(index): {'stage': stage.stage, 'stageApprover_roleID': stage.stageApprover.approverRole.roleID, "stageApprover_title": stage.stageApprover.approverRole.title, "field_name": stage.field_name, "connectors": stage.connectors, "conditions": inside_conditions}}
            context.update(stage_dict)
            index += 1
        # endregion
        return context



    def set_process_type_values(self, processCode=None, processDesc=None):
        if processCode != None:
            self.processCode = processCode
        if processDesc != None:
            self.processDescription = processDesc
        self.save()


    def create_process(self, request):
        all_post_data = dict(request.POST)

        # Update Process Type Information
        self.set_process_type_values(processCode=request.POST.get('processName'), processDesc=request.POST.get('processDesc'))

        # region deleting Old Process Stages and Old Approver Conditions
        process_stages_to_delete = ProcessStages.objects.filter(processType=self)
        for obj in process_stages_to_delete:
            conditions_to_delete = obj.conditions.all()
            for cond in conditions_to_delete:
                cond.delete()
            obj.delete()
        # endregion


        # region creating New Process Stages and New Approver Conditions
        # Get stage numbers to help sort them with stages:

        stage_numbers = []
        for key in all_post_data.keys():
            if 'stageApprover' in key:
                stage_affiliation_number = key.split("-")[1]
                if int(stage_affiliation_number) not in stage_numbers:
                    stage_numbers.append(int(stage_affiliation_number))
        stage_numbers.sort()

        # Start Creating Process Stages
        index = 0
        for stageApproverNum in stage_numbers:
            # Create Process Stage
            new_process_stage = ProcessStages()
            new_process_stage.set_process_stage_values(processType=self,
                                                       stage=int(all_post_data['stage_number'][index]),
                                                       stageApprover=ProcessApprover.objects.get(approverRole__roleID=int(request.POST.get('stageApprover-' + str(stageApproverNum)))),
                                                       field_name=all_post_data['field_name'][index])
        # endregion

        # region Create Conditions for the stage and link it to Process Stages, also create connectors
            if ('operator-' + str(stage_numbers[index])) in all_post_data:
                ApproverCondition.set_conditions_for_stage_from_post_data(all_post_data, stage_numbers[index], new_process_stage)
        # endregion
            index += 1




class Combination(models.Model):
    buName = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, blank=True, null=True)
    formType = models.CharField(max_length=2)
    processType = models.ForeignKey(ProcessType, on_delete=models.CASCADE)
    reportsToGM = models.BooleanField(default=False)

    def __str__(self):
        if self.buName != None:
            return str(self.buName.buName) + " | " + self.formType
        else:
            if self.reportsToGM:
                return "Default Report to GM | " + self.formType
            else:
                return "Default | " + self.formType

    def set_values(self, buName=None, formType=None, processType=None, reportsToGM=None):
        if buName != None:
            self.buName = buName
        if formType != None:
            self.formType = formType
        if processType != None:
            self.processType = processType
        if reportsToGM != None:
            self.reportsToGM = reportsToGM
        self.save()


# Old Process Approver table:
# class ProcessApprover(models.Model):
#     approverRole = models.ForeignKey(Role, on_delete=models.CASCADE)
# def __str__(self):
#     return self.approverRole.title


# region approval process tables
#############################################################################################################################################################################
# APPROVAL PROCESS TABLES
#############################################################################################################################################################################

class ProcessApprover(models.Model):
    approverRole = models.ForeignKey(Role, on_delete=models.CASCADE)

    @property
    def role(self):
        return self.approverRole.title

    def __str__(self):
        return str(self.role)

    # endregion



class ApproverCondition(models.Model):
    operands =(('is the same as', 'is the same as'),
               ('is not the same as', 'is not the same as'),
               ('is less than', 'is less than'),
               ('is greater than', 'is greater than'),
               ('is greater than or equal to', 'is greater than or equal to'),
               ('is less than or equal to', 'is less than or equal to'))
    constant_value_1 = models.CharField(default='', max_length=50)   # First value in condition, if it is a constant value
    field_name_1 = models.CharField(default='', max_length=50)       # First value in condition, if it is a field value
    constant_value_2 = models.CharField(default='', max_length=50)   # Second value in condition, if second value is a constant value
    field_name_2 = models.CharField(default='', max_length=50)       # Second value in condition, if it is a field value
    multi_condition_order = models.IntegerField(default=0)  # Tells which order this condition is in if there are multiple conditions per stage
                                                            # For example, if StageType has two conditions that are linked by 'and',
                                                            # and condition1 has multi_condition_order = 1
                                                            # and condition2 has multi_condition_order = 2,
                                                            # Then the statement will be condition1 and condition 2
    comparison_operator = models.CharField(choices=operands, max_length=65)


    def set_approver_condition_values(self, constant_value_1=None, field_name_1=None, constant_value_2=None,
                                      field_name_2=None, multi_condition_order=None, comparision_operator=None):
        if constant_value_1 != None:
            self.constant_value_1 = constant_value_1
        if field_name_1 != None:
            self.field_name_1 = field_name_1
        if constant_value_2 != None:
            self.constant_value_2 = constant_value_2
        if field_name_2 != None:
            self.field_name_2 = field_name_2
        if multi_condition_order != None:
            self.multi_condition_order = multi_condition_order
        if comparision_operator != None:
            self.comparison_operator = comparision_operator
        self.save()


    @staticmethod
    def set_conditions_for_stage_from_post_data(all_post_data, stage_num, process_stage):
        condition_order = 1
        condition_value_first_index = 0
        for operator in all_post_data['operator-' + str(stage_num)]:
            new_condition = ApproverCondition()
            # two values to check per operator (condition_value-#)                                  <----- condition value and
            # two literal or field name types per operator, one per value (condition_value_type-#)  <----- condition type are parallel arrays
            # and_or-# contains and and/or connectors if there is more than one condition for a stage.
            #         They won't always exist though.
            condition_value_1 = all_post_data['condition_value-' + str(stage_num)][condition_value_first_index]
            condition_value_type_1 = all_post_data['condition_value_type-' + str(stage_num)][condition_value_first_index]
            condition_value_2 = all_post_data['condition_value-' + str(stage_num)][condition_value_first_index + 1]
            condition_value_type_2 = all_post_data['condition_value_type-' + str(stage_num)][condition_value_first_index + 1]
            if condition_value_type_1 == 'literal' and condition_value_type_2 == 'literal':
                new_condition.set_approver_condition_values(constant_value_1=condition_value_1,
                                                            constant_value_2=condition_value_2,
                                                            multi_condition_order=condition_order,
                                                            comparision_operator=operator)
            elif condition_value_type_1 == 'field name' and condition_value_type_2 == 'literal':
                new_condition.set_approver_condition_values(field_name_1=condition_value_1,
                                                            constant_value_2=condition_value_2,
                                                            multi_condition_order=condition_order,
                                                            comparision_operator=operator)
            elif condition_value_type_1 == 'field name' and condition_value_type_2 == 'field name':
                new_condition.set_approver_condition_values(field_name_1=condition_value_1,
                                                            field_name_2=condition_value_2,
                                                            multi_condition_order=condition_order,
                                                            comparision_operator=operator)
            else:
                new_condition.set_approver_condition_values(constant_value_1=condition_value_1,
                                                            field_name_2=condition_value_2,
                                                            multi_condition_order=condition_order,
                                                            comparision_operator=operator)
            process_stage.conditions.add(new_condition)
            if condition_order > 1:
                condition_connector = all_post_data['and_or-' + str(stage_num)][condition_order - 2]
                if process_stage.connectors == '':
                    process_stage.connectors = condition_connector
                else:
                    process_stage.connectors = process_stage.connectors + "," + condition_connector
            process_stage.save()
            condition_order += 1
            condition_value_first_index += 2

    @staticmethod
    def parse_string_for_math(equasion, request, all_post_data_index):
        all_post_data = dict(request.POST)
        # region Get Equasion without the MATH( ) stuff

        inside_equasion = equasion.replace("MATH(", "", 1)
        inside_equasion2 = ''
        length = len(inside_equasion)

        for i in range(length):
            if (inside_equasion[i] == ")"):
                inside_equasion2 = inside_equasion[0:i] + inside_equasion[i + 1:length]
        # endregion

        # region Replace variables with numbers
        # First turn string into an array
        split1 = re.findall(r"[\w']+", inside_equasion2)
        for split in split1:
            try:
                if split != " " or split != "":
                    float(split)
            except:
                try:
                    actual_value_of_field = all_post_data[split][all_post_data_index]
                except:
                    actual_value_of_field = request.POST.get(split)
                # Now replace`value in inside_equasion2 with new value:
                inside_equasion2 = inside_equasion2.replace(split, actual_value_of_field)
        # endregion

        nsp = NumericStringParser()
        # vvv This is a modified version of eval that only does math. NumericStringParser in in office_app/custom functions
        value = nsp.eval(inside_equasion2)

        return value

    def do_any_math_for_value(self, equasion, request, all_post_data_index):
        all_post_data = dict(request.POST)
        if "MATH(" not in equasion:
            if equasion == self.field_name_1 or equasion == self.field_name_2:
                try:
                    value = all_post_data[equasion][all_post_data_index]
                except:
                    value = request.POST.get(equasion)
            else:
                value = equasion
        else:
            value = self.parse_string_for_math(equasion, request, all_post_data_index)
        return value

    def get_first_value(self, request, all_post_data_index):
        value_chosen = self.constant_value_1
        if self.field_name_1 != '':
            value_chosen = self.field_name_1
        value1 = self.do_any_math_for_value(value_chosen, request, all_post_data_index)
        return value1


    def get_second_value(self, request, all_post_data_index):
        value2 = self.constant_value_2
        if self.field_name_2 != '':
            all_post_data = dict(request.POST)
            try:
                value2 = all_post_data[self.field_name_2][all_post_data_index]
            except:
                value2 = request.POST.get(self.field_name_2)
        return value2


    def check_condition(self, request, all_post_data_index):
        val1 = self.get_first_value(request, all_post_data_index)
        val2 = self.get_second_value(request, all_post_data_index)


        if self.comparison_operator == 'is less than':
            if float(val1) < float(val2):
                return True
            else:
                return False
        elif self.comparison_operator == 'is greater than':
            if float(val1) > float(val2):
                return True
            else:
                return False
        elif self.comparison_operator == 'is greater than or equal to':
            if float(val1) >= float(val2):
                return True
            else:
                return False
        elif self.comparison_operator == 'is less than or equal to':
            if float(val1) <= float(val2):
                return True
            else:
                return False
        elif self.comparison_operator == 'is the same as':
            if val1 == val2:
                return True
            else:
                return False
        elif self.comparison_operator == 'is not the same as':
            if val1 != val2:
                return True
            else:
                return False

class ProcessStages(models.Model):
    processType = models.ForeignKey(ProcessType, on_delete=models.CASCADE)
    stage = models.IntegerField()
    stageApprover = models.ForeignKey(ProcessApprover, on_delete=models.CASCADE)
    field_name = models.CharField(default='', max_length=50)    # Field name that helps GET the approver
    conditions = models.ManyToManyField(ApproverCondition)      # Conditions that help decide if the approver should be in the process
    connectors = models.CharField(default='', max_length=100)   # A list of and/or to connect multiple conditions (actually a string with commas, no spaces.)

    def __str__(self):
        return str(self.processType) + " | " + str(self.stage) + " | " + str(self.stageApprover)

    def set_process_stage_values(self, processType=None, stage=None, stageApprover=None, field_name=None, conditions=None, connectors=None):
        if processType != None:
            self.processType = processType
        if stage != None:
            self.stage = stage
        if stageApprover != None:
            self.stageApprover = stageApprover
        if field_name != None:
            self.field_name = field_name
        if conditions != None:
            self.conditions = conditions
        if connectors != None:
            self.connectors = str(connectors).replace(" ", "").replace("'", "")
        self.save()

    def check_stage_condition(self, request, all_post_data_index):
        if self.connectors != '':
            connector_list = self.connectors.split(',')
        else:
            connector_list = None

        unordered_conditions = self.conditions.all()
        ordered_conditions = unordered_conditions.order_by('multi_condition_order')
        amount_of_conditions = unordered_conditions.count()

        if amount_of_conditions == 1: # If there is only one condition
            return ordered_conditions.first().check_condition(request, all_post_data_index)
        elif amount_of_conditions > 1: # If there are multiple conditions
            # Loop through conditions
            index = 0
            final_condition = ordered_conditions[0].check_condition(request, all_post_data_index)
            for condition in ordered_conditions:
                if index != 0:
                    if connector_list[index - 1] == 'or':
                        if final_condition or condition.check_condition(request, all_post_data_index):
                            final_condition = True
                        else:
                            final_condition = False
                    else:
                        if final_condition and condition.check_condition(request, all_post_data_index):
                            final_condition = True
                        else:
                            final_condition = False
                index += 1
            return final_condition
        else: # If there are no conditions
            return True

    def get_department_by_field(self, request, all_post_data_index):
        all_post_data = dict(request.POST)
        try:
            field_value = all_post_data[self.field_name][all_post_data_index]
        except:
            field_value = request.POST.get(self.field_name)
        try:
            dept = CostCenter.objects.get(costCenterName=field_value)
        except:
            try:
                dept = CostCenter.objects.get(costCenterCode=field_value)
            except:
                try:
                    dept = CostCenter.objects.get(pk=field_value)
                except:
                    dept = None
        return dept

    # region Function that returns the approver
    def get_approver(self, request, all_post_data_index, base_user):
        field_dept = None
        if self.field_name != '':
            field_dept = self.get_department_by_field(request, all_post_data_index)
        user_dept = EmployeeDepartment.objects.get(associateID=base_user).departmentID
        approver = None

        all_post_data = dict(request.POST)

        try:
             field_value = all_post_data[self.field_name][all_post_data_index]
        except:
            field_value = request.POST.get(self.field_name)

        if self.stageApprover.approverRole.title == "Department Manager":
            if self.field_name == '':
                return user_dept.managedBy
            else:
                return field_dept.managedBy

        elif self.stageApprover.approverRole.title == "Department Cost Manager":
            if self.field_name == '':
                approver = user_dept.costManager
            else:
                approver = field_dept.costManager

        elif self.stageApprover.approverRole.title == "Business Unit Manager":
            if self.field_name == '':
                approver = user_dept.businessUnit.managedBy
            else:
                try:
                    approver = field_dept.businessUnit.managedBy
                except:
                    BusinessUnit.objects.get(buName=field_value)

        elif self.stageApprover.approverRole.title == "Cost Management Manager":
            approver = CostCenter.objects.get(costCenterName='Supporting - Cost Management').managedBy

        elif self.stageApprover.approverRole.title == "Business Group Cost Manager":
            if self.field_name == '':
                approver = user_dept.businessUnit.businessGroup.costManager
            else:
                try:
                    approver = BusinessGroup.objects.get(name=field_value).costManager
                except:
                    try:
                        approver = BusinessGroup.objects.get(pk=field_value).costManager
                    except:
                        approver = field_dept.businessUnit.businessGroup.costManager

        elif self.stageApprover.approverRole.title == "Specific Person From Application":
            try:
                approver = Employee.objects.get(associateID=field_value)
            except:
                for employee in Employee.objects.all():
                    if employee.fullname == field_value:
                        approver = employee
                        break
                    if employee.full_name == field_value:
                        approver = employee
                        break
                    if employee.full_legal_name == field_value:
                        approver = employee
                        break
                if approver == None:
                    for employee in Employee.objects.all():
                        if employee.firstName + " " + employee.lastName == field_value:
                            approver = employee
                            break

        elif self.stageApprover.approverRole.title == "Specific Person From Employees":
                approver = Employee.objects.get(associateID=self.field_name)

        elif self.stageApprover.approverRole.title == "Business Unit Cost Manager":
            if self.field_name == '':
                approver = user_dept.businessUnit.businessGroup.costManager
            else:
                try:
                    approver = BusinessUnit.objects.get(buName=field_value).costManager
                except:
                    try:
                        approver = BusinessUnit.objects.get(pk=field_value).costManager
                    except:
                        approver = field_dept.businessUnit.costManager

        elif self.stageApprover.approverRole.title == "General Manager":
            if self.field_name == '':
                approver = user_dept.businessUnit.businessGroup.generalManager
            else:
                approver = field_dept.businessUnit.businessGroup.generalManager

        elif self.stageApprover.approverRole.title == "Accountant":
            if self.field_name == '':
                approver = user_dept.accountant
            else:
                approver = field_dept.accountant

        elif self.stageApprover.approverRole.title == "Accountant Manager":
            approver = CostCenter.objects.get(costCenterName='Supporting - Accounting').managedBy

        elif self.stageApprover.approverRole.title == "Group VP":
            if self.field_name == '':
                approver = user_dept.businessUnit.groupVp
            else:
                approver = field_dept.businessUnit.groupVp

        # elif self.stageApprover.approverRole.title == "Cost Manager Lead":
        #     if self.field_name == '':
        #         approver = user_dept.businessUnit.costManagerLead
        #     else:
        #         approver = field_dept.businessUnit.costManagerLead

        return approver


# This model is for the delegation process
class ApprovalProcessDelegation(models.Model):
    delegateID = models.BigAutoField(primary_key=True)
    delegatingUser = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='delegator')
    delegatedUser = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='delegated')
    effectiveDate = models.DateField(blank=True, null=True)

    @staticmethod
    def create_entry(delegator, delegated, effectiveDate):
        if len(ApprovalProcessDelegation.objects.filter(delegatingUser=delegator)) == 0:
            ApprovalProcessDelegation.objects.create(delegatingUser=delegator, delegatedUser=delegated,
                                                     effectiveDate=effectiveDate)

    @staticmethod
    def delete_entry(delegator):
        ApprovalProcessDelegation.objects.get(delegatingUser=delegator).delete()


#############################################################################################################################################################################
# END APPROVAL PROCESS TABLES
#############################################################################################################################################################################
# endregion


class SAPResponse(models.Model):
    transactionID = models.CharField(max_length=20, primary_key=True)
    form = models.CharField(max_length=50)      # This will be form type and id, so 'TR-191
    sapMessage = models.CharField(max_length=200, blank=True, null=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    responseValue = models.CharField(max_length=50, blank=True, null=True)
    # Response value will store any document numbers given to us by SAP


class SAPServer(models.Model):
    serverID = models.BigAutoField(primary_key=True)
    serverAddress = models.CharField(max_length=20)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    companyCode = models.CharField(max_length=50)
    wsdl = models.CharField(max_length=255)

    def set_password(self, raw_password=None):
        if raw_password is None:
            raise ValueError(f"You cannot set the password to None.")
        encrypted_password = security.encrypt(raw_password.encode('utf-8'))
        self.password = encrypted_password.decode('utf-8')
        self.save()

    def password_check(self, raw_password):
        decrypted_password = security.decrypt(self.password.encode('utf-8'))
        plain_text_pwd = decrypted_password.decode('utf-8')
        if raw_password == plain_text_pwd:
            return True
        return False

    def connect(self, raw_password):
        results = []
        return results


# region Module Control
class SmartOfficeModule(models.Model):
    moduleName = models.CharField(primary_key=True, max_length=40)
    moduleShorthandName = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.moduleName

    def __repr__(self):
        return self.moduleShorthandName

    @staticmethod
    def create_entry(moduleName, shorthandName=None):
        print(f"Creating module entry for {moduleName}...")
        try:
            SmartOfficeModule.objects.get(moduleName=moduleName)
            print(f"There is already an entry for {moduleName}!")
        except SmartOfficeModule.DoesNotExist:
            SmartOfficeModule.objects.create(moduleName=moduleName, moduleShorthandName=shorthandName)
# endregion Module Control

# region User Authentication
class MyAccountManager(BaseUserManager):
    @staticmethod
    def create_employee(email):
        temp_employee = Employee()

        name_str = email.split('.')
        email_separator = name_str[1].split('@')

        temp_employee.firstName = name_str[0]
        temp_employee.lastName = email_separator[0]
        temp_employee.email = email
        temp_employee.title = 'Administrator'
        temp_employee.save()
        return temp_employee

    def create_user(self, email, password=None, associateID=None, is_active=False, is_staff=False, is_superuser=False):
        if not email:
            raise ValueError('Users must have an email address')
        # if not associateID:
        #     raise ValueError('Users must have an associate id.')
        email = email.lower()
        user = self.model(
            email=self.normalize_email(email),
        )
        user.employee = Employee.objects.get(associateID=associateID)
        user.set_password(password)

        user.is_active = is_active
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )

        emp = self.create_employee(email=email)
        user.employee = emp

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=128, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID', null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perms(self, perm, obj=None):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_perms(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def associateID(self):
        return self.employee.associateID

    @property
    def fullname(self):
        try:
            if not self.employee.otherName:
                return self.employee.firstName + ' ' + self.employee.lastName
            elif self.employee.otherName:
                return self.employee.otherName + ' ' + self.employee.lastName
        except:
            print('Error: Employee is not linked')

    @property
    def first_name(self):
        return str(self.employee.firstName)

    @property
    def last_name(self):
        return str(self.employee.lastName)

    @property
    def associateID(self):
        return self.employee.associateID


# endregion

