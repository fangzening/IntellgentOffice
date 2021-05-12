from django.contrib import admin

# Register your models here.
from expense.models import *

admin.site.register(Expense)
admin.site.register(ExpenseItem)
admin.site.register(Currency)
admin.site.register(ApproverList)
admin.site.register(ApproverStatus)
admin.site.register(Attachment)
admin.site.register(ApproverAssignment)