from django import forms
# from crispy_forms.helper import FormHelper
import psycopg2
from django.db import connection
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from office_app.models import *
from django.contrib.auth.forms import AuthenticationForm


# make it so create user form also has email, firstname, lastname, dept, and title fields
class RegisterForm(UserCreationForm):
    username = forms.CharField(label="Username",
                               widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'Username'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    firstname = forms.CharField(label="First name", widget=forms.TextInput(attrs={'class': 'form-control'}))
    lastname = forms.CharField(label="Last name", widget=forms.TextInput(attrs={'class': 'form-control'}))
    id = forms.CharField(label="New User Form ID", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ("username", "firstname", "lastname", "email", "id")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data["firstname"]
        user.last_name = self.cleaned_data["lastname"]
        user.email = self.cleaned_data["email"]
        user.id = self.cleaned_data["id"]
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        # attrs={'class': 'user_input', 'placeholder': 'User Name', "name": "username", "type": "text"}
        attrs = {"hidden": "true", "readonly": "true"}
        ))


    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'user_input', 'placeholder': 'Password', "name": "pass", "type": "password"}
    ))

# This class gets the information from the leave application form and submits it to the database DOESNT WORK RIGHT NOW
# class leaveApplicationFormSubmit(forms.Form):
#     applicant_id = forms.CharField(label="Applicant ID")
#     fullname = forms.CharField(label="Full name")
#     address = forms.CharField(label="Address")
#     manager_domain = forms.CharField(label="Manager Domain")
#     manager_name = forms.CharField(label="Manager Name")
#     department = forms.CharField(label="Department")
#     manager_id = forms.CharField(label="Manager ID")
#     leave_start = forms.CharField(label="Leave Start")
#     leave_end = forms.CharField(label="Leave End")
#     email = forms.EmailField(label="Email")
#
#     class Meta:
#         fields = ("applicant_id", "fullname", "address", "manager_domain", "manager_name", "manager_id", "department",
#                   "leave_end", "leave_start", "email")
#
#     def save(self, commit=True):
#         application = super(self).save(commit=False)
#         applicant_id = self.cleaned_data["applicant_id"]
#         fullname = self.cleaned_data["fullname"]
#         address = self.cleaned_data['address']
#         manager_domain = self.cleaned_data['manager_domain']
#         manager_name = self.cleaned_data['manager_name']
#         manager_id = self.cleaned_data['manager_id']
#         department = self.cleaned_data['department']
#         leave_end = self.cleaned_data['leave_end']
#         leave_start = self.cleaned_data['leave_start']
#         email = self.cleaned_data['email']
#
#         if commit:
#             application.save()
#             self.push_to_database(applicant_id, fullname, address,
#                                   manager_domain,
#                                   manager_name, manager_id, department,
#                                   leave_end, leave_start, email)
#             print("Email:" + email)
#         return application
#
#     # This pushes the data from the form into the database:
#     def push_to_database(self, appid, fname, addr, mdmn, mname, mid, dept, leavend, leavestrt, email):
#         cursor = connection.cursor()
#         cursor.execute(
#             'INSERT INTO leave_application_table(applicant_id, fullname, address, manager_domain, manager_name, department, manager_id, leave_start, leave_end, email) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
#             [appid, fname, addr, mdmn, mname, dept, mid,
#              leavestrt, leavend, email])
