# Page written by Zaawar Ejaz <zaawar.ejaz@fii-usa.com

from django.contrib.postgres.fields import ArrayField
from django.db import models
from office_app.models import *
from ast import literal_eval


# Create your models here.

class VisitorForm(models.Model):
    formID = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID')
    applyingBU = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name="applyingBU")
    dateSubmitted = models.DateTimeField(blank=True, null=True)
    visitDate = models.DateTimeField(blank=True, null=True)

    company = models.CharField(max_length=250, blank=True, null=True)
    companyDescription = models.CharField(max_length=250, blank=True, null=True)
    numberOfPeople = models.CharField(max_length=250, blank=True, null=True)
    nda = models.BooleanField(blank=True, null=True)

    visitType = models.CharField(max_length=250, blank=True, null=True)
    objective = models.CharField(max_length=250, blank=True, null=True)
    fiiBU = models.CharField(max_length=250, blank=True, null=True)
    location = models.CharField(max_length=250, null=True, blank=True)

    isApproved = models.BooleanField(default=False, blank=True, null=True)
    isCompleted = models.BooleanField(default=False, blank=True, null=True)
    isDeclined = models.BooleanField(default=False, blank=True, null=True)
    currentStage = models.IntegerField(default=0, blank=True, null=True)

    @property
    def sap_prefix(self):
        return "VR"

    @property
    def form_type(self):
        return "Visitor Request"

    @property
    def form_url_without_base_url(self):
        return "/visitor/view_application/" + str(self.pk) + "/"

    @property
    def full_url(self):
        return str(settings.BASE_URL) + "visitor/view_application/" + str(self.pk) + "/"

    @property
    def module(self):
        return "visitor"

    @property
    def objective_to_array(self):
        return literal_eval(self.objective)

    @property
    def visittype_to_array(self):
        return literal_eval(self.visitType)

    @property
    def fiibu_to_array(self):
        return literal_eval(self.fiiBU)


class VisitorDetail(models.Model):
    formID = models.ForeignKey(VisitorForm, on_delete=models.CASCADE)
    visitorName = models.CharField(max_length=250, blank=True, null=True)
    jobTitle = models.CharField(max_length=250, blank=True, null=True)
    gender = models.CharField(max_length=250, blank=True, null=True)
    jobRole = models.CharField(max_length=250, blank=True, null=True)
    visitingHistory = models.CharField(max_length=250, blank=True, null=True)


class VisitorSchedule(models.Model):
    formID = models.ForeignKey(VisitorForm, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    meeting_time_from = models.TimeField(blank=True, null=True)
    meeting_time_to = models.TimeField(blank=True, null=True)
    meeting_length = models.IntegerField(blank=True, null=True)
    meeting_location = models.CharField(max_length=250, blank=True, null=True)
    meeting_participants = models.TextField(blank=True, null=True)
    meeting_explain = models.CharField(max_length=250, blank=True, null=True)
    meeting_presenter = models.CharField(max_length=250, blank=True, null=True)
    meeting_resources = models.CharField(max_length=250, blank=True, null=True)
    tour_time_from = models.TimeField(blank=True, null=True)
    tour_time_to = models.TimeField(blank=True, null=True)
    tour_length = models.IntegerField(blank=True, null=True)
    tour_location = models.CharField(max_length=250, blank=True, null=True)
    tour_participants = models.TextField(blank=True, null=True)
    tour_explain = models.CharField(max_length=250, blank=True, null=True)
    tour_presenter = models.CharField(max_length=250, blank=True, null=True)
    tour_resources = models.CharField(max_length=250, blank=True, null=True)

    @property
    def meeting_exp_to_array(self):
        return literal_eval(self.meeting_explain)

    @property
    def tour_exp_to_array(self):
        return literal_eval(self.tour_explain)


class VisitorApprovalProcess(models.Model):
    formID = models.ForeignKey(VisitorForm, on_delete=models.CASCADE)
    approver = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='associateID', blank=True, null=True)
    stage = models.IntegerField(primary_key=False, default=0)
    count = models.IntegerField(primary_key=False, default=0)
    actionTaken = models.CharField(max_length=50, default=None, blank=True, null=True)
    comments = models.CharField(max_length=255, default=None, blank=True, null=True)
    dateActionTaken = models.DateTimeField(blank=True, null=True)
    dayAssigned = models.DateField(blank=True, null=True)
