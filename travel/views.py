import sys
import traceback
from operator import itemgetter

from django.core.mail import EmailMultiAlternatives
from django.forms import model_to_dict
from django.shortcuts import *
from office_app.models import *
from travel.models import *
from django.http import *
from office_app.views import set_session
from django.contrib import messages
from travel.custom_functions import *
from SAP import SAPFunctionsPrd
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
import json
from office_app.approval_functions import *


# from .approval_proccess_functions import *

# Create your views here.
def user_guide(request):
    if request.user.is_authenticated:
        return render(request, 'travel/user_guide/index.html', {})
    else:
        return redirect('../../accounts/login/?next=/forms/')


def guide_info(request):
    if request.user.is_authenticated:
        return render(request, 'travel/user_guide/guide_info.html', {})
    else:
        return redirect('../../accounts/login/?next=/forms/')


def travel_home(request):
    if request.user.is_authenticated:
        return render(request, 'travel/HomePage/index.html', {})
    else:
        return redirect('../../accounts/login/?next=/forms/')


def get_travel_form_json(request):
    if request.user.is_authenticated:
        return JsonResponse(TravelDetail.get_approvers_travel_forms(request.session['user_id']))
    else:
        return redirect('login')


def get_my_travel_form_json(request):
    if request.user.is_authenticated:
        return JsonResponse(TravelDetail.get_emp_travel_forms(request.session['user_id']))
    else:
        return redirect('login')


def submit(request):
    return HttpResponse("Travel Submit")


def get_travel_rem_json(request):
    if request.user.is_authenticated:
        set_session(request)
        return JsonResponse(TADetails.get_emp_travel_rems(request.session['user_id']))
    else:
        return redirect('login')


def travel_rem_list_json(request):
    if request.user.is_authenticated:
        set_session(request)
        return JsonResponse(TADetails.get_approvers_travel_rems(request.session['user_id']))
    else:
        return redirect('login')


'''
Handles getting the form data from the travel application.
It saves unsubmitted travel applications, and submits submitted ones.
It also sets up the stages for who will be approving the travel application.
Author is: Corrina Barr
:param request: the webpage request
:return: redirects to login if user is not logged in. 
         otherwise shows section one page
         if method is post, it sends data to database and returns to Smart Office Home Page
'''


def travel_application(request):
    if request.user.is_authenticated:
        there_are_errors = False
        try:
            # need to work on it later 6/24/20
            gl_account = GLAccount.objects.get(glCode=135510)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            messages.error(request, "Unable to get desired gl account data")
            gl_account = None

        form_is_completely_approved = False
        departments = CostCenter.objects.all()
        business_units = BusinessUnit.objects.all()
        business_groups = BusinessGroup.objects.all()

        companies = LegalEntity.objects.all()
        emp = Employee.objects.get(associateID=request.session['user_id'])

        employee_country = emp.country
        employee_dept_object = EmployeeDepartment.objects.get(associateID=emp)
        employee_company = employee_dept_object.departmentID.businessUnit.businessGroup.legalEntity
        employee_business_group = employee_dept_object.departmentID.businessUnit.businessGroup

        old_emp_info_form = EmployeeInformation()

        old_travel_detail_form = TravelDetail()
        old_company_forms = TravelDetailCompany()
        old_expense_form = TravelDetailExpenses()
        old_advance_form = AdvanceTravelApp()
        there_are_multiple_old_company_forms = False

        try:
            vendor = EmployeeVendors.objects.filter(employee=emp).first().vendor
        except:
            vendor = None

        user_is_creator = True

        try:
            factory_codes = Building.objects.all()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving Building data. Please contact IT")

        try:
            users_factory = Building.objects.filter(
                legalEntity=LegalEntity.objects.get(entityName=request.session['legal_entity_name'])).first()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving Building data. Please contact IT")

        if request.method == "POST":
            error_messages = {'fatal_errors': "", 'other_errors': []}
            all_post_data = dict(request.POST)
            print("All post data: " + str(request.POST))
            response_data = {}
            response_data['result'] = ""
            response_data['dir_to_dash'] = "./submitted_forms/"

            # Sections 1 & 2 - Corrina Barr
            # region Section 1
            try:
                company = employee_company  # EmployeeInformation.company
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = 'Error saving form. Company data incorrect'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            try:
                BG = employee_business_group  # EmployeeInformation.bussinessGroup
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = 'Error saving form. Business Group incorrect'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            try:
                employee = Employee.objects.get(associateID=request.session['user_id'])  # EmployeeInformation.employee
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = 'Cannot retrieve creator of the forms employee data'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            project = request.POST.get("project")  # EmployeeInformation.project
            if len(project) > 100:
                error_messages['fatal_errors'] = 'Project name has too many characters'
                response_data['result'] = error_messages['fatal_errors']
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            estimated_expense = request.POST.get("estimated_expense")  # EmployeeInformation.estiematedExpense
            if float(estimated_expense) > 99999999.99:
                error_messages['fatal_errors'] = 'Estimated Expense is too large an amount'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            travel_type = request.POST.get("travel_type")  # EmployeeInformation.travelType
            if travel_type != 'International' and travel_type != 'Domestic':
                error_messages['fatal_errors'] = 'Travel Type must be International or Domestic'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            budget_sc = request.POST.get("budget_sc")  # EmployeeInformation.bugdetSourceCode
            if len(budget_sc) > 20:
                error_messages['fatal_errors'] = 'Budget Source code is too long'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            old_emp_info_form.save_travel_form(company=company, bg=BG, employee=employee, project=project,
                                               estimatedExpense=estimated_expense, travelType=travel_type,
                                               budgetSourceCode=budget_sc,
                                               advancedApp=False, isCompleted=False)
            old_emp_info_form.currentStage = 0
            old_emp_info_form.save()

            print("***********SUBMIT BUTTON: " + request.POST.get('submit_button'))
            if request.POST.get('submit_button') == "Save and Return to Home":
                is_completed = False  # EmployeeInformation.is_completed
                current_stage = 0
                try:
                    TemporaryApprovalStage.objects.get(approverID=employee, stage=0, formID=old_emp_info_form)
                except:
                    TemporaryApprovalStage().create_approval_stage(approverID=employee, stage=0,
                                                                   formID=old_emp_info_form, count=0)
            else:
                is_completed = True  # EmployeeInformation.is_completed
                current_stage = 1
                try:
                    to_be_deleted = TemporaryApprovalStage.objects.get(approverID=employee, stage=0,
                                                                       formID=old_emp_info_form)
                    to_be_deleted.delete()
                except:
                    print("no stage 0 to delete!")

            old_emp_info_form.save_travel_form(company=company, bg=BG, employee=employee, project=project,
                                               estimatedExpense=estimated_expense, travelType=travel_type,
                                               budgetSourceCode=budget_sc,
                                               advancedApp=False, isCompleted=is_completed)
            old_emp_info_form.currentStage = current_stage
            old_emp_info_form.save()
            # endregion

            # region Section 2
            form_id = EmployeeInformation.objects.get(formID=old_emp_info_form.formID)  # TravelDetail.formID
            company = form_id.company  # TravelDetail.company

            travel_datefrom = request.POST.get("travel_datefrom")  # TravelDetail.startDate
            try:
                if travel_datefrom != '':
                    datetime.strptime(travel_datefrom, '%Y-%m-%d')
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = 'Start date field must be a date'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            travel_dateto = request.POST.get("travel_dateto")  # TravelDetail.endDate
            try:
                if travel_dateto != '':
                    datetime.strptime(travel_dateto, '%Y-%m-%d')
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = 'Travel Date end field must be a date'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            if travel_dateto != '':
                if datetime.strptime(travel_dateto, '%Y-%m-%d') < datetime.strptime(travel_datefrom, '%Y-%m-%d'):
                    error_messages['fatal_errors'] = 'End date of travel must be AFTER the start date'
                    response_data['result'] = error_messages
                    there_are_errors = True
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            estimated_duration = request.POST.get("estimated_period")  # TravelDetail.estimatedDuration
            if estimated_duration != '':
                try:
                    if int(estimated_duration) > 2147483647:
                        error_messages['fatal_errors'] = 'Estimated duration of the trip is too long'
                        response_data['result'] = error_messages
                        there_are_errors = True
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Error saving form. Cannot get estimated duration'
                    response_data['result'] = error_messages
                    there_are_errors = True
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            departure_country = request.POST.get("departure_country")  # TravelDetail.DepartureCountry
            if departure_country != '':
                if len(departure_country) > 25:
                    error_messages['fatal_errors'] = 'Country of departure must not exceed 20 character'
                    response_data['result'] = error_messages
                    there_are_errors = True
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            departure_factory_code = request.POST.get("factory_code")
            if departure_factory_code != '' and departure_factory_code != None:
                if len(departure_factory_code) > 30:
                    error_messages['fatal_errors'] = 'Departure factory code must not exceed 30 characters'
                    response_data['result'] = error_messages
                    there_are_errors = True
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
            print("************************DEP FACt CODE 1: " + str(departure_factory_code))

            destination_country = request.POST.get("country2")  # TravelDetail.DepartureCountry
            if destination_country != '':
                if len(destination_country) > 25:
                    error_messages['fatal_errors'] = 'Country of destination must not exceed 25 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                    there_are_errors = True

            departure_prefferred = request.POST.get("departure_state")
            if len(departure_prefferred) > 50:
                error_messages['fatal_errors'] = 'Preferred Departure City/Stage must not exceed 50 characters'
                response_data['result'] = error_messages
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
                there_are_errors = True

            destination_state = request.POST.get("state2")  # TravelDetail.DestinationState
            if len(destination_state) > 50:
                error_messages['fatal_errors'] = 'Destination state must not exceed 50 characters'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            destination_city = request.POST.get("destination_city")  # TravelDetail.DestinationCity
            if len(destination_city) > 40:
                error_messages['fatal_errors'] = 'Destination City name must not exceed 40 characters'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            transportation_type = request.POST.get("transportation_type")  # TravelDetail.transportation
            if transportation_type != 'Flight' and transportation_type != 'Train' and transportation_type != 'Rental Car':
                error_messages['fatal_errors'] = '-Type of Transportation must be Train, Flight, or Rental Car, not ' + transportation_type + '\n'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            accomodation_type = request.POST.get("accommodation_type")  # TravelDetail.accommodation
            if accomodation_type != 'Hotel' and accomodation_type != 'Dormitory':
                error_messages['fatal_errors'] = 'Travel Accommodation type must be Hotel or Dormitory not, ' + accomodation_type + '\n'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            date = request.POST.get("date")  # TravelDetail.date
            currency = request.POST.get("country_currency")
            if len(currency) > 50:
                error_messages['fatal_errors'] = 'Currency must not exceed 50 characters'
                response_data['result'] = error_messages
                there_are_errors = True
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            # I will need to update this
            print("************************DEP FACt CODE 2: " + str(departure_factory_code))
            old_travel_detail_form.save_travel_detail(formID=form_id, company=company, startDate=travel_datefrom,
                                                      departurePrefferred=departure_prefferred,
                                                      endDate=travel_dateto,
                                                      departureCountry=departure_country,
                                                      departureFactoryCode=departure_factory_code,
                                                      destinationState=destination_state,
                                                      destinationCity=destination_city,
                                                      destinationCountry=destination_country,
                                                      transportation=transportation_type,
                                                      accommodation=accomodation_type,
                                                      date=date, isCompleted=is_completed,
                                                      estimatedDuration=estimated_duration, currency=currency)
            # endregion

            # region The Rows and Columns (wich is part of Section 2 but is so long it gets its own region apart from it)
            detail_id = TravelDetail.objects.get(
                detailID=old_travel_detail_form.detailID)  # TravelDetailCompany.detailID

            visit_dates = all_post_data['visit_date']  # Get keys that contain this
            visit_companies = all_post_data["visit_company"]
            visit_departments = all_post_data["visit_department"]
            contacts = all_post_data["company_contact"]
            objectives = all_post_data["visit_objective"]
            try:
                visit_ids = all_post_data["visit_id"]  # This field only exists on a saved form
            except:
                print('no old visit ids to attain')
            index = 0
            rows = 0

            print("Visit Dates: " + str(visit_dates))

            # Check to see if there are multiple rows:
            if str(visit_dates) != '':
                if ',' in str(visit_dates):
                    print('There are multiple rows')
                    there_are_multiple_rows = True

                else:
                    print('there is only one row')
                    there_are_multiple_rows = False

                if there_are_multiple_rows:
                    for row in visit_dates:
                        rows += 1
                    for row in visit_dates:
                        if index < rows:
                            visit_date = row  # TravelDetailCompany.date
                            try:
                                if row != '':
                                    datetime.strptime(row, '%Y-%m-%d')
                            except:
                                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                                error_messages['fatal_errors'] = 'Travel Purpose date must have a date value'
                                response_data['result'] = error_messages
                                there_are_errors = True
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )
                            visit_company = visit_companies[index]  # TravelDetailCompany.visitCompany

                            if len(visit_company) > 50:
                                error_messages['fatal_errors'] = 'Travel Purpose visit company name must not exceed 20 characters'
                                response_data['result'] = error_messages
                                there_are_errors = True
                            visit_department = visit_departments[index]  # TravelDetailCompany.department

                            if len(visit_department) > 50:
                                error_messages['fatal_errors'] = 'Travel Purpose visit department name must not exceed 50 characters'
                                response_data['result'] = error_messages
                                there_are_errors = True
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )

                            contact = contacts[index]  # TravelDetailCompany.contact
                            if len(contact) > 60:
                                error_messages['fatal_errors'] = 'Travel purpose contact name must not exceed 50 characters'
                                response_data['result'] = error_messages
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )

                            objective = objectives[index]  # TravelDetailCompany.preciseObjective
                            if len(objective) > 50:
                                error_messages['fatal_errors'] = 'Travel purpose objective must be less than 50 characters'
                                response_data['result'] = error_messages
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )

                            try:
                                # Try will update an edited row. If there is no row to update...
                                current = TravelDetailCompany.objects.get(visitID=visit_ids[index])
                                current.save_detail_company(visitCompany=visit_company, department=visit_department,
                                                            contact=contact, date=visit_date,
                                                            preciseObjective=objective,
                                                            detailID=detail_id, isCompleted=is_completed)
                            except:
                                # ...it will throw an error which except will catch. Except will create a new row instead of updating an old one
                                print('more feilds than last save for create detail company')
                                TravelDetailCompany().save_detail_company(visitCompany=visit_company,
                                                                          department=visit_department,
                                                                          contact=contact, date=visit_date,
                                                                          preciseObjective=objective,
                                                                          detailID=detail_id,
                                                                          isCompleted=is_completed)
                            index += 1
                            print("Rows: " + str(rows))
                            print("Index: " + str(index))
                        else:
                            break
                # Delete rows that have been deleted in the javascript
                try:
                    for form in old_company_forms:
                        if str(form.visitID) not in str(visit_ids) and form.visitID != visit_ids:
                            form_to_delete = TravelDetailCompany.objects.get(visitID=form.visitID)
                            form_to_delete.delete()
                except:
                    print("No old forms to delete")

                # If there is only one row:
                if there_are_multiple_rows == False:
                    try:
                        # Try will update an edited row. If there is no row to update...
                        if len(visit_companies) > 50:
                            error_messages['fatal_errors'] = 'Travel Purpose visit company name must not exceed 50 characters'
                            response_data['result'] = error_messages

                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        if len(visit_departments) > 50:
                            error_messages['fatal_errors'] = 'Travel Purpose visit department name must not exceed 50 characters'
                            response_data['result'] = error_messages

                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        if len(contacts) > 60:
                            error_messages['fatal_errors'] = 'Travel Purpose contact name must not exceed 60 characters'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        try:
                            if visit_dates[0] != '':
                                datetime.strptime(visit_dates[0], '%Y-%m-%d')
                        except:
                            print('\n'.join(traceback.format_exception(*sys.exc_info())))
                            error_messages['fatal_errors'] = 'Travel Purpose visit date must be a date value'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        if len(objectives) > 50:
                            error_messages['fatal_errors'] = 'Travel Purpose objective must not exceed 50 characters'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        print("old_company_forms[0].visitID: " + str(old_company_forms[0].visitID))
                        form_to_update = TravelDetailCompany.objects.get(visitID=old_company_forms[0].visitID)
                        form_to_update.save_detail_company(visitCompany=visit_companies[0],
                                                           department=visit_departments[0],
                                                           contact=contacts[0], date=visit_dates[0],
                                                           preciseObjective=objectives[0], detailID=detail_id,
                                                           isCompleted=is_completed)
                    except:
                        try:
                            # ...it will throw an error which except will catch. Except will create a new row instead of updating an old one
                            print("Creating new travel detail company")
                            TravelDetailCompany().save_detail_company(visitCompany=visit_companies[0],
                                                                      department=visit_departments[0],
                                                                      contact=contacts[0], date=visit_dates[0],
                                                                      preciseObjective=objectives[0],
                                                                      detailID=detail_id, isCompleted=is_completed)
                        except:
                            print("No travel detail Company information to save")

            # Section 3 - Zaawar Ejaz
            # region Section 3
            allowance = validate_number(request.POST.get('allowance'), 99999999.99) * validate_number(
                request.POST.get('estimated_period'), 99999999.99)
            if allowance != '':
                try:
                    if float(allowance) > 99999999.99:
                        error_messages['fatal_errors'] = 'Total requested per diem amount is too high'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Perdiem did not pass a numeric value'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            allowance_detail = request.POST.get('explanation_allowance')
            if len(allowance_detail) > 100:
                error_messages['fatal_errors'] = 'Per Diem explanation must not exceed 100 characters'
                response_data['result'] = error_messages
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            accomodation_expense = request.POST.get('accommodation')
            if accomodation_expense != '':
                print("Expense Accommodation:" + accomodation_expense + "END")
                try:
                    if float(accomodation_expense) > 99999999.99:
                        error_messages['fatal_errors'] = 'Accommodation amount is too large'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Accommodation expense amount must be a number'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            transport_expense = request.POST.get('transportation')
            if transport_expense != 0:
                try:
                    if float(transport_expense) > 99999999.99:
                        error_messages['fatal_errors'] = 'Transportation expense is too high'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Transportation expense must be a number'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            transport_detail = request.POST.get('explaination_transportation')
            if len(transport_detail) > 100:
                error_messages['fatal_errors'] = 'Transportation explanation must not exceed 100 characters'
                response_data['result'] = error_messages
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            public_relation_expense = request.POST.get('public_relationship')
            if public_relation_expense != '':
                try:
                    if float(public_relation_expense) > 99999999.99:
                        error_messages['fatal_errors'] = 'Destination City name must not exceed 40 characters'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Public relationship expense must be a number'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            public_relation_detail = request.POST.get('explanation_publicrelationship')
            if len(public_relation_detail) > 100:
                error_messages['fatal_errors'] = 'Public relation expense explanation must not exceed 100 characters'
                response_data['result'] = error_messages
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            other_expense = request.POST.get('other_expense')
            if other_expense != '':
                try:
                    if float(other_expense) > 99999999.99:
                        error_messages['fatal_errors'] = 'Other expense is too large'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Other expense amount must be a number'
                    response_data['result'] = error_messages
                    response_data[
                        'result'] = 'Other expense amount must be a number\n'
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            other_explanation = request.POST.get('explaination_otherexpense')
            if len(public_relation_detail) > 100:
                error_messages['fatal_errors'] = 'Public relationship explanation must not exceed 100 characters'
                response_data['result'] = error_messages
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            total_expenses = request.POST.get('total')
            if total_expenses != '':
                try:
                    if float(total_expenses) > 99999999.99:
                        error_messages['fatal_errors'] = 'Total expense amount is too large'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Total expense must be a number'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

            ticket_exp = request.POST.get('explaination_airwayticket')
            ticket_exp = validate_string(ticket_exp, 100)

            ticket = validate_number(request.POST.get('airway_ticket'), 99999999.99)
            print("**TOTAL: " + str(total_expenses))

            old_expense_form.save_detail_expense(detailID=detail_id, date=None, allowance=allowance,
                                                 allowanceExp=allowance_detail, accommodation=accomodation_expense,
                                                 accommodationExp=None,
                                                 transportation=transport_expense,
                                                 transportationExp=transport_detail, visa=None,
                                                 visaExp=None, airwayTicket=ticket,
                                                 airwayTicketExp=ticket_exp, insurance=None,
                                                 insuranceExp=None, other=other_expense,
                                                 otherExp=other_explanation, total=total_expenses,
                                                 isCompleted=is_completed, publicRelation=public_relation_expense,
                                                 publicRelationExp=public_relation_detail)

            if request.POST.get('travel_advance_apply') == 'true':
                advance_amount = request.POST.get('advance_amount')
                if validate_number(advance_amount, 999999999999.99) > validate_number(old_expense_form.allowance,
                                                                                      999999999999.99) + validate_number(
                    old_expense_form.publicRelationship, 999999999999.99) + validate_number(
                    old_expense_form.accommodation, 999999999999.99):
                    error_messages['fatal_errors'] = 'Travel advance is greater than amount allowed'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                gl_account = request.POST.get('gl_account')
                if len(gl_account) > 50:
                    error_messages['fatal_errors'] = 'Travel Advance GL Account can only be up to 50 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                gl_detail = request.POST.get('gl_description')
                if len(gl_detail) > 50:
                    error_messages['fatal_errors'] = 'Travel advance GL description can only be up to 50 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                cost_center = request.POST.get('cost_center')
                if len(cost_center) > 50:
                    error_messages['fatal_errors'] = 'Travel Advance cost center can only be up to 50 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                profit_center = request.POST.get('advanceprofit_center')
                if len(profit_center) > 50:
                    error_messages['fatal_errors'] = 'Travel advance profit center must not exceed 50 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                head_text = request.POST.get('head_text')
                if len(head_text) > 50:
                    error_messages['fatal_errors'] = 'Travel advance head text must not exceed 25 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                text = request.POST.get('text')
                if len(text) > 50:
                    error_messages['fatal_errors'] = 'Travel Advance Text must not exceed 25 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                assignment = request.POST.get('assignment')
                if len(assignment) > 100:
                    error_messages['fatal_errors'] = 'Travel advance assignment must not exceed 100 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                reference_doc = request.POST.get('reference_document')
                if len(reference_doc) > 50:
                    error_messages['fatal_errors'] = 'Travel advance reference document must not exceed 60 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                currency = request.POST.get("country_currency")
                if len(currency) > 50:
                    error_messages['fatal_errors'] = 'Currency must not exceed 50 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                vendor_code = request.POST.get("vendor_code")
                if len(vendor_code) > 15:
                    error_messages['fatal_errors'] = 'Vendor code must not exceed 15 characters'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                company_code = LegalEntity.objects.get(entityName=request.session['legal_entity_name']).sapCompCode

                # Create Advance Form  (Less Redundancy -- Zaawar Ejaz)
                adv = AdvanceTravelApp().save_adv_app(formID=form_id, advAmount=advance_amount,
                                                      glAccount=gl_account, glDescription=gl_detail,
                                                      costCenterCode=cost_center, profitCenter=profit_center,
                                                      headText=head_text,
                                                      text=text, assignment=assignment, isCompleted=is_completed,
                                                      refDocument=reference_doc, dateApplied=datetime.now(),
                                                      currency=currency, vendorCode=vendor_code,
                                                      companyCode=company_code)

                # Create two entry in the database for SAP
                SAPAdvApp().create_entries(advID=adv.advID)

            else:
                try:
                    old_advance_form.delete()
                except:
                    print("no old advance form to delete")

            if is_completed == True:
                error_messages = merge_dictionaries(error_messages,
                                                    old_emp_info_form.initialize_ta_approval_process(request))

                # If there are fatal errors:
                if error_messages['fatal_errors'] != "":
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                # If there are no fatal errors:
                messages.success(request, "Form has been saved correctly")

                for error in error_messages['other_errors']:
                    messages.error(request, error)

            response_data['result'] = error_messages
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        else:
            return render(request, "travel/index.html", {"today": datetime.now(),
                                                         "form_is_being_approved": False,
                                                         "form_is_being_shown_to_approver": False,
                                                         "full_name": request.session["full_name"],
                                                         "user_dept": request.session['department'],
                                                         "business_unit": request.session["business_unit"],
                                                         "business_units": business_units,
                                                         "departments": departments,
                                                         "business_groups": business_groups,
                                                         'companies': companies,
                                                         'old_emp_form': old_emp_info_form,
                                                         'old_company_forms': old_company_forms,
                                                         'old_detail_form': old_travel_detail_form,
                                                         'old_expense_form': old_expense_form,
                                                         'old_advance_form': old_advance_form,
                                                         'there_are_multiple_old_company_forms': there_are_multiple_old_company_forms,
                                                         'business_unit_code': request.session['business_unit_code'],
                                                         'user_dept_code': request.session['department_code'],
                                                         "factory_codes": factory_codes,
                                                         "users_building": users_factory,
                                                         "approving_modifications": False,
                                                         "modified_fields": [],
                                                         "all_forms_stages": [],
                                                         "employee_country": employee_country,
                                                         "current_date": datetime.today(),
                                                         "form_is_completely_approved": form_is_completely_approved,
                                                         "user_is_creator": user_is_creator,
                                                         "approvers_in_chat": emp,
                                                         "all_forms_approvers": emp,
                                                         "gl_account": gl_account,
                                                         "vendor": vendor,
                                                         "emp": emp,
                                                         "employee_company": employee_company,
                                                         "employee_business_group": employee_business_group
                                                         })
    else:
        return redirect('../../accounts/login/?next=/forms/travel_application')


# region Views for Approver to See
'''
This will show a list of forms for the user to approve
Author: Corrina Barr
:param request: the webpage request
:return: redirects to login if user is not logged in. 
         If user employee object has not bee created yet, tell them they cannot view this page
         otherwise shows forms to approve page
'''
def forms_to_approve_view(request):
    if request.user.is_authenticated:
        set_session(request)
        # Get message:
        # Reset message so same message doesn't show again:
        if request.session['department'] == '':
            return HttpResponse("You are not allowed to view this page.")
        else:
            return render(request, 'travel/travel_form_list.html')
    else:
        return redirect('../../accounts/login/?next=/forms/travel_list/')


'''
This will show the form the user is about to approve.
Author: Corrina Barr
:param request: the webpage request
:return: redirects to login if user is not logged in. 
         If user employee object has not bee created yet, tell them they cannot view this page
         otherwise shows forms to approve page
'''


def approve_form_view(request, pk):
    if request.user.is_authenticated:
        error_messages = {'fatal_errors': '', 'other_errors': []}
        response_data = {}
        response_data['dir_to_dash'] = "../../travel_list/"
        response_data['result'] = ''
        there_are_errors = False
        if request.session['department'] == '':
            return HttpResponse("You are not allowed to view this page.")

        # Get employees for the add new approver select option thing:
        # 1) Business Unit Manager
        # 2) Cost Managers
        # 3) Department Managers
        # 4) Accountants

        employees_for_add_new_approver = []
        accountant_list = []
        all_post_data = dict(request.POST)

        try:
            old_emp_info_form = EmployeeInformation.objects.get(pk=pk)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving the form. Please contact IT."
                                "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        try:
            employee = old_emp_info_form.employee
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving your data. Please contact IT."
                                "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        try:
            employee_country = employee.country
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving country data. Please contact IT."
                                "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        try:
            employee_dept_object = EmployeeDepartment.objects.get(associateID=employee)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving employee data. Please contact IT."
                                "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        try:
            employee_company = employee_dept_object.departmentID.businessUnit.businessGroup.legalEntity
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error company data. Please contact IT."
                                "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        try:
            employee_business_group = employee_dept_object.departmentID.businessUnit.businessGroup
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error business group data. Please contact IT."
                                "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        try:
            all_forms_stages = TemporaryApprovalStage.objects.filter(formID=old_emp_info_form).order_by('stage')
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving approval process data. Please contact IT."
                                "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        try:
            vendor = EmployeeVendors.objects.filter(employee=employee).first().vendor
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            vendor = None

        # Check if the form can have a TR or not:
        form_is_completely_approved = old_emp_info_form.isApproved

        try:
            if old_emp_info_form.employee == Employee.objects.get(associateID=request.session['user_id']):
                user_is_creator = True
                response_data['dir_to_dash'] = "../../submitted_forms/"
            else:
                user_is_creator = False
                response_data['dir_to_dash'] = "../../travel_list/"
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error figuring out creator of the form. Please contact IT."
                                "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        # Check to see if the form has been declined or not
        form_is_declined = old_emp_info_form.isDeclined

        already_approvers = [old_emp_info_form.employee]

        try:
            all_forms_stages = TemporaryApprovalStage.objects.filter(formID=old_emp_info_form).order_by('stage')
            for stage in all_forms_stages:
                already_approvers.append(stage.approverID)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving approval process data of the form. Please contact IT."
                                "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        # try:
        units = BusinessUnit.objects.all()
        print(str(units))
        if units:
            for unit in BusinessUnit.objects.all():
                if unit.managedBy not in already_approvers and unit.managedBy not in employees_for_add_new_approver:
                    employees_for_add_new_approver.append(unit.managedBy)
                if unit.costManager != None:
                    if unit.costManager not in already_approvers and unit.managedBy not in employees_for_add_new_approver:
                        employees_for_add_new_approver.append(unit.costManager)

        departments = CostCenter.objects.all()
        if departments:
            for dept in departments:
                if dept.managedBy not in already_approvers and dept.managedBy not in employees_for_add_new_approver:
                    employees_for_add_new_approver.append(dept.managedBy)

        accountants = EmployeeDepartment.objects.filter(
            departmentID=CostCenter.objects.filter(costCenterName='Supporting - Accounting').first())
        if accountants:
            for accountant in accountants:
                if accountant.associateID not in already_approvers and accountant.associateID not in employees_for_add_new_approver:
                    employees_for_add_new_approver.append(accountant.associateID)
                if accountant.pk not in accountant_list:
                    accountant_list.append(accountant.associateID)

        # Remove duplicate names:
        employees_for_add_new_approver = list(dict.fromkeys(employees_for_add_new_approver))

        # Remove employees who are on approval list but didn't get removed earlier because the employee has multiple departments:
        for emp in employees_for_add_new_approver:
            if emp != None:
                for stage in all_forms_stages:
                    try:
                        print(str(stage.approverID.email))
                        can = True
                    except:
                        can = False
                    if can:
                        print("Stage approver id: " + str(stage.approverID))
                        print("Employee: " + str(emp))
                        if stage.approverID.email == emp.email:
                            try:
                                employees_for_add_new_approver.remove(emp)
                            except:
                                dummy_var = 0


        employee_list = Employee.objects.all()
        business_groups = BusinessGroup.objects.all()
        companies = LegalEntity.objects.all()
        old_advance_form = AdvanceTravelApp()
        users_forms_to_approve = []

        users_stage = TemporaryApprovalStage()
        user_has_stage_for_form = False
        try:
            users_stage = TemporaryApprovalStage.objects.get(formID=old_emp_info_form, approverID=Employee.objects.get(associateID=request.session['user_id']))
            user_has_stage_for_form = True
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            print("User has no stage for form")

        if (old_emp_info_form.isCompleted is False or form_is_declined) and employee == Employee.objects.get(
                associateID=request.session['user_id']):
            try:
                old_travel_detail_form = TravelDetail.objects.get(formID=old_emp_info_form.formID)
                old_company_forms = TravelDetailCompany.objects.filter(detailID=old_travel_detail_form.detailID)
                old_expense_form = TravelDetailExpenses.objects.get(detailID=old_travel_detail_form.detailID)
                old_advance_form = AdvanceTravelApp.objects.filter(formID=old_emp_info_form.formID).first()
                there_are_multiple_old_company_forms = False
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                return HttpResponse("Error getting form data. Please contact IT."
                                    "<br>Go back to <a href='{% url 'smart_office_dashboard' %}'>Home</a>")
            try:
                for form in old_company_forms:
                    print("Old company form date: " + str(form.date))
                    there_are_multiple_old_company_forms = True
            except:
                print("only one old company form")
                there_are_multiple_old_company_forms = False

            try:
                factory_codes = Building.objects.all()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                return HttpResponse("Error retrieving Building data. Please contact IT")

            try:
                users_factory = Building.objects.filter(
                    legalEntity=LegalEntity.objects.get(entityName=request.session['legal_entity_name'])).first()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                return HttpResponse("Error retrieving Building data. Please contact IT")

            if request.method == 'POST':
                all_post_data = dict(request.POST)
                print("All post data: " + str(request.POST))

                # Sections 1 & 2 - Corrina Barr
                # region Section 1
                try:
                    company = employee_company  # EmployeeInformation.company
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Error saving form. Company given does not exist.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                try:
                    BG = employee_business_group  # EmployeeInformation.bussinessGroup
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Error saving form. Business Group given does not exist.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                try:
                    employee = Employee.objects.get(
                        associateID=request.session['user_id'])  # EmployeeInformation.employee
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Error saving form. Could not retrieve your employee data.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                project = request.POST.get("project")  # EmployeeInformation.project
                if len(project) > 100:
                    error_messages['fatal_errors'] = 'Error saving form. Project name must be less than 100 characters.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                estimated_expense = request.POST.get("estimated_expense")  # EmployeeInformation.estiematedExpense
                if estimated_expense != '':
                    try:
                        if float(estimated_expense) > 99999999.99:
                            error_messages['fatal_errors'] = 'Estimated expense is too high.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = 'Estimated expense must be a number'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                travel_type = request.POST.get("travel_type")  # EmployeeInformation.travelType
                if travel_type != 'International' and travel_type != 'Domestic':
                    error_messages['fatal_errors'] = 'Travel type must be International or Domestic.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                budget_sc = request.POST.get("budget_sc")  # EmployeeInformation.bugdetSourceCode
                if len(budget_sc) > 20:
                    error_messages['fatal_errors'] = 'Budget Source Code cannot be longer than 20 characters.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                try:
                    old_emp_info_form.save_travel_form(company=company, bg=BG, employee=employee, project=project,
                                                       estimatedExpense=estimated_expense, travelType=travel_type,
                                                       budgetSourceCode=budget_sc,
                                                       advancedApp=False, isCompleted=False)
                    old_emp_info_form.currentStage = 0
                    old_emp_info_form.save()
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Error saving form. Please contact IT.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                if request.POST.get('submit_button') == "Save and Return to Home":
                    is_completed = False  # EmployeeInformation.is_completed
                    current_stage = 0
                    try:
                        TemporaryApprovalStage.objects.get(approverID=employee, stage=0, formID=old_emp_info_form)
                    except:
                        TemporaryApprovalStage().create_approval_stage(approverID=employee, stage=0,
                                                                       formID=old_emp_info_form, count=0)
                else:
                    is_completed = True  # EmployeeInformation.is_completed
                    current_stage = 1
                    try:
                        to_be_deleted = TemporaryApprovalStage.objects.get(approverID=employee, stage=0,
                                                                           formID=old_emp_info_form)
                        to_be_deleted.delete()
                    except:
                        print("no stage 0 to delete!")

                if form_is_declined:
                    # If someone declined the form, set old_emp_info_form to a new form
                    old_emp_info_form = EmployeeInformation()
                    print("Saving form based off declined form")

                try:
                    old_emp_info_form.save_travel_form(company=company, bg=BG, employee=employee, project=project,
                                                       estimatedExpense=estimated_expense, travelType=travel_type,
                                                       budgetSourceCode=budget_sc,
                                                       advancedApp=False, isCompleted=is_completed)
                    old_emp_info_form.currentStage = current_stage
                    old_emp_info_form.save()
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Could not save the form. Please contact IT.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                # endregion

                # region Section 2
                try:
                    form_id = EmployeeInformation.objects.get(formID=old_emp_info_form.formID)  # TravelDetail.formID
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Could not retrieve data on newly saved part of the first page of the form. Please contact IT.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                try:
                    company = form_id.company  # TravelDetail.company
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Company given does not exist.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                travel_datefrom = request.POST.get("travel_datefrom")  # TravelDetail.startDate
                try:
                    if travel_datefrom != '':
                        datetime.strptime(travel_datefrom, '%Y-%m-%d')
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'Start date field must be a date.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                travel_dateto = request.POST.get("travel_dateto")  # TravelDetail.endDate
                try:
                    if travel_dateto != '':
                        datetime.strptime(travel_dateto, '%Y-%m-%d')
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = 'End date of travel must be a date.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                if travel_dateto != '':
                    if datetime.strptime(travel_dateto, '%Y-%m-%d') < datetime.strptime(travel_datefrom, '%Y-%m-%d'):
                        error_messages['fatal_errors'] = 'End date of travel must be AFTER start date of travel.'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                estimated_duration = request.POST.get("estimated_period")  # TravelDetail.estimatedDuration
                if estimated_duration != '':
                    try:
                        if int(estimated_duration) > 2147483647:
                            error_messages['fatal_errors'] = 'Estimated duration of the trip is too long.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = 'Estimated duraction of the trip must be a number.'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                departure_country = request.POST.get("departure_country")  # TravelDetail.DepartureCountry
                if len(departure_country) > 25:
                    error_messages['fatal_errors'] = 'Departure countrys name must not exceed 25 characters.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                departure_factory_code = request.POST.get("factory_code")
                if len(departure_factory_code) > 30:
                    error_messages['fatal_errors'] = 'Departure Factory Code cannot exceed 30 characters.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                destination_country = request.POST.get("country2")  # TravelDetail.DepartureCountry
                if len(destination_country) > 25:
                    error_messages['fatal_errors'] = 'Country of destination cannot exceed 25 characters.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                departure_prefferred = request.POST.get("departure_state")
                if len(departure_prefferred) > 50:
                    error_messages['fatal_errors'] = 'Departure state name cannot exceed 50 characters.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                destination_state = request.POST.get("state2")  # TravelDetail.DestinationState
                if len(destination_state) > 50:
                    error_messages['fatal_errors'] = 'Destination state name cannot exceed 50 characters.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                destination_city = request.POST.get("destination_city")  # TravelDetail.DestinationCity
                if len(destination_city) > 40:
                    error_messages['fatal_errors'] = 'Destination city name must not exceed 40 characters.'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                transportation_type = request.POST.get("transportation_type")  # TravelDetail.transportation
                if transportation_type != 'Flight' and transportation_type != 'Train' and transportation_type != 'Rental Car':
                    error_messages['fatal_errors'] = 'Transportation type must be flight, Train, or Rental Car, not' + transportation_type + '.\n'
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                accomodation_type = request.POST.get("accommodation_type")  # TravelDetail.accommodation
                if accomodation_type != 'Hotel' and accomodation_type != 'Dormitory':
                    error_messages['fatal_errors'] = "Travel accommodation type must be Hotel or Dormitory, not " + accomodation_type
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                currency = request.POST.get("country_currency")
                if len(currency) > 50:
                    error_messages['fatal_errors'] = "Currency must not exceed 50 characters"
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                try:
                    old_travel_detail_form.save_travel_detail(formID=form_id, company=company,
                                                              startDate=travel_datefrom,
                                                              departurePrefferred=departure_prefferred,
                                                              endDate=travel_dateto,
                                                              departureCountry=departure_country,
                                                              departureFactoryCode=departure_factory_code,
                                                              destinationState=destination_state,
                                                              destinationCity=destination_city,
                                                              destinationCountry=destination_country,
                                                              transportation=transportation_type,
                                                              accommodation=accomodation_type,
                                                              date=None, isCompleted=is_completed,
                                                              estimatedDuration=estimated_duration, currency=currency)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = "Errors saving top half of the second page of the form. Please contact IT"
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                # endregion

                # region The Rows and Columns (wich is part of Section 2 but is so long it gets its own region apart from it)
                detail_id = TravelDetail.objects.get(
                    detailID=old_travel_detail_form.detailID)  # TravelDetailCompany.detailID
                visit_dates = all_post_data['visit_date']  # Get keys that contain this
                visit_companies = all_post_data["visit_company"]
                visit_departments = all_post_data["visit_department"]
                contacts = all_post_data["company_contact"]
                objectives = all_post_data["visit_objective"]
                try:
                    visit_ids = all_post_data["visit_id"]  # This field only exists on a saved form
                except:
                    print('no old visit ids to attain')
                index = 0
                rows = 0

                print("Visit Dates: " + str(visit_dates))

                # Check to see if there are multiple rows:
                if str(visit_dates) != '':
                    if ',' in str(visit_dates):
                        print('There are multiple rows')
                        there_are_multiple_rows = True

                    else:
                        print('there is only one row')
                        there_are_multiple_rows = False

                    if there_are_multiple_rows:
                        for row in visit_dates:
                            rows += 1
                        for row in visit_dates:
                            if index < rows:
                                visit_date = row  # TravelDetailCompany.date
                                if row != '':
                                    try:
                                        datetime.strptime(row, '%Y-%m-%d')
                                    except:
                                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                                        error_messages['fatal_errors'] = "Travel purpose date needs to have a date value"
                                        response_data['result'] = error_messages
                                        return HttpResponse(
                                            json.dumps(response_data),
                                            content_type="application/json"
                                        )
                                visit_company = visit_companies[index]  # TravelDetailCompany.visitCompany
                                if len(visit_company) > 50:
                                    error_messages['fatal_errors'] = "Travel purpose visit company must not exceed 50 characters"
                                    response_data['result'] = error_messages
                                    return HttpResponse(
                                        json.dumps(response_data),
                                        content_type="application/json"
                                    )

                                visit_department = visit_departments[index]  # TravelDetailCompany.department
                                if len(visit_department) > 50:
                                    error_messages['fatal_errors'] = "Travel Purpose visit department must not exceed 50 characters"
                                    response_data['result'] = error_messages
                                    return HttpResponse(
                                        json.dumps(response_data),
                                        content_type="application/json"
                                    )

                                contact = contacts[index]  # TravelDetailCompany.contact
                                if len(contact) > 60:
                                    error_messages['fatal_errors'] = "Travel Purpose visit contact must not exceed 60 characters"
                                    response_data['result'] = error_messages
                                    return HttpResponse(
                                        json.dumps(response_data),
                                        content_type="application/json"
                                    )

                                objective = objectives[index]  # TravelDetailCompany.preciseObjective
                                if len(objective) > 50:
                                    error_messages['fatal_errors'] = "Travel purpose objectives must not exceeed 50 characters"
                                    response_data['result'] = error_messages
                                    return HttpResponse(
                                        json.dumps(response_data),
                                        content_type="application/json"
                                    )

                                try:
                                    # Try will update an edited row. If there is no row to update...
                                    current = TravelDetailCompany.objects.get(visitID=visit_ids[index])
                                    current.save_detail_company(visitCompany=visit_company, department=visit_department,
                                                                contact=contact, date=visit_date,
                                                                preciseObjective=objective,
                                                                detailID=detail_id, isCompleted=is_completed)
                                except:
                                    # ...it will throw an error which except will catch. Except will create a new row instead of updating an old one
                                    print('more feilds than last save for create detail company')
                                    TravelDetailCompany().save_detail_company(visitCompany=visit_company,
                                                                              department=visit_department,
                                                                              contact=contact, date=visit_date,
                                                                              preciseObjective=objective,
                                                                              detailID=detail_id,
                                                                              isCompleted=is_completed)
                                index += 1
                                print("Rows: " + str(rows))
                                print("Index: " + str(index))
                            else:
                                break
                    # Delete rows that have been deleted in the javascript
                    try:
                        for form in old_company_forms:
                            if str(form.visitID) not in str(visit_ids) and form.visitID != visit_ids:
                                form_to_delete = TravelDetailCompany.objects.get(visitID=form.visitID)
                                form_to_delete.delete()
                    except:
                        print("No old forms to delete")

                    # If there is only one row:
                    if there_are_multiple_rows == False:
                        try:
                            # Try will update an edited row. If there is no row to update...
                            print("old_company_forms[0].visitID: " + str(old_company_forms[0].visitID))
                            form_to_update = TravelDetailCompany.objects.get(visitID=old_company_forms[0].visitID)
                            form_to_update.save_detail_company(visitCompany=visit_companies,
                                                               department=visit_departments,
                                                               contact=contacts, date=visit_dates,
                                                               preciseObjective=objectives, detailID=detail_id,
                                                               isCompleted=is_completed)
                        except:
                            try:
                                # ...it will throw an error which except will catch. Except will create a new row instead of updating an old one
                                print("Creating new travel detail company")
                                TravelDetailCompany().save_detail_company(visitCompany=visit_companies[0],
                                                                          department=visit_departments[0],
                                                                          contact=contacts[0], date=visit_dates[0],
                                                                          preciseObjective=objectives[0],
                                                                          detailID=detail_id, isCompleted=is_completed)
                            except:
                                print("No travel detail Company information to save")
                # endregion

                # Section 3 - Zaawar Ejaz
                # region Section 3
                allowance = validate_number(request.POST.get('allowance'), 99999999.99) * validate_number(
                    request.POST.get('estimated_period'), 99999999.99)
                if allowance != '':
                    try:
                        if float(allowance) > 99999999.99:
                            error_messages['fatal_errors'] = "Total per diem amount is too big"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "Per diem amount must be a number"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                allowance_detail = request.POST.get('explanation_allowance')
                if len(allowance_detail) > 100:
                    error_messages['fatal_errors'] = "Allowance Explanation must not exceed 100 characters"
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                accomodation_expense = request.POST.get('accommodation')
                if accomodation_expense != '':
                    try:
                        if float(accomodation_expense) > 99999999.99:
                            error_messages['fatal_errors'] = "Accommodation amount is too large"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "Accommodation amount must be a number"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                transport_expense = request.POST.get('transportation')
                if transport_expense != '':
                    try:
                        if float(transport_expense) > 99999999.99:
                            error_messages['fatal_errors'] = "Transportation expense is too large"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "Transportation expense must be a number"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                transport_detail = request.POST.get('explaination_transportation')
                if len(transport_detail) > 100:
                    error_messages['fatal_errors'] = "Transportation explanation must not exceed 100 characters"
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                public_relation_expense = request.POST.get('public_relationship')
                if public_relation_expense != '':
                    try:
                        if float(public_relation_expense) > 99999999.99:
                            error_messages['fatal_errors'] = "Public Relationship expense is too large"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "Public relationship expense must be a number"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                public_relation_detail = request.POST.get('explanation_publicrelationship')
                if len(public_relation_detail) > 100:
                    error_messages['fatal_errors'] = "Public Relationship Explanation must not exceed 100 characters"
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                other_expense = request.POST.get('other_expense')
                if other_expense != '':
                    try:
                        if float(other_expense) > 99999999.99:
                            error_messages['fatal_errors'] = "Other expense amount is too large"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "Other expense amount must be a number"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                other_explanation = request.POST.get('explaination_otherexpense')
                if len(other_explanation) > 100:
                    error_messages['fatal_errors'] = "Other expense explanation must not exceed 100 characters"
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                total_expenses = request.POST.get('total')
                if total_expenses != '':
                    try:
                        if float(total_expenses) > 99999999.99:
                            error_messages['fatal_errors'] = "Total expense amount is too large"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "Total expense amount must be a number"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                print("**TOTAL: " + str(total_expenses))

                ticket_exp = request.POST.get('explaination_airwayticket')
                ticket_exp = validate_string(ticket_exp, 100)

                ticket = validate_number(request.POST.get('airway_ticket'), 99999999.99)

                old_expense_form.save_detail_expense(detailID=detail_id, date=None, allowance=allowance,
                                                     allowanceExp=allowance_detail, accommodation=accomodation_expense,
                                                     accommodationExp=None,
                                                     transportation=transport_expense,
                                                     transportationExp=transport_detail, visa=None,
                                                     visaExp=None, airwayTicket=ticket,
                                                     airwayTicketExp=ticket_exp, insurance=None,
                                                     insuranceExp=None, other=other_expense,
                                                     otherExp=other_explanation, total=total_expenses,
                                                     isCompleted=is_completed, publicRelation=public_relation_expense,
                                                     publicRelationExp=public_relation_detail)

                if request.POST.get('travel_advance_apply') == 'true':
                    advance_amount = request.POST.get('advance_amount')
                    if validate_number(advance_amount, 99999999999.99) > validate_number(old_expense_form.allowance,
                                                                                         99999999999.99) + validate_number(
                        old_expense_form.publicRelationship, 99999999999.99) + validate_number(
                        old_expense_form.accommodation, 99999999999.99):
                        error_messages['fatal_errors'] = "Travel advance is greater than maximum advance amount"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    gl_account = request.POST.get('gl_account')
                    if len(gl_account) > 50:
                        error_messages['fatal_errors'] = "GL Account must not exceed 50 characters"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    gl_detail = request.POST.get('gl_description')
                    if len(gl_detail) > 50:
                        error_messages['fatal_errors'] = "Travel Advance GL description must not exceed 50 characters"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    cost_center = request.POST.get('cost_center')
                    if len(cost_center) > 50:
                        error_messages['fatal_errors'] = "Travel Advance Cost Center must not exceed 50 characters"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    profit_center = request.POST.get('advanceprofit_center')
                    if len(profit_center) > 50:
                        error_messages['fatal_errors'] = "Travel advance profit center must not exceed 50 characters"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    head_text = request.POST.get('head_text')
                    if len(head_text) > 50:
                        error_messages['fatal_errors'] = "Travel Advance Head Text must not exceed 50 characters"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    text = request.POST.get('text')
                    if len(text) > 50:
                        error_messages['fatal_errors'] = "Travel Advance Text must not exceed 50 characters"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    assignment = request.POST.get('assignment')
                    if len(assignment) > 100:
                        error_messages['fatal_errors'] = "Travel Advance assignment must not exceed 100 characters"
                        response_data['result'] = error_messages
                        response_data['result'] = 'Travel Advance assignment must not exceed 100 characters.\n'
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    reference_doc = request.POST.get('reference_document')
                    if len(reference_doc) > 50:
                        error_messages['fatal_errors'] = "Travel Advance reference document must not exceed 50 characters"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    currency = request.POST.get("country_currency")
                    if len(currency) > 50:
                        error_messages['fatal_errors'] = "Currenct must not exceed 100 characters"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    vendor_code = request.POST.get("vendor_code")
                    if len(vendor_code) > 15:
                        error_messages['fatal_errors'] = "Travel Advance Vendor Code must not exceed 15 characters"
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    company_code = LegalEntity.objects.get(entityName=request.session['legal_entity_name']).sapCompCode

                    if old_advance_form == None:
                        adv = AdvanceTravelApp().save_adv_app(formID=old_emp_info_form, advAmount=advance_amount,
                                                              glAccount=gl_account, glDescription=gl_detail,
                                                              costCenterCode=cost_center,
                                                              profitCenter=profit_center, headText=head_text,
                                                              text=text, assignment=assignment,
                                                              isCompleted=is_completed,
                                                              refDocument=reference_doc,
                                                              dateApplied=datetime.now(), currency=currency,
                                                              vendorCode=vendor_code, companyCode=company_code)

                        SAPAdvApp().create_entries(advID=adv.advID)

                    else:
                        adv = old_advance_form.save_adv_app(formID=old_emp_info_form, advAmount=advance_amount,
                                                            glAccount=gl_account, glDescription=gl_detail,
                                                            costCenterCode=cost_center,
                                                            profitCenter=profit_center, headText=head_text,
                                                            text=text, assignment=assignment, isCompleted=is_completed,
                                                            refDocument=reference_doc,
                                                            dateApplied=datetime.now(), currency=currency,
                                                            vendorCode=vendor_code, companyCode=company_code)

                        SAPAdvApp().create_entries(advID=adv.advID)

                else:
                    try:
                        old_advance_form.delete()
                    except:
                        print("no old advance form to delete")

                if is_completed:
                    error_messages = merge_dictionaries(error_messages, old_emp_info_form.initialize_ta_approval_process(request))
                    if error_messages['fatal_errors'] != "":
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                    messages.success(request, "Form has been saved correctly")
                    for error in error_messages['other_errors']:
                        messages.error(request, error)
                    response_data['result'] = error_messages
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                else:
                    messages.success(request, "Form has been saved correctly")
                for message in error_messages['other_errors']:
                    messages.error(request, message)
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            else:
                if form_is_declined:
                    form_is_being_shown_to_approver = True
                else:
                    form_is_being_shown_to_approver = False
                print("User is Creator: " + str(user_is_creator))
                print("form is totally approved: " + str(form_is_completely_approved))
                try:
                    if (old_emp_info_form.employee == Employee.objects.filter(
                            email=request.user.email).first() or old_emp_info_form.employee == Employee.objects.filter(
                        personalEmail=request.user.email).first()) and \
                            TemporaryApprovalStage.objects.get(formID=old_emp_info_form, stage=(
                                    old_emp_info_form.currentStage - 1)).actionTaken == 'Requested Modifications':
                        approving_modifications = True
                        # Also get all fields that have been modified and put them in a list (modified_fields)
                        modified_fields = ModifiedFields.objects.filter(formID=old_emp_info_form.formID)
                    else:
                        approving_modifications = False
                        modified_fields = []
                except:
                    approving_modifications = False
                    modified_fields = []
                print("all stages: " + str(all_forms_stages))
                return render(request, "travel/index.html", {"today": datetime.now(),
                                                             "form_is_being_approved": False,
                                                             "form_is_being_shown_to_approver": form_is_being_shown_to_approver,
                                                             "full_name": request.session["full_name"],
                                                             "user_dept": request.session['department'],
                                                             "business_unit": request.session["business_unit"],
                                                             "departments": departments,
                                                             "business_groups": business_groups,
                                                             "business_units": BusinessUnit.objects.all(),
                                                             'companies': companies,
                                                             'old_emp_form': old_emp_info_form,
                                                             'old_company_forms': old_company_forms,
                                                             'old_detail_form': old_travel_detail_form,
                                                             'old_expense_form': old_expense_form,
                                                             'old_advance_form': old_advance_form,
                                                             'there_are_multiple_old_company_forms': there_are_multiple_old_company_forms,
                                                             'business_unit_code': request.session[
                                                                 'business_unit_code'],
                                                             'user_dept_code': request.session['department_code'],
                                                             "factory_codes": Building.objects.all(),
                                                             "approving_modifications": approving_modifications,
                                                             "modified_fields": [],
                                                             #"all_forms_stages": [],
                                                             "users_stage": users_stage,
                                                             "current_date": datetime.today(),
                                                             "form_is_declined": form_is_declined,
                                                             "form_is_completely_approved": form_is_completely_approved,
                                                             "user_is_creator": user_is_creator,
                                                             "approvers_in_chat": get_approvers_for_form_at_current_stage_or_lower(
                                                                 form=old_emp_info_form,
                                                                 approval_stage_type=TemporaryApprovalStage),
                                                             "all_forms_approvers": get_approvers_for_form(
                                                                 form=old_emp_info_form,
                                                                 approval_stage_type=TemporaryApprovalStage),
                                                             "vendor": vendor,
                                                             "employee_business_group": employee_business_group,
                                                             "employee_company": employee_company,
                                                             "all_forms_stages": all_forms_stages})
        else:
            if old_emp_info_form.employee.middleName == None or old_emp_info_form.employee.middleName == '':
                user_fullname = str(old_emp_info_form.employee.firstName) + " " + str(
                    old_emp_info_form.employee.lastName)
            else:
                user_fullname = str(old_emp_info_form.employee.firstName) + " " + str(
                    old_emp_info_form.employee.middleName) + " " + str(old_emp_info_form.employee.lastName)
            user_department = employee_dept_object.departmentID
            user_business_unit = employee_dept_object.departmentID.businessUnit
            user_business_unit_code = employee_dept_object.departmentID.profitCenterCode

            # forms_to_show = []
            # forms_to_approve = []

            users_temp_approval_stages = []

            # Loop through approval stage objects that say user is a part of the approval stage
            # If the current stage of the form object is the stage of the approval stage object,
            #   and the user has taken no action, add that  to a list that will be displayed in the template
            # for temp_approval_stage in users_temp_approval_stages:
            #     forms_to_show.append(temp_approval_stage.formID)
            #     # Add to approval list:
            #     print(f"Checking stage: {temp_approval_stage}")
            #     if (temp_approval_stage.formID.currentStage == temp_approval_stage.stage) \
            #             and (temp_approval_stage.formID.isApproved == False) \
            #             and (temp_approval_stage.actionTaken == None or temp_approval_stage.actionTaken == '' or temp_approval_stage.actionTaken == 'Requested Modifications' or temp_approval_stage.actionTaken == '?') \
            #             and (temp_approval_stage.formID == old_emp_info_form):
            #         print(f"********************************************approval stage is accepted!")
            #         forms_to_approve.append(temp_approval_stage.formID)

            # This line removes duplicates:
            # forms_to_approve = list(dict.fromkeys(forms_to_approve))
            # forms_to_show = list(dict.fromkeys(forms_to_show))

            # Get other temporary Approval Stage Objects for the form that have already approved the form so that I can show it:
            stages_already_finished = TemporaryApprovalStage.objects.filter(formID=old_emp_info_form,
                                                                            stage__range=[1,
                                                                                          old_emp_info_form.currentStage - 1])

            all_forms_stages = TemporaryApprovalStage.objects.filter(formID=old_emp_info_form).order_by('stage')

            if user_has_stage_for_form or old_emp_info_form.employee == employee:
                form_is_being_shown_to_approver = True
            else:
                form_is_being_shown_to_approver = False

            form_is_being_approved = False
            if user_has_stage_for_form:
                if users_stage.formID == old_emp_info_form:
                    form_is_being_approved = True

            if user_has_stage_for_form or user_is_creator or request.session['department'] == 'Supporting - General Service':
                old_travel_detail_form = TravelDetail.objects.get(formID=old_emp_info_form.formID)
                old_company_forms = TravelDetailCompany.objects.filter(detailID=old_travel_detail_form.detailID)
                old_expense_form = TravelDetailExpenses.objects.get(detailID=old_travel_detail_form.detailID)
                old_advance_form = AdvanceTravelApp.objects.filter(formID=old_emp_info_form.formID).first()
                there_are_multiple_old_company_forms = False
                try:
                    for form in old_company_forms:
                        print("Old company form date: " + str(form.date))
                        there_are_multiple_old_company_forms = True
                except:
                    print("only one old company form")
                    there_are_multiple_old_company_forms = False
                # If user is creator of the form AND the step abouve them's actionTaken = 'Requested Modifications' then set approving_modifications to True
                try:
                    # check all stages for next stage and see if any of them have Requested Modifications for their action
                    above_stages = TemporaryApprovalStage.objects.filter(formID=old_emp_info_form,
                                                       stage=(old_emp_info_form.currentStage - 1))
                    modification_request_was_sent = False
                    for stage in above_stages:
                        if stage.actionTaken == 'Requested Modifications':
                            modification_request_was_sent = True
                    if (old_emp_info_form.employee == Employee.objects.filter(
                            email=request.user.email).first()) and TemporaryApprovalStage.objects.get(
                        formID=old_emp_info_form, stage=(
                                old_emp_info_form.currentStage - 1)).actionTaken == 'Requested Modifications':
                        approving_modifications = True
                        # Also get all fields that have been modified and put them in a list (modified_fields)
                        modified_fields = ModifiedFields.objects.filter(formID=old_emp_info_form.formID)
                    else:
                        approving_modifications = False
                        modified_fields = []
                except:
                    approving_modifications = False
                    modified_fields = []

                try:
                    factory_codes = Building.objects.all()
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    return HttpResponse("Error retrieving Building data. Please contact IT")

                try:
                    users_factory = Building.objects.filter(
                        legalEntity=LegalEntity.objects.get(entityName=request.session['legal_entity_name'])).first()
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    return HttpResponse("Error retrieving Building data. Please contact IT")

                # Getting post data
                if request.method == 'POST':
                    all_post_data = dict(request.POST)
                    print("All post data: " + str(request.POST))

                if request.POST.get('submit_button') == 'Approve':
                    error_messages = merge_dictionaries(error_messages, approve_form(request, old_emp_info_form, approval_process_type=TemporaryApprovalStage, advance_type=AdvanceTravelApp))
                    response_data['result'] = error_messages
                    if error_messages['fatal_errors'] == '':
                        messages.success(request, "Travel form successfully approved!")
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                if request.POST.get('submit_button') == 'Submit and Approve':
                    allowance = validate_number(request.POST.get('allowance'), 99999999.99) * validate_number(
                        request.POST.get('estimated_period'), 99999999.99)
                    allowance_detail = request.POST.get('explanation_allowance')
                    accomodation_expense = request.POST.get('accommodation')
                    transport_expense = request.POST.get('transportation')
                    transport_detail = request.POST.get('explaination_transportation')
                    public_relation_expense = request.POST.get('public_relationship')
                    public_relation_detail = request.POST.get('explanation_publicrelationship')
                    other_expense = request.POST.get('other_expense')
                    total_expenses = request.POST.get('total')

                    if request.POST.get('advance_amount') is not None and request.POST.get(
                            'advance_amount') != 0 and request.POST.get('advance_amount') != '' and request.session[
                        'department'] == 'Supporting - Accounting':

                        advance_amount = request.POST.get('advance_amount')
                        if validate_number(advance_amount, 999999999.99) > validate_number(allowance,
                                                                                           999999999.99) + validate_number(
                            public_relation_expense, 999999999.99) + validate_number(
                            accomodation_expense, 999999999.99):
                            error_messages['fatal_errors'] = "Error saving form. Travel Advance amount is greater than amount allowed"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        gl_account = request.POST.get('gl_account')
                        if len(gl_account) > 50:
                            error_messages[
                                'fatal_errors'] = "Error saving form. Travel Advance GL Account can only be up to 50 characters"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        gl_detail = request.POST.get('gl_description')
                        if len(gl_detail) > 50:
                            error_messages['fatal_errors'] = "Error saving form. Travel Advance GL Description can only be up to 50 characters"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        cost_center = request.POST.get('cost_center')
                        if len(cost_center) > 50:
                            error_messages[
                                'fatal_errors'] = "Error saving form. Travel Advance Cost Center can only be up to 50 characters."
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        profit_center = request.POST.get('advanceprofit_center')
                        if len(profit_center) > 50:
                            error_messages['fatal_errors'] = "Error saving form. Travel Advance Profit Center can only be up to 50 characters"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        head_text = request.POST.get('head_text')
                        if len(head_text) > 50:
                            error_messages['fatal_errors'] = "Error saving form. Travel Head Text can only be up to 25 characters"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        text = request.POST.get('text')
                        if len(text) > 50:
                            error_messages['fatal_errors'] = "Error saving form. Travel Advance Text can only be up to 25 characters"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        assignment = request.POST.get('assignment')

                        if len(assignment) > 100:
                            error_messages[
                                'fatal_errors'] = "Error saving form. Travel Advance Assignment can only be up to 100 characters"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        reference_doc = request.POST.get('reference_document')
                        if len(reference_doc) > 50:
                            error_messages['fatal_errors'] = "Error saving form. Travel Advance Reference Document can only be up to 50 characters"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        currency = request.POST.get("country_currency")
                        if len(currency) > 50:
                            error_messages[
                                'fatal_errors'] = "Error saving form. Currency can only be up to 50 characters"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        vendor_code = request.POST.get("vendor_code")
                        if len(vendor_code) > 15:
                            messages.error(request,
                                           "Error saving form. Vendor Code can only be up to 15 characters.")
                            error_messages['fatal_errors'] = "Error saving form. Vendor Code can only be up to 15 characters"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        company_code = None
                        try:
                            company_code = LegalEntity.objects.get(
                                entityName=request.session['legal_entity_name']).sapCompCode
                        except:
                            error_messages['fatal_errors'] = "Error saving form. System could not get company code. Please contact IT"
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                        if old_advance_form != None:
                            old_advance_form.save_adv_app(formID=old_emp_info_form,
                                                          advAmount=request.POST.get('advance_amount'),
                                                          glAccount=request.POST.get('gl_account'),
                                                          glDescription=request.POST.get('gl_description'),
                                                          costCenterCode=request.POST.get('cost_center'),
                                                          profitCenter=request.POST.get('advanceprofit_center'),
                                                          headText=request.POST.get('head_text'),
                                                          text=request.POST.get('text'),
                                                          assignment=request.POST.get('assignment'),
                                                          isCompleted=True,
                                                          refDocument=request.POST.get('reference_document'),
                                                          dateApplied=datetime.now(),
                                                          currency=currency,
                                                          vendorCode=vendor_code,
                                                          companyCode=company_code)

                            SAPAdvApp.objects.filter(formID=old_emp_info_form).delete()
                            SAPAdvApp().create_entries(advID=old_advance_form.advID)

                    error_messages = merge_dictionaries(error_messages, approve_form(request, approval_process_type=TemporaryApprovalStage, form=old_emp_info_form, advance_type=AdvanceTravelApp))
                    response_data['result'] = error_messages
                    if error_messages['fatal_errors'] == '':
                        messages.success(request, "Travel form successfully updated and approved!")
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                if request.POST.get('submit_button') == 'Approve Modifications':
                    # save any new data
                    all_post_data = dict(request.POST)
                    print("All post data: " + str(request.POST))

                    # Sections 1 & 2 - Corrina Barr
                    # region Section 1
                    employee = old_emp_info_form.employee  # EmployeeInformation.employee
                    company = old_emp_info_form.company  # EmployeeInformation.company
                    BG = old_emp_info_form.businessGroup

                    project = request.POST.get("project")  # EmployeeInformation.project
                    estimated_expense = request.POST.get("estimated_expense")  # EmployeeInformation.estiematedExpense
                    travel_type = request.POST.get("travel_type")  # EmployeeInformation.travelType

                    budget_sc = request.POST.get("budget_sc")  # EmployeeInformation.bugdetSourceCode

                    is_completed = True

                    old_emp_info_form.save_travel_form(company=company, bg=BG, employee=employee, project=project,
                                                       estimatedExpense=estimated_expense, travelType=travel_type,
                                                       budgetSourceCode=budget_sc,
                                                       advancedApp=False, isCompleted=is_completed)
                    # endregion

                    # region Section 2
                    form_id = EmployeeInformation.objects.get(formID=old_emp_info_form.formID)  # TravelDetail.formID
                    company = form_id.company  # TravelDetail.company
                    travel_datefrom = request.POST.get("travel_datefrom")  # TravelDetail.startDate
                    travel_dateto = request.POST.get("travel_dateto")  # TravelDetail.endDate
                    estimated_duration = request.POST.get("estimated_period")  # TravelDetail.estimatedDuration

                    departure_country = request.POST.get("departure_country")  # TravelDetail.DepartureCountry
                    departure_factory_code = request.POST.get("factory_code")
                    print("************************DEP FACt CODE 6: " + str(departure_factory_code))
                    destination_country = request.POST.get("country2")  # TravelDetail.DepartureCountry
                    departure_prefferred = request.POST.get("departure_state")
                    destination_state = request.POST.get("state2")  # TravelDetail.DestinationState
                    destination_city = request.POST.get("destination_city")  # TravelDetail.DestinationCity

                    transportation_type = request.POST.get("transportation_type")  # TravelDetail.transportation
                    accomodation_type = request.POST.get("accommodation_type")  # TravelDetail.accommodation
                    date = request.POST.get("date")  # TravelDetail.date

                    currency = request.POST.get("country_currency")
                    if len(currency) > 50:
                        messages.error(request,
                                       "Error saving form. Currency can only be up to 50 characters.")
                        there_are_errors = True

                    # I will need to update this
                    print("************************DEP FACt CODE 7: " + str(departure_factory_code))
                    old_travel_detail_form.save_travel_detail(formID=form_id, company=company,
                                                              startDate=travel_datefrom,
                                                              endDate=travel_dateto,
                                                              departurePrefferred=departure_prefferred,
                                                              departureCountry=departure_country,
                                                              departureFactoryCode=departure_factory_code,
                                                              destinationState=destination_state,
                                                              destinationCity=destination_city,
                                                              destinationCountry=destination_country,
                                                              transportation=transportation_type,
                                                              accommodation=accomodation_type,
                                                              date=date, isCompleted=is_completed,
                                                              estimatedDuration=estimated_duration, currency=currency)
                    # endregion

                    # region The Rows and Columns (which is part of Section 2 but is so long it gets its own region apart from it)
                    detail_id = TravelDetail.objects.get(
                        detailID=old_travel_detail_form.detailID)  # TravelDetailCompany.detailID
                    visit_dates = all_post_data['visit_date']  # Get keys that contain this
                    visit_companies = all_post_data["visit_company"]
                    visit_departments = all_post_data["visit_department"]
                    contacts = all_post_data["company_contact"]
                    objectives = all_post_data["visit_objective"]
                    try:
                        visit_ids = all_post_data["visit_id"]  # This field only exists on a saved form
                    except:
                        print('no old visit ids to attain')
                    index = 0
                    rows = 0

                    print("Visit Dates: " + str(visit_dates))

                    # Check to see if there are multiple rows:
                    if str(visit_dates) != '':
                        if ',' in str(visit_dates):
                            print('There are multiple rows')
                            there_are_multiple_rows = True

                        else:
                            print('there is only one row')
                            there_are_multiple_rows = False

                        if there_are_multiple_rows:
                            for row in visit_dates:
                                rows += 1
                            for row in visit_dates:
                                if index < rows:
                                    visit_date = row  # TravelDetailCompany.date
                                    visit_company = visit_companies[index]  # TravelDetailCompany.visitCompany
                                    visit_department = visit_departments[index]  # TravelDetailCompany.department
                                    contact = contacts[index]  # TravelDetailCompany.contact
                                    objective = objectives[index]  # TravelDetailCompany.preciseObjective
                                    try:
                                        # Try will update an edited row. If there is no row to update...
                                        current = TravelDetailCompany.objects.get(visitID=visit_ids[index])
                                        current.save_detail_company(visitCompany=visit_company,
                                                                    department=visit_department,
                                                                    contact=contact, date=visit_date,
                                                                    preciseObjective=objective,
                                                                    detailID=detail_id, isCompleted=is_completed)
                                        current.modifiedField = False
                                        current.save()
                                    except:
                                        # ...it will throw an error which except will catch. Except will create a new row instead of updating an old one
                                        print('more feilds than last save for create detail company')
                                        TravelDetailCompany().save_detail_company(visitCompany=visit_company,
                                                                                  department=visit_department,
                                                                                  contact=contact, date=visit_date,
                                                                                  preciseObjective=objective,
                                                                                  detailID=detail_id,
                                                                                  isCompleted=is_completed)
                                    index += 1
                                    print("Rows: " + str(rows))
                                    print("Index: " + str(index))
                                else:
                                    break
                        # Delete rows that have been deleted in the javascript
                        try:
                            for form in old_company_forms:
                                if str(form.visitID) not in str(visit_ids) and form.visitID != visit_ids:
                                    form_to_delete = TravelDetailCompany.objects.get(visitID=form.visitID)
                                    form_to_delete.delete()
                        except:
                            print("No old forms to delete")

                        # If there is only one row:
                        if there_are_multiple_rows == False:
                            try:
                                # Try will update an edited row. If there is no row to update...
                                print("old_company_forms[0].visitID: " + str(old_company_forms[0].visitID))
                                form_to_update = TravelDetailCompany.objects.get(visitID=old_company_forms[0].visitID)
                                form_to_update.save_detail_company(visitCompany=visit_companies,
                                                                   department=visit_departments,
                                                                   contact=contacts, date=visit_dates,
                                                                   preciseObjective=objectives, detailID=detail_id,
                                                                   isCompleted=is_completed)
                            except:
                                try:
                                    # ...it will throw an error which except will catch. Except will create a new row instead of updating an old one
                                    print("Creating new travel detail company")
                                    TravelDetailCompany().save_detail_company(visitCompany=visit_companies[0],
                                                                              department=visit_departments[0],
                                                                              contact=contacts[0], date=visit_dates[0],
                                                                              preciseObjective=objectives[0],
                                                                              detailID=detail_id,
                                                                              isCompleted=is_completed)
                                except:
                                    print("No travel detail Company information to save")
                    # endregion

                    # Section 3 - Zaawar Ejaz
                    # region Section 3
                    allowance = validate_number(request.POST.get('allowance'), 99999999.99) * validate_number(
                        request.POST.get('estimated_period'), 99999999.99)
                    if allowance != '':
                        try:
                            if float(allowance) > 99999999.99:
                                error_messages['fatal_errors'] = 'Error saving form. Allowance amount is too large.'
                                response_data['result'] = error_messages
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )
                        except:
                            print('\n'.join(traceback.format_exception(*sys.exc_info())))
                            error_messages['fatal_errors'] = 'Error saving form. Allowance amount must be a number.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                    allowance_detail = request.POST.get('explanation_allowance')
                    if len(allowance_detail) > 100:
                        error_messages['fatal_errors'] = 'Error saving form. Allowance Explanation must be less than 100 characters.'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    accomodation_expense = request.POST.get('accommodation')
                    if accomodation_expense != '':
                        print("Expense Accommodation:" + accomodation_expense + "END")
                        try:
                            if float(accomodation_expense) > 99999999.99:
                                error_messages['fatal_errors'] = 'Error saving form. Accommodation amount is too large.'
                                response_data['result'] = error_messages
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )
                        except:
                            print('\n'.join(traceback.format_exception(*sys.exc_info())))
                            error_messages['fatal_errors'] = 'Error saving form. Accommodation expense must be a number.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                    transport_expense = request.POST.get('transportation')
                    if transport_expense != 0:
                        try:
                            if float(transport_expense) > 99999999.99:
                                error_messages['fatal_errors'] = 'Error saving form. Transportation expense amount is too large.'
                                response_data['result'] = error_messages
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )
                        except:
                            print('\n'.join(traceback.format_exception(*sys.exc_info())))
                            error_messages['fatal_errors'] = 'Error saving form. Transportation expense amount is must be a number.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                    transport_detail = request.POST.get('explaination_transportation')
                    if len(transport_detail) > 100:
                        error_messages['fatal_errors'] = 'Error saving form. Transportation explanation must be less than 100 characters.'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                    public_relation_expense = request.POST.get('public_relationship')
                    if public_relation_expense != '':
                        try:
                            if float(public_relation_expense) > 99999999.99:
                                error_messages['fatal_errors'] = 'Error saving form. Public relationship expense amount is too large.'
                                response_data['result'] = error_messages
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )
                        except:
                            print('\n'.join(traceback.format_exception(*sys.exc_info())))
                            error_messages['fatal_errors'] = 'Error saving form. Public relationship amount must be a number.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                    public_relation_detail = request.POST.get('explanation_publicrelationship')
                    if len(public_relation_detail) > 100:
                        error_messages['fatal_errors'] = 'Error saving form. Public relationship explanation must be less than 100 characters long.'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    other_expense = request.POST.get('other_expense')
                    if other_expense != '':
                        try:
                            if float(other_expense) > 99999999.99:
                                error_messages['fatal_errors'] = 'Error saving form. Other expense amount is too large.'
                                response_data['result'] = error_messages
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )
                        except:
                            print('\n'.join(traceback.format_exception(*sys.exc_info())))
                            error_messages['fatal_errors'] = 'Error saving form. Other expense amount is must be a number.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                    other_explanation = request.POST.get('explaination_otherexpense')
                    if len(public_relation_detail) > 100:
                        error_messages['fatal_errors'] = 'Error saving form. Public relationship expense must be less than 100 characters.'
                        response_data['result'] = error_messages
                        return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )

                    total_expenses = request.POST.get('total')
                    if total_expenses != '':
                        try:
                            if float(total_expenses) > 99999999.99:
                                error_messages['fatal_errors'] = 'Error saving form. Total expense amount is too large.'
                                response_data['result'] = error_messages
                                return HttpResponse(
                                    json.dumps(response_data),
                                    content_type="application/json"
                                )
                        except:
                            print('\n'.join(traceback.format_exception(*sys.exc_info())))
                            error_messages['fatal_errors'] = 'Error saving form. Total Expenses must be a number.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                    ticket_exp = request.POST.get('explaination_airwayticket')
                    ticket_exp = validate_string(ticket_exp, 100)

                    ticket = validate_number(request.POST.get('airway_ticket'), 99999999.99)

                    old_expense_form.save_detail_expense(detailID=detail_id, date=None, allowance=allowance,
                                                         allowanceExp=allowance_detail,
                                                         accommodation=accomodation_expense,
                                                         accommodationExp=None,
                                                         transportation=transport_expense,
                                                         transportationExp=transport_detail, visa=None,
                                                         visaExp=None, airwayTicket=ticket,
                                                         airwayTicketExp=ticket_exp,
                                                         insurance=None,
                                                         insuranceExp=None, other=other_expense,
                                                         otherExp=other_explanation, total=total_expenses,
                                                         isCompleted=is_completed,
                                                         publicRelation=public_relation_expense,
                                                         publicRelationExp=public_relation_detail)
                    print("\nThis is the line before getting travel_advance_button value\n")
                    if (convert_to_null_if_empty(request.POST.get("advance_amount")) is not None) or (
                            validate_number(request.POST.get("advance_amount"),
                                            float(old_expense_form.allowance) + float(
                                                old_expense_form.publicRelationship) + float(
                                                old_expense_form.accommodation)) != float(0)):
                        print('it knows to try to save Travel Advance')
                        advance_amount = request.POST.get('advance_amount')
                        if float(advance_amount) > float(old_expense_form.allowance) + float(
                                old_expense_form.publicRelationship) + float(old_expense_form.accommodation):
                            error_messages['fatal_errors'] = 'Error saving form. Travel Advance amount is greater than amount allowed.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        gl_account = request.POST.get('gl_account')
                        if len(gl_account) > 50:
                            error_messages['fatal_errors'] = 'Error saving form. Travel Advance GL Account can only be up to 50 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        gl_detail = request.POST.get('gl_description')
                        if len(gl_detail) > 50:
                            error_messages['fatal_errors'] = 'Error saving form. Travel Advance GL Description can only be up to 50 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        cost_center = request.POST.get('cost_center')
                        if len(cost_center) > 50:
                            error_messages['fatal_errors'] = 'Error saving form. Travel Advance Cost Center can only be up to 50 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        profit_center = request.POST.get('advanceprofit_center')
                        if len(profit_center) > 50:
                            error_messages['fatal_errors'] = 'Error saving form. Travel Advance Profit Center can only be up to 50 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        head_text = request.POST.get('head_text')
                        if len(head_text) > 50:
                            error_messages['fatal_errors'] = 'Error saving form. Travel Advance Head Text can only be up to 25 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        text = request.POST.get('text')
                        if len(text) > 50:
                            error_messages['fatal_errors'] = 'Error saving form. Travel Advance Text can only be up to 25 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        assignment = request.POST.get('assignment')
                        if len(assignment) > 100:
                            error_messages['fatal_errors'] = 'Error saving form. Travel Advance Assignment can only be up to 100 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        reference_doc = request.POST.get('reference_document')
                        if len(reference_doc) > 50:
                            error_messages['fatal_errors'] = 'Error saving form. Travel Advance Reference Document can only be up to 50 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        currency = request.POST.get("country_currency")
                        if len(currency) > 50:
                            error_messages['fatal_errors'] = 'Error saving form. Currency can only be up to 50 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )

                        vendor_code = request.POST.get("vendor_code")
                        if len(vendor_code) > 15:
                            error_messages['fatal_errors'] = 'Error saving form. Vendor code can only be up to 15 characters.'
                            response_data['result'] = error_messages
                            return HttpResponse(
                                json.dumps(response_data),
                                content_type="application/json"
                            )
                        try:
                            company_code = LegalEntity.objects.get(
                                entityName=request.session['legal_entity_name']).sapCompCode

                            if old_advance_form == None:
                                adv = AdvanceTravelApp().save_adv_app(formID=form_id, advAmount=advance_amount,
                                                                      glAccount=gl_account, glDescription=gl_detail,
                                                                      costCenterCode=cost_center,
                                                                      profitCenter=profit_center,
                                                                      headText=head_text,
                                                                      text=text, assignment=assignment,
                                                                      isCompleted=is_completed,
                                                                      refDocument=reference_doc,
                                                                      dateApplied=datetime.now(), currency=currency,
                                                                      vendorCode=vendor_code, companyCode=company_code)

                                SAPAdvApp().create_entries(advID=adv.advID)

                            else:
                                adv = old_advance_form.save_adv_app(formID=form_id, advAmount=advance_amount,
                                                              glAccount=gl_account, glDescription=gl_detail,
                                                              costCenterCode=cost_center,
                                                              profitCenter=profit_center, headText=head_text,
                                                              text=text, assignment=assignment,
                                                              isCompleted=is_completed,
                                                              refDocument=reference_doc,
                                                              dateApplied=datetime.now(),
                                                              vendorCode=vendor_code,
                                                              companyCode=company_code,
                                                              currency=currency)

                                SAPAdvApp().create_entries(advID=adv.advID)
                        except:
                            print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    else:
                        try:
                            print("advance: " + str(request.POST.get("advance_amount")))
                            print("deleteing adv")
                            old_advance_form.delete()
                        except:
                            print("no old advance form to delete")
                    # endregion

                    error_messages = merge_dictionaries(error_messages, approve_modifications(request=request,
                                          form=old_emp_info_form,
                                          approval_process_type=TemporaryApprovalStage,
                                          modified_fields_type=ModifiedFields))
                    response_data['result'] = error_messages
                    if error_messages['fatal_errors'] != "":
                        messages.success(request, "Modifications successfully approved!")
                    for error in error_messages['other_errors']:
                        messages.error(request, error)
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                if request.POST.get('submit_button') == 'Decline Modifications':
                    error_messages = merge_dictionaries(error_messages, decline_modifications(request=request,
                                          form=old_emp_info_form,
                                          approval_process_type=TemporaryApprovalStage,
                                          modified_fields_type=ModifiedFields))
                    response_data['result'] = error_messages
                    if error_messages['fatal_errors'] != "":
                        messages.success(request, "Modifications successfully declined!")
                    for error in error_messages['other_errors']:
                        messages.error(request, error)
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                if request.POST.get('submit_button') == 'Decline':
                    error_messages = merge_dictionaries(error_messages, decline_form(request=request, form=old_emp_info_form, approval_process_type=TemporaryApprovalStage))
                    response_data['result'] = error_messages
                    if error_messages['fatal_errors'] != "":
                        messages.success(request, "Travel Application successfully declined!")
                    for error in error_messages['other_errors']:
                        messages.error(request, error)
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                if request.POST.get('submit_button') == 'Send Modified':
                    # region Check values stored in old forms. If they do not match, add them to the modifiedFields table in database.

                    all_post_data = dict(request.POST)

                    if request.POST.get("project") != old_emp_info_form.project:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("project"),
                                                       fieldID='project', formID=old_emp_info_form.formID)

                    if float(request.POST.get("estimated_expense")) != float(old_emp_info_form.estimatedExpense):
                        ModifiedFields().modify_fields(fieldData=request.POST.get("estimated_expense"),
                                                       fieldID='estimated_expense', formID=old_emp_info_form.formID)

                    if request.POST.get("travel_type") != old_emp_info_form.travelType:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("travel_type"),
                                                       fieldID='travel_type', formID=old_emp_info_form.formID)

                    if request.POST.get("budget_sc") != old_emp_info_form.budgetSourceCode:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("budget_sc"),
                                                       fieldID='budget_sc', formID=old_emp_info_form.formID)
                    # There is no cost description field...
                    # ...but because budget source code always changes when cost desc changes,
                    # I can use budget_sc to see if cost description changed.
                    if request.POST.get("budget_sc") != old_emp_info_form.budgetSourceCode:
                        ModifiedFields().modify_fields(
                            fieldData=CostCenter.objects.get(
                                costCenterCode=request.POST.get("budget_sc")).costCenterName,
                            fieldID='cost_description_input', formID=old_emp_info_form.formID)
                    # endregion

                    # region Section 2
                    if str(request.POST.get("travel_datefrom")) != str(old_travel_detail_form.startDate):
                        ModifiedFields().modify_fields(fieldData=request.POST.get("travel_datefrom"),
                                                       fieldID='travel_datefrom', formID=old_emp_info_form.formID)

                    if str(request.POST.get("travel_dateto")) != str(old_travel_detail_form.endDate):
                        ModifiedFields().modify_fields(fieldData=request.POST.get("travel_dateto"),
                                                       fieldID='travel_dateto', formID=old_emp_info_form.formID)

                    if int(request.POST.get("estimated_period")) != int(old_travel_detail_form.estimatedDuration):
                        ModifiedFields().modify_fields(fieldData=request.POST.get("estimated_period"),
                                                       fieldID='estimated_period', formID=old_emp_info_form.formID)

                    if request.POST.get("departure_country") != old_travel_detail_form.departureCountry:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("departure_country"),
                                                       fieldID='departure_country', formID=old_emp_info_form.formID)

                    if request.POST.get("factory_code") != old_travel_detail_form.departureFactoryCode:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("factory_code"),
                                                       fieldID='factory_code', formID=old_emp_info_form.formID)

                    if request.POST.get("country2") != old_travel_detail_form.destinationCountry:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("country2"),
                                                       fieldID='country2', formID=old_emp_info_form.formID)

                    if request.POST.get("departure_state") != old_travel_detail_form.departurePreferred:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("departure_state"),
                                                       fieldID='departure_state', formID=old_emp_info_form.formID)

                    if request.POST.get("state2") != old_travel_detail_form.destinationProvince:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("state2"),
                                                       fieldID='state2', formID=old_emp_info_form.formID)

                    if request.POST.get("destination_city") != old_travel_detail_form.destinationCity:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("destination_city"),
                                                       fieldID='destination_city', formID=old_emp_info_form.formID)

                    if request.POST.get("transportation_type") != old_travel_detail_form.transportation:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("transportation_type"),
                                                       fieldID='transportation_type', formID=old_emp_info_form.formID)

                    if request.POST.get("accommodation_type") != old_travel_detail_form.accommodation:
                        ModifiedFields().modify_fields(fieldData=request.POST.get("accommodation_type"),
                                                       fieldID='accommodation_type',
                                                       formID=old_emp_info_form.formID)

                    if str(request.POST.get("date")) != str(old_travel_detail_form.date):
                        ModifiedFields().modify_fields(fieldData=request.POST.get("date"),
                                                       fieldID='date', formID=old_emp_info_form.formID)

                    if str(request.POST.get("country_currency")) != str(old_travel_detail_form.currency):
                        ModifiedFields().modify_fields(fieldData=request.POST.get("country_currency"),
                                                       fieldID='country_currency', formID=old_emp_info_form.formID)
                    currency = request.POST.get("country_currency")

                    # endregion

                    # region The Rows and Columns (wich is part of Section 2 but is so long it gets its own region apart from it)
                    detail_id = TravelDetail.objects.get(
                        detailID=old_travel_detail_form.detailID)  # TravelDetailCompany.detailID
                    visit_dates = all_post_data['visit_date']  # Get keys that contain this
                    visit_companies = all_post_data["visit_company"]
                    visit_departments = all_post_data["visit_department"]
                    contacts = all_post_data["company_contact"]
                    objectives = all_post_data["visit_objective"]

                    try:
                        visit_ids = all_post_data["visit_id"]  # This field only exists on a saved form
                    except:
                        print('no old visit ids to attain')
                    index = 0
                    rows = 0

                    print("Visit Dates: " + str(visit_dates))

                    # Check to see if there are multiple rows:
                    if str(visit_dates) != '':
                        if ',' in str(visit_dates):
                            print('There are multiple rows')
                            there_are_multiple_rows = True

                        else:
                            print('there is only one row')
                            there_are_multiple_rows = False

                        if there_are_multiple_rows:
                            for row in visit_dates:
                                rows += 1
                            for row in visit_dates:
                                if index < rows:
                                    try:
                                        # Try will update an edited row. If there is no row to update...
                                        current = TravelDetailCompany.objects.get(visitID=visit_ids[index])
                                        current_found = True
                                    except:
                                        # ...it will throw an error which except will catch. Except will create a new row instead of updating an old one
                                        print('more feilds than last save for create detail company')
                                        current = []
                                        current_found = False

                                    # I have to get the hidden fields to determine which rows belong to what Travel Detail Company Object
                                    if current_found:

                                        if str(current.date) != str(row):
                                            ModifiedFields().modify_dynamic_fields(
                                                visitID=TravelDetailCompany.objects.get(visitID=visit_ids[index],
                                                                                        detailID=detail_id),
                                                fieldData=row,
                                                fieldID='visit_date',
                                                formID=old_emp_info_form.formID)

                                        if current.visitCompany != visit_companies[index]:
                                            ModifiedFields().modify_dynamic_fields(
                                                visitID=TravelDetailCompany.objects.get(visitID=visit_ids[index],
                                                                                        detailID=detail_id),
                                                fieldData=visit_companies[index],
                                                fieldID='visit_company',
                                                formID=old_emp_info_form.formID)

                                        if visit_departments[index] != current.department:
                                            ModifiedFields().modify_dynamic_fields(
                                                visitID=TravelDetailCompany.objects.get(visitID=visit_ids[index],
                                                                                        detailID=detail_id),
                                                fieldData=visit_departments[index],
                                                fieldID='visit_department',
                                                formID=old_emp_info_form.formID)

                                        if contacts[index] != current.contact:
                                            ModifiedFields().modify_dynamic_fields(
                                                visitID=TravelDetailCompany.objects.get(visitID=visit_ids[index],
                                                                                        detailID=detail_id),
                                                fieldData=contacts[index],
                                                fieldID='company_contact',
                                                formID=old_emp_info_form.formID)

                                        if objectives[index] != '' and objectives[
                                            index] != ' ' and current.preciseObjective is not None:
                                            if objectives[index] != current.preciseObjective:
                                                ModifiedFields().modify_dynamic_fields(
                                                    visitID=TravelDetailCompany.objects.get(visitID=visit_ids[index],
                                                                                            detailID=detail_id),
                                                    fieldData=objectives[index],
                                                    fieldID='visit_objective',
                                                    formID=old_emp_info_form.formID)
                                        index += 1
                                    else:
                                        # If current not found just create modified field objects
                                        new_modified_row = TravelDetailCompany()
                                        new_modified_row.save_detail_company(detailID=detail_id,
                                                                             date=visit_dates[index],
                                                                             contact=contacts[index],
                                                                             department=visit_departments[index],
                                                                             isCompleted=True,
                                                                             preciseObjective=objectives[index],
                                                                             visitCompany=visit_companies[index])
                                        new_modified_row.modifiedField = True
                                        new_modified_row.save()
                                        index += 1
                                else:
                                    break
                        # Delete rows that have been deleted in the javascript. Just set everything to blank.
                        try:
                            for form in old_company_forms:
                                if str(form.visitID) not in str(visit_ids) and form.visitID != visit_ids:
                                    ModifiedFields().modify_dynamic_fields(visitID=form.visitID, fieldData=None,
                                                                           fieldID='visit_date',
                                                                           formID=old_emp_info_form.formID)

                                    ModifiedFields().modify_dynamic_fields(visitID=form.visitID,
                                                                           fieldData=None,
                                                                           fieldID='visit_company',
                                                                           formID=old_emp_info_form.formID)

                                    ModifiedFields().modify_dynamic_fields(visitID=form.visitID,
                                                                           fieldData=None,
                                                                           fieldID='visit_department',
                                                                           formID=old_emp_info_form.formID)

                                    ModifiedFields().modify_dynamic_fields(visitID=form.visitID,
                                                                           fieldData=None,
                                                                           fieldID='company_contact',
                                                                           formID=old_emp_info_form.formID)

                                    ModifiedFields().modify_dynamic_fields(visitID=form.visitID,
                                                                           fieldData=None,
                                                                           fieldID='visit_objective',
                                                                           formID=old_emp_info_form.formID)
                        except:
                            print("No old forms to delete")

                        # If there is only one row:
                        if there_are_multiple_rows == False:
                            try:
                                # Try will update an edited row. If there is no row to update...
                                form_to_update = TravelDetailCompany.objects.get(visitID=old_company_forms[0].visitID)

                                if str(visit_dates[0]) != str(form_to_update.date):
                                    ModifiedFields().modify_dynamic_fields(visitID=form_to_update.visitID,
                                                                           fieldData=visit_dates,
                                                                           fieldID='visit_date',
                                                                           formID=old_emp_info_form.formID)

                                if visit_companies[0] != form_to_update.visitCompany:
                                    ModifiedFields().modify_dynamic_fields(visitID=form_to_update.visitID,
                                                                           fieldData=visit_companies,
                                                                           fieldID='visit_company',
                                                                           formID=old_emp_info_form.formID)

                                if visit_departments[0] != form_to_update.department:
                                    ModifiedFields().modify_dynamic_fields(visitID=form_to_update.visitID,
                                                                           fieldData=visit_departments,
                                                                           fieldID='visit_department',
                                                                           formID=old_emp_info_form.formID)

                                if contacts[0] != form_to_update.contact:
                                    ModifiedFields().modify_dynamic_fields(visitID=form_to_update.visitID,
                                                                           fieldData=contacts,
                                                                           fieldID='company_contact',
                                                                           formID=old_emp_info_form.formID)

                                if objectives[0] != form_to_update.preciseObjective:
                                    ModifiedFields().modify_dynamic_fields(visitID=form_to_update.visitID,
                                                                           fieldData=objectives,
                                                                           fieldID='visit_objective',
                                                                           formID=old_emp_info_form.formID)

                            except:
                                try:
                                    # ...it will throw an error which except will catch. Except will create a new row instead of updating an old one
                                    print("Creating new travel detail company")
                                    ModifiedFields().modify_fields(fieldData=visit_dates[0],
                                                                   fieldID='visit_date',
                                                                   formID=old_emp_info_form.formID)

                                    ModifiedFields().modify_fields(fieldData=visit_companies[0],
                                                                   fieldID='visit_company',
                                                                   formID=old_emp_info_form.formID)

                                    ModifiedFields().modify_fields(fieldData=visit_departments[0],
                                                                   fieldID='visit_department',
                                                                   formID=old_emp_info_form.formID)

                                    ModifiedFields().modify_fields(fieldData=contacts[0],
                                                                   fieldID='company_contact',
                                                                   formID=old_emp_info_form.formID)

                                    ModifiedFields().modify_fields(fieldData=objectives[0],
                                                                   fieldID='visit_objective',
                                                                   formID=old_emp_info_form.formID)
                                except:
                                    print("No travel detail Company information to save")
                    # endregion

                    # Section 3 - Zaawar Ejaz
                    # region Section 3
                    if float(request.POST.get('allowance')) != float(old_expense_form.allowance):
                        ModifiedFields().modify_fields(fieldData=request.POST.get('allowance'),
                                                       fieldID='allowance',
                                                       formID=old_emp_info_form.formID)

                    if request.POST.get('explanation_allowance') != old_expense_form.allowanceExp:
                        ModifiedFields().modify_fields(fieldData=request.POST.get('explanation_allowance'),
                                                       fieldID='explanation_allowance',
                                                       formID=old_emp_info_form.formID)

                    if float(request.POST.get('accommodation')) != float(old_expense_form.accommodation):
                        ModifiedFields().modify_fields(fieldData=request.POST.get('accommodation'),
                                                       fieldID='accommodation',
                                                       formID=old_emp_info_form.formID)

                    # if float(request.POST.get('explaination_accommodation')) != float(
                    #         old_expense_form.accommodationExp):
                    #     ModifiedFields().modify_fields(fieldData=request.POST.get('explaination_accommodation'),
                    #                                    fieldID='explaination_accommodation',
                    #                                    formID=old_emp_info_form.formID)

                    if float(request.POST.get('transportation')) != float(old_expense_form.transportation):
                        ModifiedFields().modify_fields(fieldData=request.POST.get('transportation'),
                                                       fieldID='transportation',
                                                       formID=old_emp_info_form.formID)

                    if request.POST.get('explaination_transportation') != old_expense_form.transportationExp:
                        ModifiedFields().modify_fields(fieldData=request.POST.get('explaination_transportation'),
                                                       fieldID='explaination_transportation',
                                                       formID=old_emp_info_form.formID)

                    if request.POST.get('public_relationship') != old_expense_form.publicRelationship:
                        ModifiedFields().modify_fields(fieldData=request.POST.get('public_relationship'),
                                                       fieldID='public_relationship',
                                                       formID=old_emp_info_form.formID)

                    if request.POST.get('explanation_publicrelationship') != old_expense_form.publicRelationshipExp:
                        ModifiedFields().modify_fields(fieldData=request.POST.get('explanation_publicrelationship'),
                                                       fieldID='explanation_publicrelationship',
                                                       formID=old_emp_info_form.formID)

                    if request.POST.get('visa') != old_expense_form.visaExp:
                        ModifiedFields().modify_fields(fieldData=request.POST.get('visa'),
                                                       fieldID='visa',
                                                       formID=old_emp_info_form.formID)

                    if request.POST.get('explaination_visa') != old_expense_form.visa:
                        ModifiedFields().modify_fields(fieldData=request.POST.get('explaination_visa'),
                                                       fieldID='explaination_visa',
                                                       formID=old_emp_info_form.formID)

                    if float(request.POST.get('airway_ticket')) != float(old_expense_form.airwayTicket):
                        ModifiedFields().modify_fields(fieldData=request.POST.get('airway_ticket'),
                                                       fieldID='airway_ticket',
                                                       formID=old_emp_info_form.formID)

                    if request.POST.get('explaination_airwayticket') != old_expense_form.airwayTicketExp:
                        ModifiedFields().modify_fields(fieldData=request.POST.get('explaination_airwayticket'),
                                                       fieldID='explaination_airwayticket',
                                                       formID=old_emp_info_form.formID)

                    # if float(request.POST.get('insurance')) != float(old_expense_form.insurance):
                    #     ModifiedFields().modify_fields(fieldData=request.POST.get('insurance'), fieldID='insurance',
                    #                                    formID=old_emp_info_form.formID)
                    #
                    # if request.POST.get('explaination_insurance') != old_expense_form.insuranceExp:
                    #     ModifiedFields().modify_fields(fieldData=request.POST.get('explaination_insurance'),
                    #                                    fieldID='explaination_insurance',
                    #                                    formID=old_emp_info_form.formID)

                    if float(request.POST.get('other_expense')) != float(old_expense_form.other):
                        ModifiedFields().modify_fields(fieldData=request.POST.get('other_expense'),
                                                       fieldID='other_expense', formID=old_emp_info_form.formID)

                    if request.POST.get('explaination_otherexpense') != old_expense_form.otherExp:
                        ModifiedFields().modify_fields(fieldData=request.POST.get('explaination_otherexpense'),
                                                       fieldID='explaination_otherexpense',
                                                       formID=old_emp_info_form.formID)

                    print("***TOTAL: " + str(float(request.POST.get('total'))))
                    print("Old Total: " + str(float(old_expense_form.total)))
                    if float(request.POST.get('total')) != float(old_expense_form.total):
                        ModifiedFields().modify_fields(fieldData=request.POST.get('total'),
                                                       fieldID='total', formID=old_emp_info_form.formID)

                    print("\nThis is the line before getting travel_advance_button value\n")

                    if old_advance_form is not None:
                        if old_advance_form.advAmount is not None and old_advance_form.advAmount != 0 and old_advance_form.advAmount != '':
                            try:
                                if float(request.POST.get('advance_amount')) != float(old_advance_form.advAmount):
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('advance_amount'),
                                                                   fieldID='advance_amount',
                                                                   formID=old_emp_info_form.formID)
                            except:
                                print("no old advance form")

                            if request.POST.get('advance_amount') is not None and request.POST.get(
                                    'advance_amount') != 0 and request.POST.get('advance_amount') != '' and \
                                    request.session[
                                        'department'] == 'Supporting - Accounting':
                                vendor_code = request.POST.get("vendor_code")
                                if len(vendor_code) > 15:
                                    error_messages['fatal_errors'] = "Error saving form. Vendor Code can only be up to 15 characters."
                                    response_data['result'] = error_messages
                                    return HttpResponse(
                                        json.dumps(response_data),
                                        content_type="application/json"
                                    )
                                try:
                                    old_advance_form.save_adv_app(formID=old_emp_info_form,
                                                                  advAmount=old_advance_form.advAmount,
                                                                  glAccount=request.POST.get('gl_account'),
                                                                  glDescription=request.POST.get('gl_description'),
                                                                  costCenterCode=request.POST.get('cost_center'),
                                                                  profitCenter=request.POST.get(
                                                                      'advanceprofit_center'),
                                                                  headText=request.POST.get('head_text'),
                                                                  text=request.POST.get('text'),
                                                                  assignment=request.POST.get('assignment'),
                                                                  isCompleted=True,
                                                                  refDocument=request.POST.get('reference_document'),
                                                                  dateApplied=datetime.now(),
                                                                  vendorCode=vendor_code,
                                                                  currency=currency)
                                except:
                                    print('No old advance form to update')
                                    print('it knows to try to save Travel Advance')
                                    if request.POST.get('gl_account') != '':
                                        ModifiedFields().modify_fields(fieldData=request.POST.get('gl_account'),
                                                                       fieldID='gl_account',
                                                                       formID=old_emp_info_form.formID)

                                    if request.POST.get('gl_description') != '':
                                        ModifiedFields().modify_fields(fieldData=request.POST.get('gl_description'),
                                                                       fieldID='gl_description',
                                                                       formID=old_emp_info_form.formID)

                                    if request.POST.get('cost_center') != old_advance_form.costCenterCode:
                                        ModifiedFields().modify_fields(fieldData=request.POST.get('cost_center'),
                                                                       fieldID='cost_center',
                                                                       formID=old_emp_info_form.formID)

                                    # if request.POST.get('memo') != '':
                                    #     ModifiedFields().modify_fields(fieldData=request.POST.get('memo'),
                                    #                                    fieldID='memo', formID=old_emp_info_form.formID)

                                    if request.POST.get('head_text') != old_advance_form.headText:
                                        ModifiedFields().modify_fields(fieldData=request.POST.get('head_text'),
                                                                       fieldID='head_text',
                                                                       formID=old_emp_info_form.formID)

                                    if request.POST.get('text') != old_advance_form.text:
                                        ModifiedFields().modify_fields(fieldData=request.POST.get('text'),
                                                                       fieldID='text', formID=old_emp_info_form.formID)

                                    if request.POST.get('assignment') != old_advance_form.assignment:
                                        ModifiedFields().modify_fields(fieldData=request.POST.get('assignment'),
                                                                       fieldID='assignment',
                                                                       formID=old_emp_info_form.formID)

                                    if request.POST.get('reference_document') != old_advance_form.refDocument:
                                        ModifiedFields().modify_fields(fieldData=request.POST.get('reference_document'),
                                                                       fieldID='reference_document',
                                                                       formID=old_emp_info_form.formID)
                            else:
                                print('it knows to try to save Travel Advance')
                                gl_account = convert_to_null_if_empty(request.POST.get('gl_account'))
                                if gl_account != old_advance_form.glAccount:
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('gl_account'),
                                                                   fieldID='gl_account',
                                                                   formID=old_emp_info_form.formID)

                                gl_description = convert_to_null_if_empty(request.POST.get('gl_description'))
                                if gl_description != old_advance_form.glDescription:
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('gl_description'),
                                                                   fieldID='gl_description',
                                                                   formID=old_emp_info_form.formID)

                                cost_center = convert_to_null_if_empty(request.POST.get('cost_center'))
                                if cost_center != old_advance_form.costCenterCode:
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('cost_center'),
                                                                   fieldID='cost_center',
                                                                   formID=old_emp_info_form.formID)

                                adv_profit = convert_to_null_if_empty(request.POST.get('advanceadvanceprofit_center'))
                                if adv_profit != old_advance_form.profitCenter:
                                    ModifiedFields().modify_fields(
                                        fieldData=request.POST.get('advanceadvanceprofit_center'),
                                        fieldID='advanceadvanceprofit_center',
                                        formID=old_emp_info_form.formID)

                                # memo = convert_to_null_if_empty(request.POST.get('memo'))
                                # if memo != old_advance_form.memo:
                                #     ModifiedFields().modify_fields(fieldData=request.POST.get('memo'),
                                #                                    fieldID='memo', formID=old_emp_info_form.formID)

                                head_text = convert_to_null_if_empty(request.POST.get('head_text'))
                                if head_text != old_advance_form.headText:
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('head_text'),
                                                                   fieldID='head_text', formID=old_emp_info_form.formID)

                                text = convert_to_null_if_empty(request.POST.get('text'))
                                if text != old_advance_form.text:
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('text'),
                                                                   fieldID='text', formID=old_emp_info_form.formID)

                                assignment = convert_to_null_if_empty(request.POST.get('assignment'))
                                if assignment != old_advance_form.assignment:
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('assignment'),
                                                                   fieldID='assignment',
                                                                   formID=old_emp_info_form.formID)

                                reference_doc = convert_to_null_if_empty(request.POST.get('reference_doc'))
                                if reference_doc != old_advance_form.refDocument:
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('reference_document'),
                                                                   fieldID='reference_document',
                                                                   formID=old_emp_info_form.formID)

                                currency = request.POST.get("country_currency")
                                if currency != old_advance_form.currency:
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('country_currency'),
                                                                   fieldID='country_currency',
                                                                   formID=old_emp_info_form.formID)
                                vendor_code = request.POST.get("vendor_code")
                                if vendor_code != old_advance_form.currency:
                                    ModifiedFields().modify_fields(fieldData=request.POST.get('vendor_code'),
                                                                   fieldID='vendor_code',
                                                                   formID=old_emp_info_form.formID)
                        else:
                            try:
                                if old_advance_form.advAmount is not None and (request.POST.get(
                                        'advance_amount') == '0.00' or request.POST.get('advance_amount') == ''):
                                    ModifiedFields().modify_fields(fieldData=None,
                                                                   fieldID='advance_amount',
                                                                   formID=old_emp_info_form.formID)
                            except:
                                print("no old advance form to delete")
                    # endregion
                    # endregion
                    error_messages = merge_dictionaries(error_messages, update_stages_for_modification_request(request=request,
                                                           form=old_emp_info_form,
                                                           approval_process_type=TemporaryApprovalStage))
                    response_data['result'] = error_messages
                    if error_messages['fatal_errors'] == "":
                        messages.success(request, "Modification request successfully sent!")
                    print("modification sent!!!")
                    for error in error_messages['other_errors']:
                        messages.error(request, error)
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                if request.POST.get('submit_button') == 'Change Approver List':
                    if request.POST.get('add_approver_action') == 'Add to approval list':
                        new_approvers = []
                        for approver_pk in all_post_data['add_approvers_options']:
                            new_approvers.append(Employee.objects.get(pk=approver_pk))
                            error_messages = merge_dictionaries(error_messages, add_approver(form=old_emp_info_form,
                                         new_approvers=new_approvers,
                                         stage=old_emp_info_form.currentStage,
                                         approval_process_type=TemporaryApprovalStage, request=request))
                        response_data['fatal_errors'] = error_messages
                        if error_messages['fatal_errors'] == "":
                            messages.success(request, "List of approvers successfully modified!")

                    elif request.POST.get('add_approver_action') == 'Replace me in approval list':
                        error_messages = merge_dictionaries(error_messages, replace_approver(form=old_emp_info_form,
                                         stage=old_emp_info_form.currentStage,
                                         new_approver=Employee.objects.get(
                                             associateID=request.POST.get('add_approvers_options')),
                                         old_approver=Employee.objects.get(pk=request.session['user_id']),
                                         approval_process_type=TemporaryApprovalStage, request=request))
                        response_data['fatal_errors'] = error_messages
                        if error_messages['fatal_errors'] == "":
                            messages.success(request, "List of approvers successfully modified!")

                    response_data['result'] = error_messages
                    for error in error_messages['other_errors']:
                        messages.error(request, error)
                    return HttpResponse(
                            json.dumps(response_data),
                            content_type="application/json"
                        )
                else:
                    print("user is creator: " + str(user_is_creator))
                    print("form is totally approved: " + str(form_is_completely_approved))
                    print("**********THING: " + str(old_travel_detail_form.departureFactoryCode))
                    print("all stages: " + str(all_forms_stages))
                    return render(request, "travel/index.html", {"form_id": pk,
                                                                 "show_chat": True,
                                                                 "approving_modifications": approving_modifications,
                                                                 "employee_list": employee_list,
                                                                 "stages_already_finished": stages_already_finished,
                                                                 "form_is_being_approved": form_is_being_approved,
                                                                 "form_is_being_shown_to_approver": form_is_being_shown_to_approver,
                                                                 "approver_name": request.session['full_name'],
                                                                 "full_name": user_fullname,
                                                                 "business_unit": user_business_unit,
                                                                 "business_units": BusinessUnit.objects.all(),
                                                                 "user_dept": request.session['department'],
                                                                 "business_unit_code": user_business_unit_code,
                                                                 "departments": departments,
                                                                 "business_groups": business_groups,
                                                                 'companies': companies,
                                                                 'old_emp_form': old_emp_info_form,
                                                                 'old_company_forms': old_company_forms,
                                                                 'old_detail_form': old_travel_detail_form,
                                                                 'old_expense_form': old_expense_form,
                                                                 'old_advance_form': old_advance_form,
                                                                 'there_are_multiple_old_company_forms': there_are_multiple_old_company_forms,
                                                                 "factory_codes": factory_codes,
                                                                 "users_building": users_factory,
                                                                 "employees_for_add_new_approver": employees_for_add_new_approver,
                                                                 "modified_fields": modified_fields,
                                                                 "today": datetime.now(),
                                                                 "users_stage": users_stage,
                                                                 'form_is_declined': form_is_declined,
                                                                 "employee_country": employee_country,
                                                                 "current_date": datetime.today(),
                                                                 "form_is_completely_approved": form_is_completely_approved,
                                                                 "user_is_creator": user_is_creator,
                                                                 "vendor": vendor,
                                                                 "emp": Employee.objects.get(
                                                                     associateID=request.session['user_id']),
                                                                 "employee_business_group": employee_business_group,
                                                                 "employee_company": employee_company,
                                                                 "all_forms_stages": all_forms_stages
                                                             })
            else:
                return HttpResponse("You are not allowed to view this page.")
    else:
        return redirect('../../../accounts/login/?next=/forms/travel_application/' + str(pk) + '/')


# endregion


'''
This view shows TA forms that belong to the user.
Author: Corrina Barr
:param request: the webpage request
:return: redirects to login if user is not logged in. 
         otherwise shows section one page
         if method is post, it sends data to database and returns to Smart Office Home Page
'''


def submitted_forms_view(request):
    if request.user.is_authenticated:
        set_session(request)
        return render(request, 'travel/submitted_forms.html', {})
    else:
        return redirect('../../accounts/login/?next=/forms/submitted_forms/')


'''
This view shows TR forms that belong to the user.
Author: Corrina Barr
:param request: the webpage request
:return: redirects to login if user is not logged in. 
         otherwise shows section one page
         if method is post, it sends data to database and returns to Smart Office Home Page
'''
def my_TR_forms_view(request):
    if request.user.is_authenticated:
        set_session(request)
        return render(request, 'travel/submitted_tr_forms.html', {})
    else:
        return redirect('../../accounts/login/?next=/forms/my_travel_rem/')


'''
This view shows TR forms that user will approve
Author: Corrina Barr
:param request: the webpage request
:return: redirects to login if user is not logged in. 
         otherwise shows section one page
         if method is post, it sends data to database and returns to Smart Office Home Page
'''
def travel_rem_list(request):
    if request.user.is_authenticated:
        set_session(request)
        return render(request, 'travel/tr_forms_to_approve.html', {})
    else:
        return redirect('../../accounts/login/?next=/forms/travel_rem_list/')


# region Travel Reimbursement
'''
This view shows the travel reimbursement page.
Author: Corrina Barr
:param request: the webpage request
:return: redirects to login if user is not logged in. 
         otherwise shows travel_reimbursement
         if method is post, it sends data to database and returns to Smart Office Home Page
'''
def travel_reimbursement_view(request, pk):
    if request.user.is_authenticated:
        # Validation check:
        error_messages = {'fatal_errors': '', 'other_errors': []}
        set_session(request)
        if request.session['department'] == '':
            return HttpResponse("You are not allowed to view this page")

        form_is_declined = False

        # Get list of GL accounts:
        try:
            gl_accounts = GLAccount.objects.all()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving GL Account Data. Contact IT if this problem persists.<br>"
                                "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

        # Get Travel App from the pk:
        try:
            the_travel_app = EmployeeInformation.objects.get(formID=pk)
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving Travel Application Data. Contact IT if this problem persists.<br>"
                                "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

        # Check if user is creator:
        try:
            if the_travel_app.employee.pk == request.session['id']:
                user_is_creator = True
            else:
                user_is_creator = False
        except:
            user_is_creator = False


        # Get Travel App End Date:
        try:
            travel_app_end = TravelDetail.objects.get(formID=the_travel_app).endDate
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving Travel Application Data. Contact IT if this problem persists.<br>"
                                "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

        # Get cost center description:
        try:
            cost_center_desc = CostCenter.objects.get(costCenterCode=the_travel_app.budgetSourceCode).costCenterName
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving Cost Center Data. Contact IT if this problem persists.<br>"
                                "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

        # Get Travel Advance from the pk:
        the_travel_advance = AdvanceTravelApp.objects.filter(formID=the_travel_app).first()
        SAP_travel = None
        SAP_adv = None
        if the_travel_advance:
            try:
                SAP_adv = SAPAdvApp.objects.filter(formID=the_travel_app).first()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                return HttpResponse("Error retrieving Travel Application Data. Contact IT if this problem persists.<br>"
                                    "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")
            try:
                SAP_travel = SAPTravelApp.objects.filter(formID=the_travel_app).first()
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                return HttpResponse("Error retrieving Travel Application Data. Contact IT if this problem persists.<br>"
                                    "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

        # Get how much spent on perdiem:
        try:
            perdiem_amount_chosen = TravelDetailExpenses.objects.get(detailID__formID=the_travel_app).allowance
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse("Error retrieving Perdiem data. Contact IT if this problem persists.<br>"
                                "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")
        business_docs = ''
        personal_docs = ''
        payment_docs = ''
        mileage_docs = ''

        # Get TRFileUpload from the pk:
        the_files = TRFilesLink.objects.filter(form=the_travel_app).first()
        try:
            if the_files is None:
                the_files = TRFilesLink()
                the_files.form = the_travel_app
                the_files.save()
            else:
                # Get all different files:
                business_docs = the_files.get_files_in_folder('business-expenses')
                if str(business_docs) == "<QuerySet []>":
                    business_docs = ''
                personal_docs = the_files.get_files_in_folder('personal-expenses')
                if str(personal_docs) == "<QuerySet []>":
                    personal_docs = ''
                payment_docs = the_files.get_files_in_folder('proof-of-payment')
                if str(payment_docs) == "<QuerySet []>":
                    payment_docs = ''
                mileage_docs = the_files.get_files_in_folder('mileage-expenses')
                if str(mileage_docs) == "<QuerySet []>":
                    mileage_docs = ''
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return messages.error(request, "Error retrieving uploaded file data. Contact IT if this problem persists")

        # Check if reimbursement is not valid:
        if the_travel_app is None:
            return HttpResponse("This Travel Reimbursement form does not exist")
        else:
            if the_travel_app.isApproved == False:
                return HttpResponse("This Travel Reimbursement form does not exist")

        # Get Reimbursement from the pk:
        this_travel_rem = TADetails.objects.filter(taDetail=the_travel_app).first()  # This could be nothing.
        if this_travel_rem:
            if user_is_creator == False and this_travel_rem.isCompleted == False:
                return HttpResponse("You are not authorized to view this form")
            users_approval_stage = TRApprovalProcess.objects.filter(approverID__associateID=request.session['user_id'],
                                                                    formID=this_travel_rem).first()
            # Get modified fields:
            modified_fields = TRModifiedFields.objects.filter(formID=this_travel_rem.formID)
        else:
            if user_is_creator == False:
                return HttpResponse("You are not authorized to view this form")
            modified_fields = []
            users_approval_stage = None



        # Get TR Advance
        try:
            the_tr_advance = None
            the_tr_advances = AdvanceReimbursementApp.objects.filter(form=this_travel_rem)
            for adv in the_tr_advances:
                if adv.vendorCode != None and adv.advAmount > 0:
                    the_tr_advance = adv
            if the_tr_advance == None:
                the_tr_advance = the_tr_advances.first()
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            the_tr_advance = None
            the_tr_advances = None

        if this_travel_rem:
            # Get gl acount data
            gls_chosen = TRGLAccount.objects.filter(trForm=this_travel_rem)
        else:
            gls_chosen = None

        form_is_being_approved = False
        approving_modifications = False
        form_is_being_shown_to_approver = False
        employees_for_add_new_approver = []
        accountant_list = []
        already_approvers = []
        all_forms_stages = []

        try:
            if (the_travel_app.employee.associateID == request.session['user_id']):
                user_is_creator_of_form = True
            else:
                user_is_creator_of_form = False
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            return HttpResponse(
                "Error retrieving data on the creator of the form. Contact IT if this problem persists.<br>"
                "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

        if this_travel_rem:
            if this_travel_rem.currentStage != 0 and this_travel_rem.isCompleted != False:
                try:
                    if (users_approval_stage != None or the_travel_app.employee.associateID == request.session['user_id']) and this_travel_rem.isCompleted == True:
                        form_is_being_shown_to_approver = True
                    else:
                        form_is_being_shown_to_approver = False
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    return HttpResponse("Error retrieving approval stage data. Contact IT if this problem persists.<br>"
                                        "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

                form_is_being_approved = False
                approving_modifications = False

                if form_is_being_shown_to_approver:
                    try:
                        if users_approval_stage:
                            if users_approval_stage.stage == this_travel_rem.currentStage and this_travel_rem.isApproved == False:
                                form_is_being_approved = True
                                # check all stages for next stage and see if any of them have Requested Modifications for their action
                                above_stages = TRApprovalProcess.objects.filter(formID=this_travel_rem,
                                                                                     stage=(this_travel_rem.currentStage - 1))
                                modification_request_was_sent = False
                                for stage in above_stages:
                                    if stage.actionTaken == 'Modified':
                                        modification_request_was_sent = True
                                if user_is_creator_of_form and modification_request_was_sent:
                                    approving_modifications = True
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        return HttpResponse(
                            "Error retrieving data on approval process for form. Contact IT if this problem persists.<br>"
                            "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

                if form_is_being_shown_to_approver == False:
                    return HttpResponse("You are not allowed to view this page")

            employees_for_add_new_approver = []
            accountant_list = []
            already_approvers = [the_travel_app.employee]

            all_forms_stages = TRApprovalProcess.objects.filter(formID=this_travel_rem).order_by('stage')
            for stage in all_forms_stages:
                already_approvers.append(stage.approverID)

            try:
                for unit in BusinessUnit.objects.all():
                    if unit.managedBy not in already_approvers and unit.managedBy not in employees_for_add_new_approver:
                        employees_for_add_new_approver.append(unit.managedBy)
                    if unit.costManager not in already_approvers and unit.managedBy not in employees_for_add_new_approver:
                        employees_for_add_new_approver.append(unit.costManager)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                return HttpResponse("Error retrieving business unit data. Contact IT if this problem persists.<br>"
                                    "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

            try:
                for dept in CostCenter.objects.all():
                    if dept.managedBy not in already_approvers and dept.managedBy not in employees_for_add_new_approver:
                        employees_for_add_new_approver.append(dept.managedBy)
                accountants = EmployeeDepartment.objects.filter(
                    departmentID=CostCenter.objects.get(costCenterName='Supporting - Accounting'))
                for accountant in accountants:
                    if accountant.associateID not in already_approvers and accountant.associateID not in employees_for_add_new_approver:
                        employees_for_add_new_approver.append(accountant.associateID)
                    if accountant.associateID not in accountant_list:
                        accountant_list.append(accountant.associateID)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                return HttpResponse("Error retrieving data about accountants. Contact IT if this problem persists.<br>"
                                    "<a href='{%url 'smart_office_dashboard'%}'>Home</a>")

            # Check to see if the form has been declined or not
            try:
                form_is_declined = this_travel_rem.isDeclined
            except:
                form_is_declined = False

        days_of_the_week = [0, 1, 2, 3, 4, 5, 6]

        if this_travel_rem:
            this_travel_weeks = TRWeek.objects.filter(formID=this_travel_rem)
            this_travel_days = TRDay.objects.filter(weekID__formID=this_travel_rem)
            this_travel_emp_expenses = EmployeeExpenses.objects.filter(dayID__weekID__formID=this_travel_rem)
            this_travel_explanations = BusinessExpenseExplanation.objects.filter(dayID__weekID__formID=this_travel_rem)
            this_travel_exps_charged = ExpendituresCharged.objects.filter(dayID__weekID__formID=this_travel_rem)
            this_travel_mileages = DailyMileage.objects.filter(dayID__weekID__formID=this_travel_rem)
            travel_mileage_weeks = []
            counter = -1

            if this_travel_explanations:
                print("travel explanations: " + str(this_travel_explanations))
            else:
                this_travel_explanations = None

            for milage in this_travel_mileages:
                try:
                    supporting_document_name = \
                        str(milage.mileage.supportingDoc).split("media/travel/mileage_expenses/", 1)[1]
                except:
                    supporting_document_name = None
                # loop through each mileage week and see if [0] == mileage.dayID.weekID
                try:
                    week_exists = False
                    for m in travel_mileage_weeks:
                        if m[0] == milage.dayID.weekID:
                            week_exists = True
                    if week_exists == False:
                        counter += 1
                        if milage.dayID.weekID.startDate != None:
                            travel_mileage_weeks.append(
                                [milage.dayID.weekID, milage.mileage.supportingDoc, supporting_document_name, counter])
                            # this_travel_mileage_weeks:
                            #   for each week in the list:
                            #   [0] = weekID
                            #   [1] = supportingDoc
                            #   [2] = supporting document name
                            #   [3] = index of week in the list (row number)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    messages.error(request, "Error retrieving mileage data. Contact IT if this problem persists.")
            if travel_mileage_weeks == []:
                travel_mileage_weeks = None

        else:
            this_travel_weeks = None
            this_travel_days = None
            this_travel_emp_expenses = None
            this_travel_explanations = None
            this_travel_expense_type_ids = None
            this_travel_item_type_ids = None
            this_travel_mileages = None
            this_travel_exps_charged = None
            travel_mileage_weeks = None
            # supporting_document = None
            # supporting_document_name = None

        # print("Forms TA Details: " + str(this_travel_rem))
        # print("Travel App: " + str(the_travel_app))
        # print("FINAL TA Weeks: " + str(this_travel_weeks))
        # print("FINAL TR Days: " + str(this_travel_days))
        # print("Employee Expenses: " + str(this_travel_emp_expenses))
        print("BEE Explanations: " + str(this_travel_explanations))
        # print("Type List: " + str(this_travel_expense_type_ids))
        # print("Item List: " + str(this_travel_item_type_ids))
        # print("FINAL Mileages: " + str(this_travel_mileages))
        # print("Expendatures Charged: " + str(this_travel_exps_charged))
        # print("Travel Advance: " + str(the_travel_advance))
        # print("Mileage Weeks: " + str(travel_mileage_weeks))

        # region Formatting EmployeeExpense objects and Expenditures so that they can be looped through in the view

        sorted_personal_meals = []
        sorted_hotels = []
        sorted_transportations = []
        sorted_business_meals = []
        sorted_others = []
        sorted_expenditures = []
        sorted_personal_meal_perdiems = []

        personal_meal_names = ['personal_breakfast', 'personal_lunch', 'personal_dinner']
        hotel_names = ['hotel_room_change', 'hotel_laundry', 'hotel_telephone', 'hotel_others']
        transportation_names = ['parking', 'tolls', 'rides', 'transportation_others']
        business_meal_names = ['business_breakfast', 'business_lunch', 'business_dinner']
        other_names = ['others_telephone', 'others_gift', 'others_misc']

        p_meal_weeks = []
        hotel_weeks = []
        transportation_weeks = []
        b_meal_weeks = []
        other_weeks = []
        expenditure_weeks = []

        mileages_with_numbers = []
        if this_travel_mileages != None:
            try:
                for mileage in this_travel_mileages:
                    if mileage is not None:
                        if mileage.dayID.date is not None:
                            mileage_date = mileage.dayID.date.weekday()
                            mileages_with_numbers.append({'day': mileage_date, 'mileage': mileage})
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                messages.error(request, "Error retrieving mileage data. Contact IT if this problem persists.")

        # Convert gs_chosen to be understood better
        if gls_chosen:
            gls_chosen = convert_gl_dictionary(gls_chosen)

        if this_travel_emp_expenses is not None:
            for expense in this_travel_emp_expenses:
                try:
                    field_name_with_number = expense.fieldName
                    field_name_without_number = field_name_with_number.split('-')[0]
                    row_number = field_name_with_number.split("-", 1)[1]
                    go_on = True

                    # print("\nField name with number: " + str(field_name_with_number))
                    # print("Field name without number: " + str(field_name_without_number))

                    # Personal Meal:
                    if field_name_without_number in personal_meal_names:
                        try:
                            expense_week = expense.dayID.weekID
                        except:
                            expense.delete()
                            go_on = False
                        if go_on:
                            sorted_personal_meals = update_section_list(sorted_personal_meals, row_number,
                                                                        field_name_without_number, expense)
                            if expense_week not in p_meal_weeks:
                                p_meal_weeks.append(expense_week)
                    # Hotel Expense:
                    elif field_name_without_number in hotel_names:
                        try:
                            expense_week = expense.dayID.weekID
                        except:
                            expense.delete()
                            go_on = False
                        if go_on:
                            sorted_hotels = update_section_list(sorted_hotels, row_number, field_name_without_number,
                                                                expense)
                            if expense_week not in hotel_weeks:
                                hotel_weeks.append(expense_week)
                    # Transportation Expense:
                    elif field_name_without_number in transportation_names:
                        try:
                            expense_week = expense.dayID.weekID
                        except:
                            expense.delete()
                            go_on = False
                        if go_on:
                            sorted_transportations = update_section_list(sorted_transportations, row_number,
                                                                         field_name_without_number, expense)
                            if expense_week not in transportation_weeks:
                                transportation_weeks.append(expense_week)
                    # Business Meal:
                    elif field_name_without_number in business_meal_names:
                        try:
                            expense_week = expense.dayID.weekID
                        except:
                            expense.delete()
                            go_on = False
                        if go_on:
                            sorted_business_meals = update_section_list(sorted_business_meals, row_number,
                                                                        field_name_without_number, expense)
                            if expense_week not in b_meal_weeks:
                                b_meal_weeks.append(expense_week)
                    # Other Expenses:
                    elif field_name_without_number in other_names:
                        try:
                            expense_week = expense.dayID.weekID
                        except:
                            expense.delete()
                            go_on = False
                        if go_on:
                            sorted_others = update_section_list(sorted_others, row_number, field_name_without_number,
                                                                expense)
                            if expense_week not in other_weeks:
                                other_weeks.append(expense_week)
                    # Perdiems:
                    elif field_name_without_number == "personal_meal_perdiem":
                        try:
                            expense_week = expense.dayID.weekID
                        except:
                            expense.delete()
                            go_on = False
                        if go_on:
                            sorted_personal_meal_perdiems = update_section_list(sorted_personal_meal_perdiems,
                                                                                row_number,
                                                                                field_name_without_number, expense)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    return HttpResponse("Error formatting saved data. Contact IT if this problem persists.<br>"
                                        "<a href='{% url 'smart_office_dashboard' %}'>Home</a>")
        # print("Sorted other expenses: " + str(sorted_others))

        # Expenditures:
        if this_travel_exps_charged is not None:
            for expenditure in this_travel_exps_charged:
                try:
                    field_name_with_number = expenditure.fieldName
                    field_name_without_number = field_name_with_number.split('-')[0]
                    row_number = field_name_with_number.split("-", 1)[1]

                    try:
                        expenditure_week = expenditure.dayID.weekID
                        go_on = True
                    except:
                        go_on = False
                        expenditure.delete()
                    if go_on:
                        sorted_expenditures = update_section_list_expenditure(sorted_expenditures, row_number,
                                                                              field_name_without_number, expenditure)
                        if expenditure_week not in expenditure_weeks:
                            expenditure_weeks.append(expenditure_week)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    return HttpResponse("Error formatting saved data. Contact IT if this problem persists.<br>"
                                        "<a href='{% url 'smart_office_dashboard' %}'>Home</a>")

        if p_meal_weeks == []:
            p_meal_weeks = None
        if hotel_weeks == []:
            hotel_weeks = None
        if transportation_weeks == []:
            transportation_weeks = None
        if b_meal_weeks == []:
            b_meal_weeks = None
        if other_weeks == []:
            other_weeks = None
        if expenditure_weeks == []:
            expenditure_weeks = None

        # print("Hotel weeks: " + str(hotel_weeks))
        # print("Transportation weeks: " + str(transportation_weeks))
        # print("Sorted Transportation: " + str(sorted_transportations))
        # print("Business meal weeks: " + str(b_meal_weeks))
        # print("Other weeks: " + str(other_weeks))
        # print("Expenditure weeks: " + str(expenditure_weeks))
        # print("Personal meal weeks: " + str(p_meal_weeks))
        # print("Other Expenses: " + str(sorted_others))
        # print("Personal Expenses: " + str(sorted_personal_meals))
        # print("Sorted Expenditures: " + str(sorted_expenditures))
        # print("p meal deims: " + str(sorted_personal_meal_perdiems))
        # print("b meal diems: " + str(sorted_business_meal_perdiems))
        # print("other diems: " + str(sorted_other_perdiems))
        # endregion

        if request.method == 'POST':
            response_data = {}
            response_data['result'] = ""
            if user_is_creator_of_form:
                response_data['dir_to_dash'] = "../../my_travel_rem/"
            else:
                response_data['dir_to_dash'] = "../../travel_rem_list/"
            # print("request.POST: " + str(request.POST))
            # all_post_data = dict(request.POST)
            # print("\nAll Post Data: " + str(all_post_data))
            # return JsonResponse(request.POST)

            print(request)
            error_messages = merge_dictionaries(error_messages, post_travel_reimbursement(request=request, forms_TADetails=this_travel_rem,
                                                     travel_app=the_travel_app,
                                                     forms_TAWeeks=this_travel_weeks,
                                                     forms_TRDays=this_travel_days,
                                                     forms_EmployeeExpenses=this_travel_emp_expenses,
                                                     forms_BEExplanations=this_travel_explanations,
                                                     forms_Mileages=this_travel_mileages,
                                                     forms_ExpendaturesCharged=this_travel_exps_charged,
                                                     travel_advance=the_travel_advance,
                                                     sorted_business_meals=sorted_business_meals,
                                                     sorted_expenditures=sorted_expenditures,
                                                     sorted_hotel=sorted_hotels, sorted_others=sorted_others,
                                                     sorted_personal_meals=sorted_personal_meals,
                                                     sorted_travel=sorted_transportations,
                                                     sorted_mileages=mileages_with_numbers,
                                                     sorted_personal_meal_perdiem=sorted_personal_meal_perdiems,
                                                     form_is_declined=form_is_declined, tr_files=the_files,
                                                     tr_advance=the_tr_advance, tr_advances=the_tr_advances))
            response_data['result'] = error_messages
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        print("User is creator: " + str(user_is_creator_of_form))
        if the_travel_advance:
            travel_adv_exists = True
        else:
            travel_adv_exists = False
        # print("tr avdance:" + str(the_tr_advance))
        print("it exists:" + str(travel_adv_exists))
        try:
            ta_doc_num = SAPResponse.objects.get(form='TA-' + str(the_travel_app.formID)).transactionID
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            ta_doc_num = None
        #print("Sap ta_doc_num:" + str(ta_doc_num) + "END")
        return render(request, 'travel/travel_reimbursement.html', {"form_id": pk,
                                                                    "show_chat": True,
                                                                    'forms_TADetails': this_travel_rem,
                                                                    'forms_TAWeeks': this_travel_weeks,
                                                                    'forms_TRDays': this_travel_days,
                                                                    'forms_BEExplanations': this_travel_explanations,
                                                                    'forms_DailyMileages': this_travel_mileages,
                                                                    'forms_ExpendaturesCharged': this_travel_exps_charged,
                                                                    'travel_app': the_travel_app,
                                                                    'travel_advance': the_travel_advance,
                                                                    "business_unit": request.session["business_unit"],
                                                                    'user_dept': request.session['department'],
                                                                    'gl_accounts': gl_accounts,
                                                                    'daily_mileages': mileages_with_numbers,
                                                                    'personal_meals': sorted_personal_meals,
                                                                    'hotel_expenses': sorted_hotels,
                                                                    'transportation_expenses': sorted_transportations,
                                                                    'business_meals': sorted_business_meals,
                                                                    'other_expenses': sorted_others,
                                                                    'expenditures': sorted_expenditures,
                                                                    'cost_center_desc': cost_center_desc,
                                                                    'mileage_weeks': travel_mileage_weeks,
                                                                    'p_meal_weeks': p_meal_weeks,
                                                                    'hotel_weeks': hotel_weeks,
                                                                    'transportation_weeks': transportation_weeks,
                                                                    'b_meal_weeks': b_meal_weeks,
                                                                    'other_weeks': other_weeks,
                                                                    'expenditure_weeks': expenditure_weeks,
                                                                    # 'supporting_document': supporting_document,
                                                                    # 'supporting_document_name': supporting_document_name,
                                                                    'days_of_the_week': days_of_the_week,
                                                                    "current_date": datetime.today(),
                                                                    "personal_meal_perdiems": sorted_personal_meal_perdiems,
                                                                    "form_is_being_approved": form_is_being_approved,
                                                                    "form_is_being_shown_to_approver": form_is_being_shown_to_approver,
                                                                    "approving_modifications": approving_modifications,
                                                                    "all_forms_stages": all_forms_stages,
                                                                    "employees_for_add_new_approver": employees_for_add_new_approver,
                                                                    "accountant_list": accountant_list,
                                                                    "approver_name": request.session['full_name'],
                                                                    "users_stage": users_approval_stage,
                                                                    "today": datetime.now(),
                                                                    "modified_fields": modified_fields,
                                                                    "form_is_declined": form_is_declined,
                                                                    "forms_docs": the_files,
                                                                    "business_docs": business_docs,
                                                                    "personal_docs": personal_docs,
                                                                    "mileage_docs": mileage_docs,
                                                                    "payment_docs": payment_docs,
                                                                    "perdiem_amount": perdiem_amount_chosen,
                                                                    "gls_chosen": gls_chosen,
                                                                    "user_is_creator": user_is_creator_of_form,
                                                                    "tr_advance": the_tr_advance,
                                                                    "travel_app_end": travel_app_end,
                                                                    "SAP_travel": SAP_travel,
                                                                    "SAP_adv": SAP_adv,
                                                                    "travel_adv_exists": travel_adv_exists,
                                                                    "ta_doc_num": ta_doc_num,
                                                                    "user_is_creator": user_is_creator,
                                                                    })
    else:
        return redirect('../../../accounts/login/?next=/forms/travel_reimbursement/' + pk + '/')


# endregion

def test_rem_view(request):
    return render(request, 'travel/travel_reimbursement.html', {})
