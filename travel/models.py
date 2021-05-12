import datetime
import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import *
from office_app.models import *
# To encrypt or decrypt data
from travel.custom_functions import is_nothing, merge_dictionaries

security = Fernet(settings.ENCRYPT_KEY)


# Travel Application
def get_upload(instance, filename):
    return '/'.join(filter(None, (instance.location, filename)))


class EmployeeInformation(models.Model):
    formID = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(LegalEntity, on_delete=models.CASCADE)
    businessGroup = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    # department = models.ForeignKey(Department, on_delete=models.CASCADE)
    project = models.CharField(max_length=100, null=True)
    estimatedExpense = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    travelType = models.CharField(max_length=50, blank=True, null=True)  # value comes from drop down box
    budgetSourceCode = models.CharField(max_length=20, blank=True, null=True)
    advancedApp = models.BooleanField(default=False, null=True)
    isCompleted = models.BooleanField(default=False, null=True)
    currentStage = models.IntegerField(default=0, blank=True)
    isApproved = models.BooleanField(default=False)
    isDeclined = models.BooleanField(default=False)


    @property
    def creationDate(self):
        return TravelDetail.objects.get(formID=self.formID).date

    @property
    def form_url_without_base_url(self):
        return "/travel/travel_application/" + str(self.pk) + "/"

    @property
    def full_url(self):
        return str(settings.BASE_URL) + "/travel/travel_application/" + str(self.pk) + "/"

    def __str__(self):
        return 'Travel Form: ' + str(self.formID)

    @property
    def form_type(self):
        return "Travel Application"

    @property
    def sap_prefix(self):
        return "TA"

    @property
    def module(self):
        return "travel"

    @property
    def advance_type(self):
        return AdvanceTravelApp

    def save_travel_form(self, company, bg, employee, project, estimatedExpense, travelType, budgetSourceCode,
                         advancedApp, isCompleted):
        self.company = company
        self.businessGroup = bg
        self.employee = employee
        self.project = project
        if estimatedExpense == '':
            self.estimatedExpense = 0
        else:
            self.estimatedExpense = estimatedExpense
        self.travelType = travelType
        print("Budget Source Code: " + budgetSourceCode)
        self.budgetSourceCode = budgetSourceCode
        self.advancedApp = advancedApp
        self.isCompleted = isCompleted
        self.save()


    def initialize_ta_approval_process(self, request):
        error_messages = {"fatal_errors": "", "other_errors": []}
        # Get budget sc informations
        try:
            budgetSC = CostCenter.objects.get(costCenterCode=self.budgetSourceCode)
            businessUnit = budgetSC.businessUnit
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "Error updating approval process! Form was saved but not submitted. Please try again later."
            return error_messages

        error_messages = merge_dictionaries(error_messages, ProcessType.initialize_approval_process(form=self,
                                                               approval_proccess_object_type=TemporaryApprovalStage,
                                                               request=request, businessUnit=businessUnit))
        return error_messages


class TravelDetail(models.Model):
    detailID = models.BigAutoField(primary_key=True)
    formID = models.ForeignKey(EmployeeInformation, on_delete=models.CASCADE)
    company = models.ForeignKey(LegalEntity, on_delete=models.CASCADE, null=True)
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    departurePreferred = models.CharField(max_length=50, blank=True, null=True)
    departureFactoryCode = models.CharField(max_length=30, blank=True, null=True)
    departureCountry = models.CharField(max_length=25, null=True)
    destinationCity = models.CharField(max_length=40, null=True)
    destinationProvince = models.CharField(max_length=50, null=True)
    destinationCountry = models.CharField(max_length=25, null=True)
    transportation = models.CharField(max_length=50, null=True)
    date = models.DateField(null=True)
    accommodation = models.CharField(max_length=20, null=True)
    estimatedDuration = models.IntegerField(null=True)
    isCompleted = models.BooleanField(default=False, null=True)
    currency = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "Travel Detail " + str(self.detailID)

    def save_travel_detail(self, formID, company, startDate, endDate, departureCountry, departurePrefferred,
                           departureFactoryCode,
                           destinationCity,
                           destinationState, destinationCountry,
                           transportation, date, accommodation, isCompleted, estimatedDuration, currency):
        self.formID = formID
        self.company = company
        self.currency = currency
        self.departureCountry = departureCountry
        self.departurePreferred = departurePrefferred
        self.departureFactoryCode = departureFactoryCode
        self.destinationCity = destinationCity
        self.destinationCountry = destinationCountry
        self.destinationProvince = destinationState
        if startDate != '':
            self.startDate = startDate
        else:
            self.startDate = None
        if endDate != '':
            self.endDate = endDate
        else:
            self.endDate = None
        if estimatedDuration != '':
            self.estimatedDuration = estimatedDuration
        else:
            self.estimatedDuration = None
        self.transportation = transportation
        if date != '':
            self.date = date
        else:
            self.date = None
        self.accommodation = accommodation
        self.isCompleted = isCompleted
        self.save()

    @staticmethod
    # That has stage > 0
    def get_all_travel_forms():
        cursor = connection.cursor()
        result = []
        cursor.execute(
            'SELECT null as formType, emp_info."formID", emp."firstName", emp."middleName", emp."lastName", dept."costCenterName" as department, emp_info."currentStage", "date" '
            'FROM travel_traveldetail '
            'INNER JOIN travel_employeeInformation AS emp_info '
            'ON travel_traveldetail."formID_id" = emp_info."formID" '
            'INNER JOIN office_app_employeedepartment AS empdept '
            'ON empdept."associateID_id" = emp_info."employee_id"'
            'INNER JOIN office_app_employee AS emp '
            'ON empdept."associateID_id" = emp."associateID"'
            'INNER JOIN office_app_costcenter AS dept '
            'ON dept."costCenterCode" = empdept."departmentID_id" '
            'AND emp_info."currentStage" > %s ', [0]
        )
        try:
            for row in cursor.fetchall():
                result.append(dict(zip([col[0] for col in cursor.description], row)))
        except:
            return {"data": result}

        return {"data": result}

    @staticmethod
    def get_approvers_travel_forms(employee):
        cursor = connection.cursor()
        result = []
        cursor.execute(
            'SELECT null as formType, emp_info."formID", emp."firstName", emp."middleName", emp."lastName", dept."costCenterName" as department, emp_info."currentStage", '
            'approvalstage."actionTaken", approvalstage."stage" as "tempStage", approvalstage."date", emp_info."isApproved", emp_info."isDeclined" '
            'FROM travel_traveldetail '
            'INNER JOIN travel_employeeInformation AS emp_info '
            'ON travel_traveldetail."formID_id" = emp_info."formID" '
            'INNER JOIN office_app_employeedepartment AS empdept '
            'ON empdept."associateID_id" = emp_info."employee_id" '
            'INNER JOIN office_app_employee AS emp '
            'ON empdept."associateID_id" = emp."associateID" '
            'INNER JOIN office_app_costcenter AS dept '
            'ON dept."costCenterCode" = empdept."departmentID_id" '
            'INNER JOIN travel_temporaryapprovalstage AS approvalstage '
            'ON emp_info."formID" = approvalstage."formID_id" '
            'WHERE %s = approvalstage."approverID_id" '
            'AND approvalstage."stage" > %s '
            'AND emp_info."currentStage" >= approvalstage."stage"', [employee, 0]
        )
        try:
            for row in cursor.fetchall():
                result.append(dict(zip([col[0] for col in cursor.description], row)))
        except:
            return {"data": result}
        return {"data": result}

    @staticmethod
    def get_emp_travel_forms(employee):
        cursor = connection.cursor()
        result = []
        cursor.execute(
            'SELECT DISTINCT emp_info."formID", (SELECT COUNT(*) FROM travel_temporaryapprovalstage WHERE travel_temporaryapprovalstage."formID_id" = emp_info."formID") AS "totalStages", '
            'emp_info."travelType", "startDate", "endDate", emp."firstName", emp."middleName", emp."lastName", emp_info."currentStage", emp_info."isCompleted", approval_stage."actionTaken", emp_info."isApproved", emp_info."isDeclined" '
            'FROM travel_traveldetail '
            'INNER JOIN travel_employeeInformation AS emp_info '
            'ON travel_traveldetail."formID_id" = emp_info."formID" '
            'INNER JOIN office_app_employeedepartment AS empdept '
            'ON empdept."associateID_id" = emp_info."employee_id" '
            'INNER JOIN office_app_employee AS emp '
            'ON empdept."associateID_id" = emp."associateID" '
            'INNER JOIN office_app_costcenter AS dept '
            'ON dept."costCenterCode" = empdept."departmentID_id" '
            'INNER JOIN travel_temporaryapprovalstage AS approval_stage '
            'ON approval_stage."formID_id" = emp_info."formID"'
            'WHERE emp_info."currentStage" = approval_stage."stage" '
            'AND emp_info."employee_id" = %s ', [employee]
        )
        try:
            for row in cursor.fetchall():
                result.append(dict(zip([col[0] for col in cursor.description], row)))
        except:
            return {"data": result}

        return {"data": result}


class TravelDetailExpenses(models.Model):
    expenseID = models.BigAutoField(primary_key=True)
    detailID = models.ForeignKey(TravelDetail, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    allowanceExp = models.CharField(max_length=100, null=True)
    accommodation = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    accommodationExp = models.CharField(max_length=100, null=True)
    transportation = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    transportationExp = models.CharField(max_length=100, null=True)
    visa = models.CharField(max_length=50, null=True)
    visaExp = models.CharField(max_length=100, blank=True, null=True)
    airwayTicket = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    airwayTicketExp = models.CharField(max_length=100, null=True)
    insurance = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    insuranceExp = models.CharField(max_length=100, null=True)
    other = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    otherExp = models.CharField(max_length=100, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    isCompleted = models.BooleanField(default=False, null=True)
    publicRelationship = models.CharField(max_length=20, null=True)
    publicRelationshipExp = models.CharField(max_length=100, null=True)

    def save_detail_expense(self, detailID, date, allowance, allowanceExp, accommodation, accommodationExp,
                            transportation, transportationExp, visa, visaExp, airwayTicket, airwayTicketExp,
                            insurance, insuranceExp, other, otherExp, total, isCompleted,
                            publicRelation, publicRelationExp):
        self.detailID = detailID
        self.date = date
        if allowance == None and allowance != '':
            self.allowance = 0
        else:
            self.allowance = allowance
        self.allowanceExp = allowanceExp
        self.accommodation = accommodation
        self.accommodationExp = accommodationExp
        self.transportation = transportation
        self.transportationExp = transportationExp
        self.visa = visa
        self.visaExp = visaExp
        self.airwayTicket = airwayTicket
        self.airwayTicketExp = airwayTicketExp
        self.insurance = insurance
        self.insuranceExp = insuranceExp
        self.other = other
        self.otherExp = otherExp
        if (total == ''):
            self.total = 0
        else:
            self.total = total
        self.isCompleted = isCompleted
        self.publicRelationship = publicRelation
        self.publicRelationshipExp = publicRelationExp
        self.save()


class TravelDetailCompany(models.Model):
    visitID = models.BigAutoField(primary_key=True)
    detailID = models.ForeignKey(TravelDetail, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    visitCompany = models.CharField(max_length=50, null=True)  # Comes from pre-defined data
    department = models.CharField(max_length=50, null=True)  # Comes from pre-defined data
    contact = models.CharField(max_length=60, null=True)  # Comes from pre-defined data
    preciseObjective = models.CharField(max_length=50, null=True)
    isCompleted = models.BooleanField(default=False, null=True)
    modifiedField = models.BooleanField(default=False, null=True)

    def __str__(self):
        return " TravelDetailCompany: " + str(self.visitID) + " " + str(self.detailID.formID)

    def save_detail_company(self, detailID, date, visitCompany, department, contact, preciseObjective, isCompleted):
        if ',' in str(date):
            return 0
        self.detailID = detailID
        if date != '':
            if str(date)[0] == '[':
                self.date = date[0]
            else:
                self.date = date
        else:
            self.date = None
        if visitCompany != '':
            if str(visitCompany)[0] == '[':
                self.visitCompany = visitCompany[0]
            else:
                self.visitCompany = visitCompany
        else:
            self.visitCompany = None
        if department != '':
            if str(department)[0] == '[':
                self.department = department[0]
            else:
                self.department = department
        else:
            self.department = None
        if contact != '':
            if str(contact)[0] == '[':
                self.contact = contact[0]
            else:
                self.contact = contact
        else:
            self.contact = None
        if preciseObjective != '':
            if str(preciseObjective)[0] == '[':
                self.preciseObjective = preciseObjective[0]
            else:
                self.preciseObjective = preciseObjective
        else:
            self.preciseObjective = None
        self.isCompleted = isCompleted
        self.save()


class AdvanceTravelApp(models.Model):
    advID = models.BigAutoField(primary_key=True)
    formID = models.ForeignKey(EmployeeInformation, on_delete=models.CASCADE)
    advAmount = models.DecimalField(max_digits=10, decimal_places=2)
    glAccount = models.CharField(max_length=50, blank=True, null=True)
    glDescription = models.CharField(max_length=50, blank=True, null=True)
    costCenterCode = models.CharField(max_length=50, blank=True, null=True)
    profitCenter = models.CharField(max_length=50, blank=True, null=True)  # Department
    headText = models.CharField(max_length=50, blank=True, null=True)
    text = models.CharField(max_length=50, blank=True, null=True)
    assignment = models.CharField(max_length=100, blank=True, null=True) # vendorcode,costcentercode
    isCompleted = models.BooleanField(default=False, null=True)
    currency = models.CharField(max_length=50, blank=True, null=True)
    refDocument = models.CharField(max_length=50, blank=True, null=True)
    dateApplied = models.DateField(blank=True, null=True)
    dateApproved = models.DateField(blank=True, null=True)
    companyCode = models.CharField(max_length=50, blank=True, null=True)
    vendorCode = models.CharField(max_length=15, blank=True, null=True)

    def save_adv_app(self, formID, advAmount, glAccount, glDescription, costCenterCode, profitCenter, currency,
                     headText, text, assignment, isCompleted, refDocument, dateApplied, vendorCode, companyCode):
        self.formID = formID
        if advAmount != '':
            self.advAmount = advAmount
        else:
            self.advAmount = 0
        self.invoiceDate = datetime.today()  # SET BY SYSTEM, NOT THE PROGRAMMER
        if is_nothing(currency) == False:
            self.currency = currency
        if is_nothing(glAccount) == False:
            self.glAccount = glAccount
        if is_nothing(glDescription) == False:
            self.glDescription = glDescription
        if is_nothing(costCenterCode) == False:
            self.costCenterCode = costCenterCode
        if is_nothing(profitCenter) == False:
            self.profitCenter = profitCenter
        if is_nothing(companyCode) == False:
            self.companyCode = companyCode
        if is_nothing(headText) == False:
            self.headText = headText
        if is_nothing(text) == False:
            self.text = text
        if is_nothing(assignment) == False:
            self.assignment = assignment
        if is_nothing(isCompleted) == False:
            self.isCompleted = isCompleted
        if is_nothing(refDocument) == False:
            self.refDocument = refDocument
        if is_nothing(dateApplied) == False:
            self.dateApplied = dateApplied
        if is_nothing(vendorCode) == False:
            self.vendorCode = vendorCode
        self.save()
        return self


class TemporaryApprovalStage(models.Model):
    formID = models.ForeignKey(EmployeeInformation, on_delete=models.CASCADE)
    approverID = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True, to_field='associateID')
    stage = models.IntegerField(primary_key=False, default=0)
    count = models.IntegerField(primary_key=False, default=0)
    actionTaken = models.CharField(max_length=50, default=None, blank=True, null=True)
    comments = models.CharField(max_length=255, default=None, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    dayAssigned = models.DateTimeField(blank=True, null=True)
    approvalType = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.approverID) + " stage " + str(self.stage) + " for " + str(self.formID)

    def set_action_taken(self, actionTaken):
        self.actionTaken = actionTaken
        self.save()

    def create_approval_stage(self, formID, approverID, stage, count):
        self.formID = formID
        self.approverID = approverID
        self.stage = stage
        self.count = count
        self.save()

    def count_approvers(self):
        temp = TemporaryApprovalStage
        rows = temp.objects.filter(stage=self.stage, formID=self.formID)
        ctr = 0
        for row in rows:
            ctr += 1
        return ctr

    def count_approved_forms_for_stage(self):
        temp = TemporaryApprovalStage
        rows = temp.objects.filter(stage=self.stage, formID=self.formID, count=1)
        ctr = 0
        for row in rows:
            ctr += 1
        return ctr


class ModifiedFields(models.Model):
    formID = models.IntegerField(unique=False)
    fieldID = models.CharField(max_length=50, null=True)
    fieldData = models.CharField(max_length=100, null=True)
    visitID = models.ForeignKey(TravelDetailCompany, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "Form " + str(self.formID) + " " + str(self.fieldID)

    def modify_fields(self, formID, fieldID, fieldData):
        self.formID = formID
        self.fieldID = fieldID
        self.fieldData = fieldData
        self.save()

    def modify_dynamic_fields(self, formID, fieldID, fieldData, visitID):
        self.formID = formID
        self.fieldID = fieldID
        self.fieldData = fieldData
        self.visitID = visitID
        self.save()


# Travel Reimbursement
class TADetails(models.Model):
    taDetail = models.OneToOneField(EmployeeInformation, on_delete=models.CASCADE, primary_key=True)
    numOfWeeks = models.IntegerField(blank=True, null=True)
    isCompleted = models.BooleanField(default=False, blank=True, null=True)
    currentStage = models.IntegerField(default=0, blank=True)
    isApproved = models.BooleanField(default=False)
    isDeclined = models.BooleanField(default=False)
    totalAmount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    @property
    def form_type(self):
        return "Travel Reimbursement"

    @property
    def sap_prefix(self):
        return "TR"

    @property
    def module(self):
        return "travel"

    @property
    def form_url_without_base_url(self):
        return "/travel/travel_reimbursement/" + str(self.pk) + "/"

    @property
    def advance_type(self):
        return AdvanceReimbursementApp

    @property
    def full_url(self):
        return str(settings.BASE_URL) + "/travel/travel_reimbursement/" + str(self.pk) + "/"

    def update_ta_detail(self, taDetail, numOfWeeks, isCompleted):
        self.taDetail = taDetail
        self.numOfWeeks = numOfWeeks
        self.isCompleted = isCompleted
        self.save()

    def initiate_tr_approval_proccess(self, request):
        error_messages = merge_dictionaries({'fatal_errors': '', 'other_errors': []}, ProcessType.initialize_approval_process(form=self, approval_proccess_object_type=TRApprovalProcess, request=request))
        return error_messages

    @staticmethod
    def get_emp_travel_rems(employee):
        cursor = connection.cursor()
        result = []
        cursor.execute(
            'SELECT DISTINCT emp_info."formID", (SELECT COUNT(*) FROM travel_temporaryapprovalstage WHERE travel_temporaryapprovalstage."formID_id" = emp_info."formID") AS "totalStages", '
            'emp_info."travelType", "startDate", "endDate", emp."firstName", emp."middleName", emp."lastName", ta_detail."currentStage", ta_detail."isCompleted", approval_stage."actionTaken", ta_detail."isApproved", ta_detail."isDeclined" '
            'FROM travel_traveldetail '
            'INNER JOIN travel_employeeInformation AS emp_info '
            'ON travel_traveldetail."formID_id" = emp_info."formID" '
            'INNER JOIN office_app_employeedepartment AS empdept '
            'ON empdept."associateID_id" = emp_info."employee_id" '
            'INNER JOIN office_app_employee AS emp '
            'ON empdept."associateID_id" = emp."associateID"'
            'INNER JOIN office_app_costcenter AS dept '
            'ON dept."costCenterCode" = empdept."departmentID_id" '
            'INNER JOIN travel_TADetails AS ta_detail '
            'ON ta_detail."taDetail_id" = emp_info."formID" '
            'JOIN travel_TRApprovalProcess AS approval_stage '
            'ON approval_stage."formID_id" = ta_detail."taDetail_id" '
            'WHERE ta_detail."currentStage" = approval_stage."stage" '
            'AND emp_info."employee_id" = %s ', [employee]
        )
        try:
            for row in cursor.fetchall():
                result.append(dict(zip([col[0] for col in cursor.description], row)))
        except:
            return {"data": result}

        return {"data": result}

    @staticmethod
    def get_approvers_travel_rems(employee):
        cursor = connection.cursor()
        result = []
        cursor.execute(
            'SELECT null as formType, emp_info."formID", emp."firstName", emp."middleName", emp."lastName", dept."costCenterName" as department, ta_detail."currentStage", '
            'approvalstage."actionTaken", approvalstage."stage" as "tempStage", approvalstage."date", ta_detail."isApproved", ta_detail."isDeclined" '
            'FROM travel_traveldetail '
            'INNER JOIN travel_employeeInformation AS emp_info '
            'ON travel_traveldetail."formID_id" = emp_info."formID" '
            'INNER JOIN office_app_employeedepartment AS empdept '
            'ON empdept."associateID_id" = emp_info."employee_id"'
            'INNER JOIN office_app_employee AS emp '
            'ON empdept."associateID_id" = emp."associateID"'
            'INNER JOIN office_app_costcenter AS dept '
            'ON dept."costCenterCode" = empdept."departmentID_id" '
            'INNER JOIN travel_TADetails AS ta_detail '
            'ON ta_detail."taDetail_id" = emp_info."formID" '
            'INNER JOIN travel_TRApprovalProcess AS approvalstage '
            'ON ta_detail."taDetail_id" = approvalstage."formID_id" '
            'WHERE %s = approvalstage."approverID_id" '
            'AND ta_detail."currentStage" >= approvalstage."stage" '
            'AND approvalstage."stage" > %s', [employee, 0]
        )
        try:
            for row in cursor.fetchall():
                result.append(dict(zip([col[0] for col in cursor.description], row)))
        except:
            return {"data": result}

        return {"data": result}

    @property
    def formID(self):
        return self.taDetail.formID

    @property
    def company(self):
        return self.taDetail.company

    @property
    def businessGroup(self):
        return self.taDetail.businessGroup

    @property
    def businessUnit(self):
        return self.taDetail.businessUnit

    @property
    def costCenter(self):
        return self.taDetail.budgetSourceCode

    @property
    def employeeName(self):
        return self.taDetail.employee.lastName + ', ' + self.taDetail.employee.firstName

    @property
    def employee(self):
        return self.taDetail.employee


class TRWeek(models.Model):
    weekID = models.BigAutoField(primary_key=True)
    formID = models.ForeignKey(TADetails, on_delete=models.CASCADE)
    startDate = models.DateField(blank=True, null=True)
    endDate = models.DateField(blank=True, null=True)

    '''
    This function takes a list of tuples and creates a week for each tuple. If there are two tuples with the
    same dates, it only creates one week, not two
    :param tuple_list: The list of tuples used to create a new week. Element 0 of tuple is start date and Element 1 of tuple is end date
    :param travel_reimbursement: The TRDetail object that the weeks belong to
    '''
    @staticmethod
    def create_multiple_TRWeeks(tuple_list, travel_reimbursement):
        already_added_weeks = []
        for week in tuple_list:
            if week not in already_added_weeks:
                new_TRWeek = TRWeek()
                new_TRWeek.save_tr_week(formID=travel_reimbursement, startDate=week[0], endDate=week[1])
                already_added_weeks.append(week)

    def save_tr_week(self, formID, startDate, endDate):
        self.formID = formID
        # Fields user could leave empty:
        if startDate != '':
            self.startDate = startDate
        if endDate != '':
            self.endDate = endDate
        self.save()


class TRDay(models.Model):
    weekID = models.ForeignKey(TRWeek, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)

    def save_tr_day(self, weekID, date):
        self.weekID = weekID
        if date != '':
            self.date = date
        self.save()

    @property
    def dayID(self):
        return self.pk


class Mileage(models.Model):
    miles = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fromLocation = models.CharField(max_length=250, blank=True, null=True)
    toLocation = models.CharField(max_length=250, blank=True, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    glAccount = models.ForeignKey(GLAccount, on_delete=models.CASCADE, blank=True, null=True)
    supportingDoc = models.FileField(upload_to='media/travel/mileage_expenses', blank=True, null=True)

    # def delete(self):
    #     self.supportingDoc.delete()

    def replace_file(self, file):
        if self.supportingDoc is not None:
            self.supportingDoc.delete(save=True)
            # os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))
            self.supportingDoc = file
            self.save()
        else:
            try:
                self.supportingDoc = file
                self.save()
            except FileNotFoundError:
                print("There is no file in this field.")
            except:
                print("Unexpected error found.")

    def __str__(self):
        return 'Cost for ' + str(self.miles) + ' miles: ' + str(self.amount)


    def save_mileage(self, miles, fromLoc, toLoc, amount, glAccount, supportingDoc):
        if miles != '' and miles != 'None':
            self.miles = float(miles)
        else:
            self.miles = None
        if fromLoc != '':
            self.fromLocation = str(fromLoc)
        if toLoc != '':
            self.toLocation = str(toLoc)
        try:
            if amount != '':
                self.amount = float(amount)
            else:
                self.amount = 0
        except:
            if amount != [] and amount[0].isdigit():
                print("AMOUNT:" + amount[0] + ":")
                self.amount = float(amount[0])
            else:
                self.amount = 0
        if glAccount != None:
            self.glAccount = glAccount
        if supportingDoc != '' and supportingDoc != None:
            self.supportingDoc = supportingDoc
        self.save()


class DailyMileage(models.Model):
    listID = models.IntegerField(primary_key=False, blank=True, null=True)
    mileage = models.ForeignKey(Mileage, on_delete=models.CASCADE)
    dayID = models.ForeignKey(TRDay, on_delete=models.CASCADE, blank=True, null=True)

    def save_daily_mileage_entry(self, dayID, mileage):
        if dayID != None:
            self.dayID = dayID
        self.mileage = mileage
        self.save()


class ExpenseType(models.Model):
    typeName = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return 'Expense Type: ' + self.typeName

    def save_expense_type(self, expenseName):
        self.typeName = expenseName
        self.save()


class ItemType(models.Model):
    itemName = models.CharField(max_length=100, primary_key=True)
    glAccount = models.ForeignKey(GLAccount, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return 'Item Type: ' + self.itemName

    def save_item_type(self, itemName, glAccount):
        self.itemName = itemName
        self.glAccount = glAccount
        self.save()


class EmployeeExpenses(models.Model):
    expenseID = models.BigAutoField(primary_key=True)
    dayID = models.ForeignKey(TRDay, on_delete=models.CASCADE, blank=True, null=True)
    expenseType = models.ForeignKey(ExpenseType, on_delete=models.CASCADE)
    itemType = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fieldName = models.CharField(max_length=100, blank=True, null=True)

    def save_expense(self, expenseType, itemType, amount, fieldName, dayID):
        self.expenseType = expenseType
        self.itemType = itemType
        self.dayID = dayID
        self.fieldName = fieldName
        # Fields user could leave empty:
        if amount != '':
            self.amount = amount
        self.save()


class BusinessExpenseExplanation(models.Model):
    dayID = models.ForeignKey(TRDay, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    purpose = models.CharField(max_length=200, blank=True, null=True)
    detail = models.CharField(max_length=200, blank=True, null=True)
    place = models.CharField(max_length=200, blank=True, null=True)
    counterParty = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=70, blank=True, null=True)
    title = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return 'Misc. Explanation: ' + str(self.purpose)

    def save_be_explanation(self, dayID, amount, purpose, place, counterParty, name, title, detail):
        if dayID is not None:
            self.dayID = dayID
        self.save()
        if amount != '':
            self.amount = float(amount)
        self.save()
        if purpose != '':
            self.purpose = purpose
        self.save()
        if place != '':
            self.place = place
        self.save()
        if counterParty != '':
            self.counterParty = counterParty
        self.save()
        if name != '':
            self.name = name
        self.save()
        if title != '':
            self.title = title
        self.save()
        if detail != '':
            self.detail = detail
        self.save()


class ExpenditureType(models.Model):
    expenditureType = models.CharField(primary_key=True, max_length=100)
    glAccount = models.ForeignKey(GLAccount, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return 'Expenditure Type: ' + self.expenditureType

    def save_exp_type(self, expenditureType, glAccount):
        self.expenditureType = expenditureType
        self.glAccount = glAccount
        self.save()


class ExpendituresCharged(models.Model):
    dayID = models.ForeignKey(TRDay, on_delete=models.CASCADE, blank=True, null=True)
    fieldName = models.CharField(max_length=100, blank=True, null=True)
    expenditureType = models.ForeignKey(ExpenditureType, on_delete=models.CASCADE, blank=True, null=True)
    expenditureCost = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def save_expenditures_charged(self, expenditureType, expenditureCost, dayID, fieldName):
        self.dayID = dayID
        try:
            self.expenditureCost = float(expenditureCost)
        except:
            print("Error saving expenditure cost")
        self.expenditureType = expenditureType
        self.fieldName = fieldName
        self.save()


class TRGLAccount(models.Model):
    trForm = models.ForeignKey(TADetails, on_delete=models.CASCADE, blank=True, null=True)
    glAccount = models.ForeignKey(GLAccount, on_delete=models.CASCADE, blank=True, null=True)
    sectionName = models.CharField(max_length=10, blank=True, null=True)

    @property
    def formID(self):
        return self.trForm.formID


class TRApprovalProcess(models.Model):
    formID = models.ForeignKey(TADetails, on_delete=models.CASCADE)
    approverID = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True, to_field='associateID')
    stage = models.IntegerField(primary_key=False, default=0)
    count = models.IntegerField(primary_key=False, default=0)
    actionTaken = models.CharField(max_length=50, default=None, blank=True, null=True)
    comments = models.CharField(max_length=255, default=None, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    dayAssigned = models.DateTimeField(blank=True, null=True)
    approvalType = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.approverID) + " stage " + str(self.stage) + " for " + str(self.formID)

    def set_action_taken(self, actionTaken):
        self.actionTaken = actionTaken
        self.save()

    def create_approval_stage(self, formID, approverID, stage, count):
        self.formID = formID
        self.approverID = approverID
        self.stage = stage
        self.count = count
        self.save()

    def count_approvers(self):
        temp = TRApprovalProcess
        rows = temp.objects.filter(stage=self.stage, formID=self.formID)
        ctr = 0
        for row in rows:
            ctr += 1
        return ctr

    def count_approved_forms_for_stage(self):
        temp = TRApprovalProcess
        rows = temp.objects.filter(stage=self.stage, formID=self.formID, count=1)
        ctr = 0
        for row in rows:
            ctr += 1
        return ctr


class TRModifiedFields(models.Model):
    formID = models.IntegerField(unique=False)
    fieldID = models.CharField(max_length=50, null=True)
    fieldData = models.CharField(max_length=250, null=True)
    expenseID = models.ForeignKey(EmployeeExpenses, on_delete=models.CASCADE, blank=True, null=True)
    expenditureID = models.ForeignKey(ExpendituresCharged, on_delete=models.CASCADE, blank=True, null=True)

    def save_TRModifiedField(self, formID, fieldID, fieldData, expenseID, expenditureID):
        self.formID = formID
        self.fieldID = fieldID
        print("INSIDE fieldID: " + fieldID)
        self.fieldData = fieldData
        print("INSIDE fieldData: " + str(fieldData))
        self.expenseID = expenseID
        self.expenditureID = expenditureID
        self.save()


class AdvanceReimbursementApp(models.Model):
    advID = models.BigAutoField(primary_key=True)
    form = models.ForeignKey(TADetails, on_delete=models.CASCADE)
    invoiceNo = models.CharField(max_length=25, blank=True, null=True)
    advAmount = models.DecimalField(max_digits=10, decimal_places=2)
    costCenterCode = models.CharField(max_length=50, blank=True, null=True)
    profitCenter = models.CharField(max_length=50, blank=True, null=True)
    headText = models.CharField(max_length=50, blank=True, null=True)
    text = models.CharField(max_length=50, blank=True, null=True)
    assignment = models.CharField(max_length=100, blank=True, null=True) # vendorcode,costcentercode
    isCompleted = models.BooleanField(default=False, null=True)
    currency = models.CharField(max_length=50, blank=True, null=True)
    dateApplied = models.DateField(blank=True, null=True)
    dateApproved = models.DateField(blank=True, null=True)
    companyCode = models.CharField(max_length=50, blank=True, null=True)
    vendorCode = models.CharField(max_length=15, blank=True, null=True)
    taDocNo = models.CharField(max_length=25, blank=True, null=True)
    glCode = models.CharField(max_length=50, blank=True, null=True)

    # region methods
    def save_advance_reimbursement(self, form, invoiceNo, advAmount, costCenterCode, profitCenter, headText, text,
                                   assignment, isCompleted, currency, dateApplied, dateApproved, companyCode,
                                   vendorCode, taDocNo, glCode):
        self.form = form
        if is_nothing(invoiceNo) == False:
            self.invoiceNo = invoiceNo
        #print("advance amount before:" + str(self.advAmount))
        if is_nothing(advAmount) == False:
            self.advAmount = advAmount
        #print("advance amount after:" + str(self.advAmount))
        if is_nothing(costCenterCode) == False:
            self.costCenterCode = costCenterCode
        if is_nothing(profitCenter) == False:
            self.profitCenter = profitCenter
        if is_nothing(headText) == False:
            self.headText = headText
        if is_nothing(text) == False:
            self.text = text
        if is_nothing(assignment) == False:
            self.assignment = assignment
        if is_nothing(isCompleted) == False:
            self.isCompleted = isCompleted
        if is_nothing(currency) == False:
            self.currency = currency
        if is_nothing(dateApplied) == False:
            self.dateApplied = dateApplied
        if is_nothing(dateApproved) == False:
            self.dateApproved = dateApproved
        if is_nothing(companyCode) == False:
            self.companyCode = companyCode
        if is_nothing(vendorCode) == False:
            self.vendorCode = vendorCode
        if is_nothing(taDocNo) == False:
            self.taDocNo = taDocNo
        if is_nothing(glCode) == False:
            self.glCode = glCode
        self.save()
    # endregion

    # region Properties
    @property
    def formID(self):
        return self.form.formID

    @property
    def vendorName(self):
        return Vendors.objects.get(vendorCode=self.vendorCode).vendorName

    # @property
    # def vendorCode(self):
    #     return self.vendorCode

    @property
    def vendorAddress(self):
        return Vendors.objects.get(vendorCode=self.vendorCode).supplierAddress

    @property
    def vendorContact(self):
        return Vendors.objects.get(vendorCode=self.vendorCode).supplierContact

    @property
    def vendorTelephone(self):
        return Vendors.objects.get(vendorCode=self.vendorCode).supplierTelephone
    # endregion Properties


class TRFilesLink(models.Model):
    form = models.ForeignKey(EmployeeInformation, on_delete=models.CASCADE)

    @property
    def formID(self):
        return self.form.formID

    def get_files(self):  # <-- This should work but I'm not certain
        return TRFileUpload.objects.filter(formLink=self)

    def get_files_in_folder(self, folder_name):
        return TRFileUpload.objects.filter(formLink=self, location__contains='travel/' + folder_name)


class TRFileUpload(models.Model):
    formLink = models.ForeignKey(TRFilesLink, on_delete=models.CASCADE)
    location = models.CharField(max_length=500, default='travel/')  # Ex: travel/personal-expenses
    file = models.FileField(upload_to=get_upload)

    @property
    def formID(self):
        return self.formLink.form.formID

    @property
    def fileName(self):
        return str(self.file).split(self.location, 1)[1]

    def replace_personal_file(self, file):
        if self.personalExpenses is not None:
            self.personalExpenses.delete(save=True)
            # os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))
            self.personalExpenses = file
            self.save()
        else:
            try:
                self.personalExpenses = file
                self.save()
            except FileNotFoundError:
                print("There is no file in this field.")
            except:
                print("Unexpected error found.")

    def replace_business_file(self, file):
        if self.businessExpenses is not None:
            self.businessExpenses.delete(save=True)
            self.businessExpenses = file
            self.save()
        else:
            try:
                self.businessExpenses = file
                self.save()
            except FileNotFoundError:
                print("There is no file in this field.")
            except:
                print("Unexpected error found.")

    def replace_proof_file(self, file):
        if self.proofOfPayment is not None:
            self.proofOfPayment.delete(save=True)
            self.proofOfPayment = file
            self.save()
        else:
            try:
                self.proofOfPayment = file
                self.save()
            except FileNotFoundError:
                print("There is no file in this field.")
            except:
                print("Unexpected error found.")


class SAPTravelApp(models.Model):
    sapDataID = models.BigAutoField(primary_key=True)
    formID = models.ForeignKey(EmployeeInformation, on_delete=models.CASCADE)
    headerText = models.CharField(max_length=100)
    invoiceNumber = models.CharField(max_length=100)
    glAccount = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    assignment = models.CharField(max_length=100)
    itemText = models.CharField(max_length=100)
    costCenterCode = models.CharField(max_length=50)
    taDocNumber = models.CharField(max_length=50)
    vendorCode = models.CharField(max_length=50)
    currency = models.CharField(max_length=50)
    invoiceDate = models.DateField(auto_now=True)

    @staticmethod
    def create_entries(formID):
        temp_entry = SAPTravelApp()
        # temp_travel_app = EmployeeInformation.objects.get(formID=formID)
        #
        # temp_entry.formID = temp_travel_app.formID
        # # temp_entry.glAccount = ?
        # # temp_entry.assignment = ?
        # temp_entry.currency = temp_travel_app


class SAPAdvApp(models.Model):
    sapDataID = models.BigAutoField(primary_key=True)
    formID = models.ForeignKey(EmployeeInformation, on_delete=models.CASCADE)
    advAmount = models.DecimalField(max_digits=10, decimal_places=2)
    glAccount = models.CharField(max_length=50, blank=True, null=True)
    glDescription = models.CharField(max_length=50, blank=True, null=True)
    costCenterCode = models.CharField(max_length=50, blank=True, null=True)
    profitCenter = models.CharField(max_length=50, blank=True, null=True)
    headText = models.CharField(max_length=50, blank=True, null=True)
    text = models.CharField(max_length=50, blank=True, null=True)
    assignment = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=50, blank=True, null=True)
    refDocument = models.CharField(max_length=50, blank=True, null=True)
    dateApplied = models.DateField(blank=True, null=True)
    dateApproved = models.DateField(blank=True, null=True)
    companyCode = models.CharField(max_length=50, blank=True, null=True)
    vendorCode = models.CharField(max_length=15, blank=True, null=True)

    @staticmethod
    def create_entries(advID):
        temp_entry = SAPAdvApp()
        temp_adv_app = AdvanceTravelApp.objects.get(advID=advID)

        temp_entry.formID = temp_adv_app.formID
        temp_entry.advAmount = temp_adv_app.advAmount
        temp_entry.glAccount = temp_adv_app.glAccount
        temp_entry.glDescription = temp_adv_app.glDescription
        temp_entry.costCenterCode = temp_adv_app.costCenterCode
        temp_entry.profitCenter = temp_adv_app.profitCenter
        temp_entry.headText = temp_adv_app.headText
        temp_entry.text = temp_adv_app.text
        temp_entry.assignment = temp_adv_app.assignment
        temp_entry.currency = temp_adv_app.currency
        temp_entry.refDocument = temp_adv_app.refDocument
        temp_entry.dateApplied = temp_adv_app.dateApplied
        temp_entry.dateApproved = temp_adv_app.dateApproved
        temp_entry.companyCode = temp_adv_app.companyCode
        temp_entry.vendorCode = None
        temp_entry.save()

        temp_entry = SAPAdvApp()
        temp_entry.formID = temp_adv_app.formID
        temp_entry.advAmount = temp_adv_app.advAmount
        temp_entry.glAccount = None
        temp_entry.glDescription = None
        temp_entry.costCenterCode = temp_adv_app.costCenterCode
        temp_entry.profitCenter = temp_adv_app.profitCenter
        temp_entry.headText = temp_adv_app.headText
        temp_entry.text = temp_adv_app.text
        temp_entry.assignment = temp_adv_app.assignment
        temp_entry.currency = temp_adv_app.currency
        temp_entry.refDocument = temp_adv_app.refDocument
        temp_entry.dateApplied = temp_adv_app.dateApplied
        temp_entry.dateApproved = temp_adv_app.dateApproved
        temp_entry.companyCode = temp_adv_app.companyCode
        temp_entry.vendorCode = temp_adv_app.vendorCode
        temp_entry.save()


class FormChat(models.Model):
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    formID = models.IntegerField(blank=True, null=True)
    message = models.TextField()
    sentOn = models.DateTimeField()
    formType = models.CharField(max_length=50, blank=True, null=True)
