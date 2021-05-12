"""Smart_Office URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views
from django.urls import path, include
from office_app.forms import *

urlpatterns = [
                  # Django Admin
                  path('django_admin/', admin.site.urls),

                  # Special login
                  path('accounts/login/',
                       views.LoginView.as_view(
                           template_name="registration/login.html",
                           authentication_form=UserLoginForm
                       ),
                       name='login'
                       ),

                  # Django Auth
                  path('accounts/', include('django.contrib.auth.urls')),

                  # Smart OFfice App
                  path('', include('office_app.urls')),

                  # Smart Hr App
                  path('smart_hr/', include('smart_hr.urls')),

                  # Smart Travel App
                  path('travel/', include('travel.urls')),

                  # Purchase Request
                  path('purchase_request/', include('purchase.urls')),

                  # Expense App
                  path('expense/', include('expense.urls')),

                  # GR Form
                  path('goods_received/', include('goods_received.urls')),

                  # MRO Invoice
                  path('mro_invoice/', include('mro_invoice.urls')),

                  # Visitor App
                  path('visitor/', include('visitor.urls')),

                  # Employee General Data App
                  #      path('employee_data/', include('employee_general_data.urls')),

                # IT App
                path('it/', include('it_app.urls'))

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
