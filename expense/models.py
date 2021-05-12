from django.db import models
from decimal import *
from Smart_Office.settings import MEDIA_ROOT
from datetime import datetime
from Smart_Office.settings import DATE_INPUT_FORMATS
from office_app.models import Employee, BusinessUnit, BusinessGroup, GLAccount, LegalEntity, EmployeeDepartment,CostCenter,Vendors
import datetime
import os
from django.core.files import File
# Create your models here.
# The basic structure of an expense form.

class Currency(models.Model):
      name=models.CharField(max_length=20,primary_key=True)

      def __str__(self):
          return self.name


class Expense(models.Model):
       requester = models.ForeignKey(Employee, on_delete=models.CASCADE,related_name="expense_requester",to_field='associateID')
       id = models.BigAutoField(primary_key=True)
       form_ID = models.TextField(null=True)
       payment_Date=models.DateField()
       request_Date=models.DateField()
       post_Date=models.DateField(null=True,blank=True)
       # company=models.ForeignKey(LegalEntity,on_delete=models.CASCADE)
       BU=models.ForeignKey(BusinessUnit,on_delete=models.CASCADE)# this is used to decide the approval proccess
       # BG=models.ForeignKey(BusinessGroup,on_delete=models.CASCADE)
       company = models.ForeignKey(LegalEntity,on_delete=models.CASCADE)
       company_Code=models.CharField(max_length=8)
       document_Header=models.CharField(max_length=64,null=True,blank=True)
       invoice_ID=models.CharField(max_length=20)
       vendor=models.ForeignKey(Vendors,on_delete=models.CASCADE,related_name="expense_vendor")
       vendor_Code=models.CharField(max_length=15, blank=True, null=True)
       tax_Rate=models.DecimalField(max_digits=5, decimal_places=4)
       sales_Tax_Amount=models.DecimalField(max_digits=15, decimal_places=2)
       shipping_Cost=models.DecimalField(max_digits=15, decimal_places=2)
       ground_Total = models.DecimalField(max_digits=15, decimal_places=2)
       # post_Date=models.DateField()
       apnumber=models.CharField(max_length=32,null=True,blank=True)
       currency=models.CharField(max_length=20)
       cost_Center=models.ForeignKey(CostCenter,on_delete=models.CASCADE,related_name='expense_cost_center',blank=True, null=True)

       def __str__(self):
           return 'Expense Form: ' + str(self.form_ID)

       def form_type(self):
           return "Expense"

       def save(self, *args, **kwargs):
           self.sales_Tax_Amount = self.get_sales_tax_amount
           self.ground_Total=self.get_ground_total
           # self.form_ID = self.get_formID()
           super(Expense, self).save(*args, **kwargs)


           # sales tax amount is auto-caculated based on user input
       @property
       def get_sales_tax_amount(self):
           item_subtotal = Decimal(0.0)

           for t in self.expenseitem_set.all():
               if t.active_Status == ExpenseItem.ACTIVE:
                       item_subtotal += t.amount

           return (item_subtotal+self.shipping_Cost)*self.tax_Rate

       # Ground total is auto-caculated based on user input
       @property
       def get_ground_total(self):
              item_subtotal=Decimal(0.0)
              for t in  self.expenseitem_set.all():#ExpenseItem.get_all_items_by_expense(self.form_ID):
                     if t.active_Status==ExpenseItem.ACTIVE:
                         item_subtotal+=t.amount
              accrued_tax_amount=item_subtotal*self.tax_Rate
              return item_subtotal+self.shipping_Cost+self.get_sales_tax_amount


       #get the cutomized ID
       def get_formID(self):
           today = datetime.datetime.today()
           return "EXP" + str(today.year) + str(today.month) + str(today.day) + str(self.id)

       #retrive the expenses that need to be approved by the employee according to the associate ID
       @staticmethod
       def get_expense_to_approve_by_id(aid):
           employeedept = EmployeeDepartment.objects.get(associateID=aid)#get corresponding EmployeeDepartment
           approver_status_list=employeedept.approverstatus_set.all()#get all approverStatus by EmployeeDepartment
           expense_list=[]
           for app_sta in approver_status_list:
               applist=app_sta.approver_list
               if applist.status == ApproverList.PENDING and applist.currentStage==app_sta.stage and app_sta.status==ApproverStatus.PENDING:# only if the current stage equals EmployeeDepartment's stage and the approve process is still pending,we display it at the front pages
                  expense_list.append(applist.expense)
           return expense_list

           # this method is used to retrieve all the expense forms that applied by this employee
       @staticmethod
       def get_expense_history_by_id(aid):
               employee = Employee.objects.get(associateID=aid)
               return employee.expense_requester.all()

       # this is used to set cost center for shipping and sales tax
       def set_cost_center(self):
           items=ExpenseItem.objects.filter(expense__form_ID=self.form_ID)
           amount_dic={}
           cCode=""
           cAmount=0
           for item in items:
                if item.cost_Center.costCenterCode in amount_dic:
                    amount_dic[item.cost_Center.costCenterCode] += item.amount
                    if cAmount <= amount_dic[item.cost_Center.costCenterCode]:
                        cAmount=amount_dic[item.cost_Center.costCenterCode]
                        cCode=item.cost_Center.costCenterCode
                else:
                    amount_dic[item.cost_Center.costCenterCode]=item.amount
                    if cAmount<=item.amount:
                        cAmount=item.amount
                        cCode=item.cost_Center.costCenterCode
           self.cost_Center=CostCenter.objects.get(costCenterCode=cCode)

       class Meta:
              ordering = ['request_Date']


class ExpenseItem(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    cost_Center = models.ForeignKey(CostCenter,on_delete=models.CASCADE,related_name='cost_center_expense_item')# to field cost_center_code
    # cost_Center_Name = models.TextField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    STATUS_CHOICES = [(ACTIVE, 'active'), (INACTIVE, 'inactive')]
    active_Status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    USE_TAX = 'use_tax'
    ASSET = 'asset'
    NOAPP = 'null'
    TYPE_CHOICES = [(USE_TAX, 'use_tax'), (ASSET, 'asset'),(NOAPP,'null')]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=NOAPP)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    asset_number = models.CharField(max_length=32,null=True,blank=True)
    asset_subnumber = models.CharField(max_length=4,null=True,blank=True)
    # asset_amount = models.DecimalField(max_digits=15, decimal_places=2,null=True,blank=True)
    # asset_quantity = models.IntegerField(default=0, null=True,blank=True)
    GL = models.ForeignKey(GLAccount, on_delete=models.CASCADE,null=True,blank=True)  # this is the GLCode
    CREDIT = 'C'
    DEBIT = 'D'
    CARD_CHOICES = [(CREDIT, 'credit'), (DEBIT, 'debit'),(NOAPP,'null')]
    card_Type = models.CharField(max_length=10, choices=CARD_CHOICES, default=NOAPP)
    text = models.TextField(null=True,blank=True)
    assignment = models.TextField(null=True,blank=True)

    @staticmethod
    def get_all_items_by_expense(form_ID):
          return ExpenseItem.objects.filter( expense__form_ID=form_ID )



    # def save(self, *args, **kwargs):
    #    self.cost_Center_Name = CostCenter.objects.filter()[0].cost_Center_Name
    #    super(Expense, self).save(*args, **kwargs)


class Attachment(models.Model):
    attachments = models.FileField(upload_to="expense/attachments/")#no need to add prefix to make relative path cause we've already get MEDIA_ROOT
    description=models.TextField()
    expense=models.ForeignKey(Expense,on_delete=models.CASCADE,related_name='attachments')

    def filename(self):
        return os.path.basename(self.attachments.name)




# class UseTax(models.Model):# if this is just expense
#     GL=models.ForeignKey(GLAccount,on_delete=models.CASCADE)#this is the GLCode
#     CREDIT = 'C'
#     DEBIT = 'D'
#     CARD_CHOICES = [(CREDIT, 'credit'), (DEBIT, 'debit')]
#     card_Type = models.CharField(max_length=10, choices=CARD_CHOICES, default=CREDIT)
#     text = models.TextField()
#     assignment = models.TextField()
#     item = models.ForeignKey(ExpenseItem, on_delete=models.CASCADE,related_name="item_expense")
#
#
#     # def save(self, *args, **kwargs):
#     #    self.cost_Center_Name = self.cost_Center_cost_Center_Name
#     #    super(Expense, self).save(*args, **kwargs)
#
# class Asset(models.Model):
#     asset_number=models.CharField(max_length=32)
#     amount=models.DecimalField(max_digits=15, decimal_places=2)
#     quantity=models.IntegerField(default=0)
#     item = models.ForeignKey(ExpenseItem, on_delete=models.CASCADE,related_name="item_asset")


class ApproverList(models.Model):
     currentStage=models.IntegerField(primary_key=False,default=0)
     APPROVAL = 'Approved'
     REJECTION = 'Rejected'
     PENDING = 'Pending'
     STATUS_CHOICES = [(APPROVAL, 'approved'), (REJECTION, 'rejected'), (PENDING, 'pending')]
     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
     expense=models.ForeignKey(Expense,on_delete=models.CASCADE)
     maxStage=models.IntegerField(primary_key=False,default=0)
    #  currentIndex=0
    #  approverlist=[]

     def get_max_stage(self):
         # approverlist=self.approverstatus_set.all().order_by('stage')
         maxStage=self.approverstatus_set.all().order_by('-stage')[0].stage
         return maxStage

     #get all current approvers for this stage
     # def get_current_approvers(self):
     #     aprrovers=[]
     #     i = 0;
     #     app_list = self.approverstatus_set.all().order_by('stage')
     #     approverlist=self.approverstatus_set.all()
     #     while i < len(app_list):



      # move the current stage to the next level
     # and remember not to call this method at creation stage because I've already added cm at stage 0
     def update_current_stage(self):
         i=0;
         app_list=self.approverstatus_set.all().order_by('stage')
         while i<len(app_list):
             if self.currentStage==app_list[i].stage and app_list[i].status==ApproverStatus.PENDING:# means the current is still pending
                self.currentStage=app_list[i].stage
                break
             elif self.currentStage<app_list[i].stage:# get the first stage that higher than current
                 self.currentStage=app_list[i].stage
                 break
             i+=1
             if i==len(app_list):
                 self.currentStage=self.maxStage+1
                 # print(app_list[i-1].status)
                 # if app_list[i-1].status=="approved":
                 #     self.status=self.APPROVAL
                 # elif app_list[i-1].status=="rejected" :
                 #     self.status=self.REJECTION

     # this is the method used to approve or reject the current stage
     # params:
     #  eid: approver associate id;
     #  status: approve or reject or hangup
     # response:
     # true: the stage is still
     # false: the stage has been changed
     def set_current_status(self,eid,status,memo):
         currentstage=self.currentStage
         if status==self.APPROVAL:
             appsta=self.approverstatus_set.get(approver__associateID=eid)
             appsta.status=ApproverStatus.APPROVAL
             appsta.memo=memo
             appsta.date=datetime.datetime.now()
             appsta.save()
             self.update_current_stage()
             if self.maxStage<self.currentStage:
                 self.status=self.APPROVAL
         elif status==self.REJECTION:
             appsta = self.approverstatus_set.get(approver__associateID=eid)
             appsta.status = ApproverStatus.REJECTION
             appsta.memo = memo
             appsta.date = datetime.datetime.now()
             appsta.save()
             self.status=self.REJECTION
             self.save()
         return currentstage==self.currentStage


     #this is used to get current approverstatus objects
     def get_current_approverstatus(self):
         appsta_list=self.approverstatus_set.filter(stage=self.currentStage)
         return appsta_list

     def get_approverstatus_byapprover(self,edid):
         app=self.approverstatus_set.get(approver__associateID=edid)
         return app

# The basic info of manager approval or rejection, an approver list consists five ApproverStatus with several separate titles
class ApproverStatus(models.Model):
    APPROVAL='Approved'
    REJECTION='Rejected'
    PENDING='Pending'
    STATUS_CHOICES=[(APPROVAL,'approved'),(REJECTION,'rejected'),(PENDING,'pending')]
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default=PENDING)

    # DEPTMANAGER='DM'
    # COSTMANAGER='CM'
    # CMHEAD='CMH'
    # ACCOUNTING='A'
    # ACCOUNTINGMANAGER='AM'
    # TITLE_CHOICES=[(DEPTMANAGER,'dept manager'),(COSTMANAGER,'cost manager'),(CMHEAD,'CM head'),(ACCOUNTING,'accounting'),(ACCOUNTINGMANAGER,'accounting manager')]
    partial = models.BooleanField()# this field indicates whether the approver can partial approve the items
    # title=models.CharField(max_length=64,null=True)
    department=models.CharField(max_length=32,null=True)
    approver=models.ForeignKey(EmployeeDepartment,on_delete=models.CASCADE)
    date=models.DateField(null=True)
    memo=models.TextField(null=True)
    stage=models.IntegerField(primary_key=False, default=0)
    approver_list=models.ForeignKey(ApproverList,on_delete=models.CASCADE)

    class Meta:
        ordering = ['stage']



# this is the approver list based on BU+BG+company, we use this to retrive the corresponding approvers and generate the ApproverStatus above
class ApproverAssignment(models.Model):
    approver = models.ForeignKey(EmployeeDepartment,on_delete=models.CASCADE)
    BU = models.ForeignKey(BusinessUnit,on_delete=models.CASCADE)
    minimum = models.DecimalField(max_digits=15, decimal_places=2)
    stage = models.IntegerField(primary_key=False, default=0)
    department = models.CharField(max_length=32)
    partial = models.BooleanField()
    #List all match data
    @staticmethod
    def get_all_records():
        return ApproverAssignment.objects.all()

    #Retrieve all the approver based on the given BU,BG,company code
    @staticmethod
    def get_approvers(BUstring):
        return ApproverAssignment.objects.filter(BU=BUstring).order_by('stage')

    def __str__(self):
        return str(Employee.get_employee_by_associate_id(self.approver.associateID.associateID)) + ":"+str(self.BU)