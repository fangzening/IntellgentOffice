from django.urls import path, include
from travel import views
from smart_hr import views as smart_hr_views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('submit', views.submit),
    path('', views.travel_home, name='travel_home'),
    path('travel_application', views.travel_application, name='travel_application'),
    path('travel_application/send_validation', views.travel_application, name='travel_app_send_validation'),
    path('travel_list/', views.forms_to_approve_view, name='travel_list'),
    path('travel_application/<slug:pk>/', views.approve_form_view, name='approve_form'),
    path('submitted_forms/', views.submitted_forms_view, name='submitted_forms'),
    path('travel_forms_json/', views.get_travel_form_json, name='travel_forms_json'),
    path('my_travel_forms_json/', views.get_my_travel_form_json, name='my_travel_forms_json'),
    path('travel_reimbursement/<slug:pk>/', views.travel_reimbursement_view, name='travel_reimbursement'),
    path('see_rem_page/', views.test_rem_view, name='test_reimbursement'),
    path('my_travel_rem_json/', views.get_travel_rem_json, name='my_travel_rem_json'),
    path('my_travel_rem/', views.my_TR_forms_view, name='my_travel_rem'),
    path('travel_rem_list/', views.travel_rem_list, name='travel_rem_list'),
    path('travel_rem_list_json/', views.travel_rem_list_json, name='travel_rem_list_json'),
    path('user_manual/', views.user_guide, name='user_manual'),
    path('guide_info/', views.guide_info, name='guide_info'),

    # for PDF Generator (inside smart-hr module)
    path('paf_create', smart_hr_views.paf_create, name='paf_create'),
    path('paf_list', smart_hr_views.paf_list, name='paf_list'),
    path('paf_json', smart_hr_views.paf_json, name='paf_json'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


