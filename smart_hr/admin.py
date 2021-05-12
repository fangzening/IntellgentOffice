from django.contrib import admin
from .models import *

# Register your models here.

# *** Written by Zaawar
# Register database table with the admin

admin.site.register(PAF)
admin.site.register(PAFAuthorizer)
admin.site.register(NewHireChecklist)
admin.site.register(ChecklistTask)