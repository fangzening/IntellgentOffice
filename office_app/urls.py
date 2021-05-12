from django.urls import path
from office_app import views
from django.conf import settings
from django.conf.urls.static import static
from it_app.views import change_password_form, test_email_sending

urlpatterns = [
    # Smart_Office Admin Links
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/module/', views.module, name='module'),
    path('admin/module_api/', views.module_api, name='module_api'),
    path('admin/account/', views.account, name='account'),
    path('admin/account_api/', views.account_api, name='account_api'),
    path('admin/employee/', views.employee, name='employee'),
    path('admin/employee_api/', views.employee_api, name='employee_api'),
    path('admin/costcenter/', views.costcenter, name='costcenter'),
    path('admin/costcenter_api/', views.costcenter_api, name='costcenter_api'),
    path('admin/businessunit/', views.businessunit, name='businessunit'),
    path('admin/businessunit_api/', views.businessunit_api, name='businessunit_api'),
    path('admin/businessgroup/', views.businessgroup, name='businessgroup'),
    path('admin/businessgroup_api/', views.businessgroup_api, name='businessgroup_api'),
    path('admin/legalentity/', views.legalentity, name='legalentity'),
    path('admin/legalentity_api/', views.legalentity_api, name='legalentity_api'),
    path('admin/approver/', views.approver, name='approver'),
    path('admin/approver_api/', views.approver_api, name='approver_api'),
    path('admin/vendor/', views.vendor, name='vendor'), # VENDOR WIP
    path('admin/vendor_api/', views.vendor_api, name='vendor_api'), # VENDOR WIP
    path('admin/combination/', views.combination, name='combination'),
    path('admin/combination_api/', views.combination_api, name='combination_api'),
    path('admin/approval_process/', views.approval_process, name='approval_process'),
    path('admin/approval_process_api/', views.approval_process_api, name='approval_process_api'),
    path('admin/get_information_to_edit_approval_process/', views.get_information_to_edit_approval_process, name='get_approval_process_info'),
    path('admin/ap_tracker/travel_application/', views.ta_ap_tracker, name='ta_ap_tracker'),
    path('admin/ap_tracker_api/travel_application/', views.ta_ap_tracker_api, name='ta_ap_tracker_api'),
    path('admin/ap_tracker/travel_reimbursement/', views.tr_ap_tracker, name='tr_ap_tracker'),
    path('admin/ap_tracker_api/travel_reimbursement/', views.tr_ap_tracker_api, name='tr_ap_tracker_api'),
    path('admin/ap_tracker/purchase_request/', views.pr_ap_tracker, name='pr_ap_tracker'),
    path('admin/ap_tracker_api/purchase_request/', views.pr_ap_tracker_api, name='pr_ap_tracker_api'),

    # Smart_Office Links
    path('', views.dashboard_view, name='smart_office_dashboard'),
    path('contact_us/', views.contact_view, name='contact_us'),
    path('ocr', views.ocr, name='ocr'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications_api/', views.notifications_api, name='notifications_api'),
    path('messages/', views.messages, name='messages'),
    path('messages_api/', views.messages_api, name='messages_api'),
    path('user/change_password/', change_password_form, name='change_password'),
    path('chat_api/', views.chat_api, name='chat_api'),
    path('get_form_approvers_api/', views.get_form_approvers_api, name='get_form_approver_api'),

    # path('leave_application/', views.LeaveForm, name='leave_application'),
    # path('403Error/', TemplateView.as_view(template_name='office_app/403_error.html'), name='Error_403'),
    # path('approve_forms/', views.approveFormsView, name='approve_forms'),
    # path('404/', views.error404view, name='Error_404'),
    path('send_fake_email/', test_email_sending),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
