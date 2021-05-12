from django.contrib.auth import authenticate
from django.db import models
from Smart_Office.settings import AUTH_USER_MODEL
from office_app.models import Employee, Notification, Role, EmployeeDepartment
from office_app.services import EmailHandler
from datetime import datetime, timedelta


# region Constants
PASSWORD_CHANGE_APPROVER_ROLE = "IT Password Approver"
# endregion Constants


# Create your models here.
class Equipment(models.Model):
    equipmentID = models.BigAutoField(primary_key=True)
    # roleID = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return self.equipmentID


class Item(models.Model):
    itemID = models.BigAutoField(primary_key=True)
    equipmentID = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, default='Item', blank=True)
    description = models.CharField(max_length=75, default='Item Description', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)
    supplier = models.CharField(max_length=100)
    specs = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class UserPasswordChange(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    expirationTime = models.DateTimeField()
    isActive = models.BooleanField(default=False)
    firstLogin = models.BooleanField(default=False)

    # region Functions
    @staticmethod
    def create_entry(user, expirationTime=timedelta(days=1), isActive=False, firstLogin=False):
        temp = UserPasswordChange()
        temp.user = user
        temp.expirationTime = datetime.now().astimezone() + expirationTime
        temp.isActive = isActive
        temp.firstLogin = firstLogin
        temp.save()

    @staticmethod
    def first_time_user(user):
        UserPasswordChange.create_entry(user=user, expirationTime=timedelta(days=30), isActive=True, firstLogin=True)
        notification = Notification(employee=user.employee, is_unread=True, created_on=datetime.now().astimezone(),
                                    module='Pass-request')

        notification.title = "Password Change"
        notification.body = "Your password is still the Smart Office default. Click here to change your password."
        notification.link = "/user/change_password/"
        notification.save()


    @staticmethod
    def approve_change_request(approved_user):
        error_messages = {'fatal_errors': '', 'other_errors': []}
        UserPasswordChange.create_entry(user=approved_user, expirationTime=timedelta(days=1), isActive=True, firstLogin=False)

        # Create notification
        notification = Notification(employee=approved_user.employee, is_unread=True, created_on=datetime.now().astimezone(),
                                    module='Pass-request')

        notification.title = "Password Change"
        notification.body = "You've been authorized to change your password. Click here if you haven't done so yet."
        notification.link = "/user/change_password/"
        notification.save()

        # Send email
        error_messages['other_errors'] = EmailHandler.send_password_change_email(approved_user)
        return error_messages


    @staticmethod
    def check_passwords(user, current, new, confirm):
        msg = ''
        # Start with verifying the current password
        if not user.check_password(current):
            msg = 'You have entered an incorrect password. Please try again.'
            return {'is_changed': False, 'msg': msg}
        if new == 'foxconn1':
            msg = 'Please enter a more secure password.'
            return {'is_changed': False, 'msg': msg}
        if current == new:
            msg = 'Please enter a different password from your current.'
            return {'is_changed': False, 'msg': msg}
        if new != confirm:
            msg = 'Please re-confirm your password.'
            return {'is_changed': False, 'msg': msg}
        if new == confirm:
            user.set_password(raw_password=new)
            user.save()
            msg = 'Your password has been changed!'
            return {'is_changed': True, 'msg': msg}

    """
        Author: Jacob Lattergrass
        Purpose: This function is called by the change_password_form view to check if the allotted time has passed.
        :param user: The user who made the request.
        :returns boolean: True if time expired, False if not
    """
    @staticmethod
    def expired_time(user):
        notification = Notification(employee=Employee.objects.get(email=user), is_unread=True, created_on=datetime.now().astimezone(),
                                    module='Pass-request')
        notification.title = "Password Change Request"
        notification.body = "The time to change your password has expired! Please submit another request."
        notification.link = "/contact_us/"
        notification.save()

    # endregion Functions
