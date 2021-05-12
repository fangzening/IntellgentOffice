from django.db import models, transaction, connection
from cryptography.fernet import Fernet
from django.conf import settings
from django.http import *

# To encrypt or decrypt data
from django.forms import model_to_dict

from office_app.models import *
import json

security = Fernet(settings.ENCRYPT_KEY)


class PAF(models.Model):
    pafID = models.BigAutoField(primary_key=True)

    # Employee Information
    emp_firstName = models.CharField(max_length=20, blank=True, null=True)
    emp_middleName = models.CharField(max_length=20, blank=True, null=True)
    emp_lastName = models.CharField(max_length=20, blank=True, null=True)
    emp_otherName = models.CharField(max_length=20, blank=True, null=True)
    emp_email = models.EmailField(unique=False, blank=True, null=True)
    emp_phone = models.CharField(unique=False, max_length=20, blank=True, null=True)
    emp_homeAddress = models.CharField(max_length=250, blank=True, null=True)

    # General Informationn
    dateOfHire = models.DateField(blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    actionType = models.CharField(max_length=50, blank=True, null=True)
    employmentType = models.CharField(max_length=50, blank=True, null=True)
    createdBy = models.CharField(max_length=50)

    def __str__(self):
        return str(self.pafID)

    """
        This function create new paf object and submit it to the data base
        Written by: Zaawar Ejaz
        :param: self: new paf object
    """

    def createPAF(self, emp_firstName, emp_middleName, emp_lastName, emp_otherName, emp_email, emp_phone,
                  emp_homeAddress, dateOfHire, position, unit, department, actionType, employmentType, createdBy):

        self.actionType = actionType
        self.employmentType = employmentType
        self.emp_firstName = emp_firstName
        self.emp_middleName = emp_middleName
        self.emp_lastName = emp_lastName
        self.emp_otherName = emp_otherName
        self.emp_email = emp_email
        self.emp_phone = emp_phone
        self.emp_homeAddress = emp_homeAddress
        self.dateOfHire = dateOfHire
        self.position = position
        self.unit = unit
        self.department = department
        self.createdBy = createdBy
        self.save()

    """
        This function returns all checklist in json format
        Written by: Zaawar Ejaz
        :param: pafID: the paf id of the paf
        :return: paf object

    """

    @staticmethod
    def get_paf_details(pafID):
        return PAF.objects.get(pafID=pafID)

    """
        This function returns all paf or paf created by manager (if id is provided) in json format
        Written by: Zaawar Ejaz
        :param manager_id: manager employee id
        :return: json formatted data

    """

    @staticmethod
    def get_all_paf(empID):
        cursor = connection.cursor()
        result = []

        cursor.execute(
            'SELECT "pafID","emp_firstName", "emp_middleName", "emp_lastName", "emp_email", "emp_phone", "position", "department", '
            '"unit", "employmentType", "actionType", "dateOfHire", "createdBy" '
            'FROM smart_hr_paf '
            'WHERE "createdBy" = %s', [empID]
        )

        try:
            for row in cursor.fetchall():
                result.append(dict(zip([col[0] for col in cursor.description], row)))
        except:
            return {"data": result}

        return {"data": result}


"""
    This function create new paf object and submit it to the data base
    Written by: Zaawar Ejaz
    :param: self: new paf object
"""


class PAFAuthorizer(models.Model):
    pafID = models.ForeignKey(PAF, on_delete=models.CASCADE)
    signature_number = models.IntegerField()
    fullName = models.CharField(max_length=50)
    dateSigned = models.DateField()

    def __str__(self):
        return str(self.pafID)

    def addPAFAuthorizer(self, pafID, fullName, dateSigned, signature_number):
        self.pafID = pafID
        self.signature_number = signature_number
        self.fullName = fullName
        self.dateSigned = dateSigned
        self.save()

    @staticmethod
    def getPAFAuthorizers(pafID):
        pafAuths = []
        for obj in PAFAuthorizer.objects.filter(pafID=pafID):
            pafAuths.append(obj)
        return pafAuths

    @staticmethod
    def get_Paf_Managers():
        managers = []
        for p in PAFAuthorizer.objects.filter(signature_number=1):
            managers.append(p)
        return managers

    """
         This function gets the string version of a field's value
         Author: Corrina Barr
         :param self: the Model's object(an instance of the model, a row in the model)
         :param field: the field in the object you want to be converted to a string
         :return: returns the object's field as a string datatype so it is easier for python to work with
    """

    def get_string_version(self, field):
        return str(field)


class ChecklistTask(models.Model):
    taskID = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(CostCenter, on_delete=models.CASCADE)
    status = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return str(self.taskID)


class NewHireChecklist(models.Model):
    empID = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    taskID = models.ForeignKey(ChecklistTask, on_delete=models.CASCADE)
    taskAssignee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee', to_field='associateID')
    dueDate = models.DateField(blank=True, null=True)
    completed = models.BooleanField()
    dateCompleted = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.empID)

    def updateChecklist(self, employeeID, taskID, dueDate):
        self.empID = employeeID
        self.taskID = taskID
        self.dueDate = dueDate

    def createChecklist(self, employeeID):
        self.empID = employeeID
        self.save()

    """
         This function gets the string version of a field's value
         Author: Corrina Barr
         :param self: the Model's object(an instance of the model, a row in the model)
         :param field: the field in the object you want to be converted to a string
         :return: returns the object's field as a string datatype so it is easier for python to work with
    """

    def get_string_version(self, field):
        return str(field)

    """
        This function returns all checklist in json format
        Written by: Zaawar Ejaz
        :return: json formatted data

    """

    @staticmethod
    def get_assigned_checklist(assigneeID):
        cursor = connection.cursor()
        result = []

        if UserPermissions.objects.filter(user=assigneeID, permission__key="view_all_checklist").count() > 0:
            cursor.execute(
                'SELECT DISTINCT '
                '(SELECT COUNT(*) FROM smart_hr_newhirechecklist newhire WHERE newhire."empID_id" = emp."associateID") as "totalTasks", '
                '(SELECT COUNT(*) FROM smart_hr_newhirechecklist newhire WHERE newhire."empID_id" = emp."associateID" and newhire."taskAssignee_id" = %s) as "assigneeTasks", '
                '(SELECT COUNT(*) FROM smart_hr_newhirechecklist newhire WHERE newhire."empID_id" = emp."associateID" and newhire."completed" = True) as "totalTasksCompleted", '
                '(SELECT COUNT(*) FROM smart_hr_newhirechecklist newhire WHERE newhire."empID_id" = emp."associateID" and newhire."taskAssignee_id" = %s and newhire."completed" = True) as "assigneeTasksCompleted", '
                'emp."associateID", emp."firstName", emp."middleName", emp."lastName", role."title" as position, costcenter."costCenterName" as department, emp."doh", manager."firstName" as mfname, manager."lastName" as mlname '
                'FROM smart_hr_newhirechecklist '
                'INNER JOIN office_app_employee AS emp '
                'ON smart_hr_newhirechecklist."empID_id" = emp."associateID"'
                'INNER JOIN office_app_employeedepartment AS empdept '
                'ON emp."associateID" = empdept."associateID_id"'
                'INNER JOIN office_app_costcenter AS costcenter '
                'ON costcenter."costCenterCode" = empdept."departmentID_id" '
                'INNER JOIN office_app_role AS role '
                'ON role."roleID" = empdept."roleID_id" '
                'INNER JOIN (SELECT * FROM office_app_employee) manager '
                'ON manager."associateID" = costcenter."managerBy_id" ', [assigneeID, assigneeID]
            )
        else:
            cursor.execute(
                'SELECT DISTINCT '
                '(SELECT COUNT(*) FROM smart_hr_newhirechecklist newhire WHERE newhire."empID_id" = emp."associateID") as "totalTasks", '
                '(SELECT COUNT(*) FROM smart_hr_newhirechecklist newhire WHERE newhire."empID_id" = emp."associateID" and newhire."taskAssignee_id" = %s) as "assigneeTasks", '
                '(SELECT COUNT(*) FROM smart_hr_newhirechecklist newhire WHERE newhire."empID_id" = emp."associateID" and newhire."completed" = True) as "totalTasksCompleted", '
                '(SELECT COUNT(*) FROM smart_hr_newhirechecklist newhire WHERE newhire."empID_id" = emp."associateID" and newhire."taskAssignee_id" = %s and newhire."completed" = True) as "assigneeTasksCompleted", '
                'emp."associateID", emp."firstName", emp."middleName", emp."lastName", role."title" as position, costcenter."costCenterName" as department, emp."doh", manager."firstName" as mfname, manager."lastName" as mlname '
                'FROM smart_hr_newhirechecklist '
                'INNER JOIN office_app_employee AS emp '
                'ON smart_hr_newhirechecklist."empID_id" = emp."associateID"'
                'INNER JOIN office_app_employeedepartment AS empdept '
                'ON emp."associateID" = empdept."associateID_id"'
                'INNER JOIN office_app_costcenter AS costcenter '
                'ON costcenter."costCenterCode" = empdept."departmentID_id" '
                'INNER JOIN office_app_role AS role '
                'ON role."roleID" = empdept."roleID_id" '
                'INNER JOIN (SELECT * FROM office_app_employee) manager '
                'ON manager."associateID" = costcenter."managedBy_id" '
                'WHERE smart_hr_newhirechecklist."taskAssignee_id" = %s ', [assigneeID, assigneeID, assigneeID]
            )
        try:
            for row in cursor.fetchall():
                result.append(dict(zip([col[0] for col in cursor.description], row)))
        except:
            return {"data": result}

        return {"data": result}
