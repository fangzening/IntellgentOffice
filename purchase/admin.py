from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(PurchaseBasicInfo)
admin.site.register(PRApprovalProcess)
admin.site.register(PurchaseRequestForm)
admin.site.register(PurchaseItemDetail)
admin.site.register(PurchaseItemAsset)
admin.site.register(SupplierInfo)
admin.site.register(ShippingInfo)
admin.site.register(UnitOfMeasurement)
