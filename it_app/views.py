import csv
import socket

import openpyxl
import xlsxwriter
import datetime
import enum
import http
import logging
import sys
import traceback

import SAP.SAPFunctions
import SAP.SAPFunctionsPrd
from SAP.SAPFunctions import createAP
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login


# Create your views here.
from office_app.services import EmailHandler
from it_app.models import UserPasswordChange
from .tests import *
from io import BytesIO


def clean_str(temp_str):
    import string
    final_str = ''
    for char in temp_str:
        if char in string.printable:
            final_str += char
    final_str = final_str.lstrip()
    final_str = final_str.rstrip()
    return final_str


'''
    Created By: Jacob Lattergrass
    This is the form for the password change. Only users that have
    been approved can view it. Otherwise, they'll be redirected.
'''


def change_password_form(request):
    if request.user.is_authenticated:
        ctx = {'msg': ''}
        if request.method == 'POST':
            current = request.POST['current']
            new = request.POST['new']
            confirm = request.POST['confirm']
            if new == '' or confirm == '':
                ctx['msg'] = 'You must enter a new password!'
                return render(request, 'office_app/registration/change_password.html/', ctx)

            response = UserPasswordChange.check_passwords(request.user, current, new, confirm)

            if response['is_changed']:
                UserPasswordChange.objects.filter(user=request.user).delete()
                messages.info(request, "Your password has been changed!")
                user = authenticate(request, username=request.user, password=new)
                login(request, user)
                return redirect('smart_office_dashboard')
            elif not response['is_changed']:
                ctx['msg'] = response['msg']
                return render(request, 'office_app/registration/change_password.html/', ctx)

        tempUserChangeObj = None
        ctx['msg'] = None

        try:
            tempUserChangeObj = UserPasswordChange.objects.filter(user=request.user).latest('expirationTime')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return redirect('smart_office_dashboard')

        current_time = datetime.now().astimezone()
        if current_time > tempUserChangeObj.expirationTime:
            tempUserChangeObj.delete()
            UserPasswordChange.expired_time(request.user)
            ctx['msg'] = 'Your time has expired. Please submit a new request.'
            return redirect('smart_office_dashboard')

        return render(request, 'office_app/registration/change_password.html/', ctx)
    else:
        return redirect('login')


def test_email_sending(request):
    # response = SAPFunctions.createPO(formID=670,
    #                                  companyCode='US27',
    #                                  vendorCode='WAGICOR',
    #                                  plantCode='FII8',
    #                                  PONumber='FII20A2600')
    # response = SAPFunctions.downloadPO('FII20A2603', 'FII8')
    # response = SAPFunctions.downloadGR('', 'FII20A2603')
    emp_list = Employee.objects.all().order_by('associateID')
    acc_list = Account.objects.all().order_by('employee')

    # for emp in emp_list:
    #     for char in emp.email:
    #         if char.isupper():
    #             emp.email = emp.email.lower()
    #             emp.save()
    #             print(f"{emp.associateID} has uppercase letters.")
    #             break
    # for acc in acc_list:
    #     for char in acc.email:
    #         if char.isupper():
    #             acc.email = acc.email.lower()
    #             acc.save()
    #             print(f"{acc.employee.associateID} account has uppercase letters.")
    #             break
    column_headers = ['building', 'first_name', 'other_name', 'last_name', 'email', 'title', 'cost_center']

    with open('EmployeeData(10-27-2020).csv', 'r') as file:
        rows = csv.DictReader(file, column_headers)
        empContext = {}
        for row in rows:
            empContext['building'] = clean_str(row['building'])
            empContext['fname'] = clean_str(row['first_name'])
            empContext['lname'] = clean_str(row['last_name'])
            empContext['prefName'] = clean_str(row['other_name'])
            empContext['email'] = clean_str(row['email'])
            empContext['email'] = empContext['email'].lower()
            empContext['title'] = clean_str(row['title'])
            empContext['costCenter'] = clean_str(row['cost_center'])
            Employee.create_employee_user(empContext)

    SAPFunctions.getVendorCode()

    return HttpResponse(f"Welcome to my empty page!")
