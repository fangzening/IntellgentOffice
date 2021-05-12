# Page written by Zaawar Ejaz <zaawar.ejaz@fii-usa.com

import json
from collections import OrderedDict
from pprint import pprint

from django.contrib import messages
from django.forms import model_to_dict
from django.shortcuts import *
from django.http import *
from django.shortcuts import render

from office_app.approval_functions import notify_approver
from visitor.models import *


def create_application(request):
    if request.user.is_authenticated:
        businessunits = BusinessUnit.objects.all().order_by('buName')

        return render(request, 'visitor/createform.html', {'applicant_name': request.session['full_name'],
                                                          'businessunits': businessunits,
                                                          'today_date': datetime.now().astimezone().date(),
                                                           })
    else:
        return redirect('../../accounts/login/?next=/visitor/create_application')


def my_applications(request):
    if request.user.is_authenticated:
        return render(request, 'visitor/myforms.html', {})
    else:
        return redirect('../../accounts/login/?next=/visitor/my_applications')


def approve_applications(request):
    if request.user.is_authenticated:
        return render(request, 'visitor/approveforms.html', {})
    else:
        return redirect('../../accounts/login/?next=/visitor/approve_applications')


def view_application(request, id):
    if request.user.is_authenticated:

        if not VisitorForm.objects.filter(formID=id).exists():
            return HttpResponseNotFound("Visitor form not found. Please go back to the previous page.")

        visitorform = VisitorForm.objects.get(formID=id)
        visitordetails = VisitorDetail.objects.filter(formID=visitorform)
        visitorschedules = VisitorSchedule.objects.filter(formID=visitorform)
        approvalprocess = VisitorApprovalProcess.objects.filter(formID=visitorform).order_by('stage', 'dateActionTaken')

        # Check if approver is allowed to view and is allowed to take action on the form
        is_approver_allowed_view = False
        is_approver_allowed_action = False
        for process in VisitorApprovalProcess.objects.filter(formID=visitorform, approver=request.session['user_id']):
            if process.formID.currentStage >= process.stage:
                is_approver_allowed_view = True
            if process.formID.currentStage == process.stage and process.actionTaken is None:
                is_approver_allowed_action = True

        # Forbid if user is not a applicant/approver and approver is not allowed to view
        if visitorform.employee.associateID != request.session['user_id'] and not is_approver_allowed_view:
            return HttpResponseForbidden("You are not allowed to view this form. Please go back to the previous page.")

        return render(request, 'visitor/viewform.html', {'visitorform': visitorform,
                                                         'visitordetails': visitordetails,
                                                         'visitorschedule': visitorschedules,
                                                         'approvalprocess': approvalprocess,
                                                         'is_approver_allowed_action': is_approver_allowed_action,
                                                         'user': request.session['full_name']})
    else:
        return redirect('../../accounts/login/?next=/visitor/view_application/' + str(id))


def visitor_api(request):
    if request.user.is_authenticated:

        if request.method == 'GET':
            if request.GET.get('action') == "myforms":

                visitorforms = []
                for form in VisitorForm.objects.filter(employee=request.session['user_id']):
                    review_str = ""
                    for process in VisitorApprovalProcess.objects.filter(formID=form, stage=form.currentStage):
                        review_str += (process.approver.title + " Review, <br>")

                    visitorforms.append({
                        'formId': form.formID,
                        'applyingBU': form.applyingBU.buName,
                        'dateSubmitted': form.dateSubmitted.date(),
                        'currentStage': review_str,
                        'totalStages': form.visitorapprovalprocess_set.count(),
                        'isApproved': form.isApproved,
                        'isDeclined': form.isDeclined
                    })

                return JsonResponse({'visitorforms': visitorforms})

            elif request.GET.get('action') == "approveforms":

                visitorforms = []
                for process in VisitorApprovalProcess.objects.filter(approver=request.session['user_id']):
                    if process.formID.currentStage >= process.stage:
                        visitorforms.append({
                            'formId': process.formID.formID,
                            'applicantName': process.formID.employee.full_name,
                            'applyingBU': process.formID.applyingBU.buName,
                            'dateSubmitted': process.formID.dateSubmitted.date(),
                            'status': "Action Required" if process.formID.currentStage == process.stage
                                                           and process.actionTaken == None and not process.formID.isDeclined else process.actionTaken
                        })

                return JsonResponse({'visitorforms': visitorforms})

            else:
                return HttpResponseBadRequest("Please provide action type")

        if request.method == 'POST':

            # Get data from html form
            form_data = json.loads(request.POST.get('data'))

            # Create form object
            form = VisitorForm()

            try:
                # Create entry in the form
                form.employee = Employee.objects.get(associateID=request.session['user_id'])
                form.applyingBU = BusinessUnit.objects.get(buName=form_data['bu_name'][0])
                form.dateSubmitted = datetime.now().astimezone()
                form.visitDate = datetime.strptime(form_data['visit_date'][0], "%Y-%m-%d")
                form.company = form_data['company'][0]
                form.numberOfPeople = form_data['numberof_people'][0]
                form.nda = True if form_data['nda'][0] == "on" else False
                form.companyDescription = form_data['company_description'][0]
                form.visitType = form_data['visit_type']
                form.objective = form_data['objectives']
                form.fiiBU = form_data['fii-bu']
                form.location = form_data['location']
                form.currentStage = 1
                form.isCompleted = 1
                form.save()

                for x in range(len(form_data['visitor_name'])):
                    visitor = VisitorDetail()
                    visitor.formID = form
                    visitor.visitorName = form_data['visitor_name'][x]
                    visitor.jobTitle = form_data['job_title'][x]
                    visitor.gender = form_data['sex'][x]
                    visitor.jobRole = form_data['job_role'][x]
                    visitor.visitingHistory = form_data['visiting_history'][x]
                    visitor.save()

                for x in range(len(form_data['schedule_date'])):
                    schedule = VisitorSchedule()
                    schedule.formID = form
                    schedule.date = datetime.strptime(form_data['schedule_date'][x], "%Y-%m-%d") if \
                    form_data['schedule_date'][x] != "" else None
                    schedule.meeting_time_from = form_data['meeting_time_from'][x] if form_data['meeting_time_from'][
                                                                                          x] != "" else None
                    schedule.meeting_time_to = form_data['meeting_time_to'][x] if form_data['meeting_time_to'][
                                                                                      x] != "" else None
                    schedule.meeting_length = form_data['meeting_length'][x] if form_data['meeting_length'][
                                                                                    x] != "" else None
                    schedule.meeting_explain = form_data['meeting_explain_' + str(x)]
                    schedule.meeting_presenter = form_data['meeting_presenter'][x]
                    schedule.meeting_resources = form_data['meeting_resources'][x]
                    schedule.meeting_participants = form_data['meeting_participants'][x]
                    schedule.tour_time_from = form_data['tour_time_from'][x] if form_data['tour_time_from'][
                                                                                    x] != "" else None
                    schedule.tour_time_to = form_data['tour_time_to'][x] if form_data['tour_time_to'][x] != "" else None
                    schedule.tour_length = form_data['tour_length'][x] if form_data['tour_length'][x] != "" else None
                    schedule.tour_explain = form_data['tour_explain_' + str(x)]
                    schedule.tour_presenter = form_data['tour_presenter'][x]
                    schedule.tour_resources = form_data['tour_resources'][x]
                    schedule.tour_participants = form_data['tour_participants'][x]
                    schedule.save()

                # Array to store approvers
                approvers_arr = []

                # 1. Applying BU Manager
                if form.applyingBU.managedBy is not None:
                    approvers_arr.append([form.applyingBU.managedBy])

                # 2. Company (FII CEO)
                if form.applyingBU.buName in ['iAI', '5G', 'IIoT']:
                    approvers_arr.append([Employee.objects.get(email="brand.cheng@fii-usa.com")])

                # 3. FII BU (Selected Managers)
                bu_approvers = []
                for bu in form.fiiBU:
                    if bu == "L5":
                        bu_approvers.append(Employee.objects.get(email="chen-fu.lin@foxconn.com"))
                    elif bu == "L6":
                        bu_approvers.append(Employee.objects.get(email="geoff.heseman@fii-usa.com"))
                    elif bu == "L10" or bu == "L11":
                        bu_approvers.append(Employee.objects.get(email="kilin.mo@fii-usa.com"))

                approvers_arr.append(bu_approvers)

                # 4. Company (Selected Managers)
                location_approvers = []
                for location in form.location:
                    if location == "MPB":
                        location_approvers.append(Employee.objects.get(email="foo-ming.fu@foxconn.com"))
                    elif location == "SMC":
                        location_approvers.append(Employee.objects.get(email="foo-ming.fu@foxconn.com"))
                    elif location == "GLOBE":
                        location_approvers.append(Employee.objects.get(email="brand.cheng@fii-usa.com"))
                    elif location == "868":
                        location_approvers.append(Employee.objects.get(email="brand.cheng@fii-usa.com"))

                approvers_arr.append(location_approvers)

                # Create approval process
                added_approvers = []
                added_stages = []
                stage_counter = 1
                print(approvers_arr)
                for list in approvers_arr:
                    for approver in list:

                        # Skip the approver if already added in the process or is a applicant
                        if approver.associateID in added_approvers or approver == form.employee:
                            continue

                        process = VisitorApprovalProcess()
                        process.formID = form
                        process.stage = stage_counter
                        process.approver = approver
                        process.dayAssigned = datetime.now().astimezone()
                        process.actionTaken = None
                        process.dateActionTaken = None
                        process.count = 0
                        process.save()
                        added_approvers.append(approver.associateID)
                        added_stages.append(stage_counter)

                        # Notify current stage approvers
                        if stage_counter == form.currentStage:
                            notify_approver(message_type="next_approver", form=form, employee=approver, request=request)

                    if stage_counter in added_stages:
                        stage_counter += 1

                return HttpResponse("Form Successfully Submitted")

            except:
                # Delete the form and print error message
                form.delete()
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                return HttpResponseServerError("Error submitting form. Please try again or contact I.T department")

        if request.method == 'PUT':
            if request.GET.get('action') == "approveform":

                # Get approver's approval process
                form = VisitorForm.objects.get(formID=request.GET.get('formid'))
                process = VisitorApprovalProcess.objects.get(formID=form, stage=form.currentStage, approver=request.session['user_id'])

                # Check if user is approver and form current stage is approver stage
                is_approver_allowed_action = False
                for approvalprocess in VisitorApprovalProcess.objects.filter(formID=form, approver=request.session['user_id']):
                    if approvalprocess.stage == approvalprocess.formID.currentStage and approvalprocess.actionTaken is None:
                        is_approver_allowed_action = True

                if not is_approver_allowed_action:
                    HttpResponseForbidden('You are not allowed to take action on this form. Please go back to the previous page.')

                # Save approver actions
                process.count += 1
                process.dateActionTaken = datetime.now().astimezone()
                process.actionTaken = "Approved"
                process.comments = request.GET.get('comments')
                process.save()

                # Check if all approvers under the current stage has approved the form
                all_current_approved = True
                for process in VisitorApprovalProcess.objects.filter(formID=form, stage=form.currentStage):
                    if process.actionTaken != "Approved":
                        all_current_approved = False

                # Update form stage if all current stage approvers has approved the form
                if all_current_approved:
                    if form.currentStage + 1 > VisitorApprovalProcess.objects.filter(formID=form).count():
                        form.isApproved = True
                        notify_approver(message_type="approved", form=form, employee=form.employee, request=request)
                    else:
                        form.currentStage += 1

                        # Notify new stage approvers
                        approvers = VisitorApprovalProcess.objects.filter(formID=form, stage=form.currentStage)
                        for approverobj in approvers:
                            notify_approver(message_type="next_approver", form=form, employee=approverobj.approver, request=request)

                form.save()

                return HttpResponse("Form Successfully Approved")

            if request.GET.get('action') == "declineform":
                form = VisitorForm.objects.get(formID=request.GET.get('formid'))
                process = VisitorApprovalProcess.objects.get(formID=form, stage=form.currentStage,
                                                             approver=request.session['user_id'])

                # Check if the user is allowed to take action
                is_approver_allowed_action = False
                for approvalprocess in VisitorApprovalProcess.objects.filter(formID=form, approver=request.session['user_id']):
                    if approvalprocess.stage == approvalprocess.formID.currentStage and approvalprocess.actionTaken is None:
                        is_approver_allowed_action = True

                if not is_approver_allowed_action:
                    HttpResponseForbidden(
                        'You are not allowed to take action on this form. Please go back to the previous page.')

                # Save approver actions
                process.count += 1
                process.dateActionTaken = datetime.now().astimezone()
                process.actionTaken = "Declined"
                process.comments = request.GET.get('comments')
                process.save()

                # Update form stage
                form.isDeclined = True
                form.save()

                # Notify applicant
                notify_approver(message_type="declined", form=form, employee=form.employee, request=request)

                return HttpResponse("Form Successfully Declined")

            else:
                return HttpResponseBadRequest("Please provide correct action type and form id")


    else:
        return redirect('login')
