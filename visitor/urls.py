from visitor import views
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('create_application', views.create_application, name='visitor_create'),
    path('view_application/<str:id>/', views.view_application, name='visitor_view'),
    path('my_applications', views.my_applications, name='visitor_myforms'),
    path('approve_applications', views.approve_applications, name='visitor_approveforms'),
    path('visitor_api', views.visitor_api, name='visitor_api'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
