from django.urls import path, include
from smart_hr import views

urlpatterns = [
    path('', views.index, name='smart_hr_home'),
    path('checklist_create', views.checklist_create, name='checklist_create'),
    path('checklist_list', views.checklist_list, name='checklist_list'),
    path('checklist_detail/<str:empID>', views.checklist_detail, name='checklist_detail'),
    path('checklist_edit/<str:empID>', views.checklist_edit, name='checklist_edit'),
    path('checklist_json', views.checklist_json, name='checklist_json'),
]
