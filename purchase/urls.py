from django.urls import path, include
from purchase import views
from smart_hr import views as smart_hr_views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from purchase import pr_custom_functions

urlpatterns = [
    path('', views.pr_dashboard, name='purchase_dashboard'),
    path('submitted_purchase', views.my_purchase, name='submitted_purchase'),
    path('purchase_to_approve', views.approve_purchase_list, name='purchase_to_approve'),
    path('my_purchase_api', views.my_purchase_api, name='my_purchase_api'),
    path('purchase_to_approve_api/', views.purchase_to_approve_api, name='purchase_to_approve_api'),
    path('units_of_measure_api', views.UoM, name='units_of_measure_api'),

    path('all_purchase_form', views.all_purchase_form, name='all_purchase_form'),
    path('all_purchase_form_api', views.all_purchase_form_api, name='all_purchase_form_api'),

    path('print_pr', views.print_pr, name ='print_pr'),
    path('<slug:pk>/', views.PurchaseRequest, name='purchase_request'), # slug is formID

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
