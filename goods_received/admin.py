from django.contrib import admin

# Register your models here.
from goods_received.models import *

admin.site.register(GRForm)
admin.site.register(GRList)
admin.site.register(GRApproversProcess)