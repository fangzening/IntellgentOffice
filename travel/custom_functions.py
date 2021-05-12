import sys
import traceback
import math

from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse, HttpResponse

from office_app.models import *
from travel.models import *
from office_app.approval_functions import *
from datetime import datetime, timedelta
from os import listdir
from os.path import isfile, join
from Smart_Office.settings import *
from django.contrib import messages
from SAP import SAPFunctionsPrd


# from .approval_proccess_functions import *
from travel.models import *


def say_hi():
    return "Hello there"


'''
This posts travel reimbursement application
Author: Corrina Barr
:param request: the webpage request
:return: error message for user to see, if there is any
'''
def post_travel_reimbursement(request, travel_app, forms_TADetails, forms_TAWeeks, forms_TRDays,
                              forms_EmployeeExpenses, forms_BEExplanations, forms_Mileages,
                              forms_ExpendaturesCharged, travel_advance, tr_advance, sorted_mileages, sorted_personal_meals,
                              sorted_hotel, sorted_travel, sorted_business_meals, sorted_others, sorted_expenditures,
                              sorted_personal_meal_perdiem, form_is_declined, tr_files, tr_advances):
    from travel.models import TravelDetailCompany
    from travel.models import ItemType
    from travel.models import TRWeek
    from travel.models import TRDay
    from travel.models import EmployeeExpenses
    from travel.models import ExpenseType
    from travel.models import Mileage
    from travel.models import ExpendituresCharged
    from travel.models import ExpenditureType
    from travel.models import BusinessExpenseExplanation
    from travel.models import TRApprovalProcess
    from travel.models import DailyMileage
    from travel.models import TRFileUpload
    from travel.models import TADetails
    from travel.models import TRGLAccount
    from travel.models import TRModifiedFields
    from travel.models import AdvanceReimbursementApp
    error_messages = {'fatal_errors': "", 'other_errors': []}
    if request.method == 'POST':
        all_weeks = []
        save_data_buttons = ["Save", "Submit", "Approve Modifications", "Save and Return Home"]

        # Check if travel rem object exists, if not, create a new one.
        if forms_TADetails:
            print("Travel Rem exists")
        else:
            # print("Creating new travel rem")
            forms_TADetails = TADetails()
            forms_TAWeeks = TRWeek()
            forms_TRDays = TRDay()
            forms_EmployeeExpenses = EmployeeExpenses()
            forms_TypeList = ExpenseType()
            forms_ItemList = ItemType()
            forms_Mileages = Mileage()
            forms_ExpendaturesCharged = ExpendituresCharged()
            travel_advance = None

        # Check if it is being saved or submitted.
        if request.POST.get('submit_button') == "Save":
            is_completed = False
        else:
            is_completed = True

        # region Getting Data from POST

        ##print("request.POST: " + str(request.POST))
        all_post_data = dict(request.POST)
        print("\nAll Post Data: " + str(all_post_data))

        # Weeks:
        ## Mileage:
        mileage_week_begins = all_post_data['week_begin']
        mileage_week_ends = all_post_data['week_end']
        all_weeks += merge(mileage_week_begins, mileage_week_ends)
        ## Personal Meal:
        p_meal_week_starts = all_post_data['meal_week_start']
        p_meal_week_ends = all_post_data['meal_week_end']
        all_weeks += merge(p_meal_week_starts, p_meal_week_ends)
        ## Hotel:
        hotel_week_starts = all_post_data['hotel_week_start']
        hotel_week_ends = all_post_data['hotel_week_end']
        all_weeks += merge(hotel_week_starts, hotel_week_ends)
        ## Transportation
        tran_week_starts = all_post_data['transportation_week_start']
        tran_week_ends = all_post_data['transportation_week_end']
        all_weeks += merge(tran_week_starts, tran_week_ends)
        ## Business Meal
        b_meal_week_starts = all_post_data['businessmeal_week_start']
        b_meal_week_ends = all_post_data['businessmeal_week_end']
        all_weeks += merge(b_meal_week_starts, b_meal_week_ends)
        ## Other
        others_week_starts = all_post_data['others_week_start']
        others_week_end = all_post_data['others_week_end']
        all_weeks += merge(others_week_starts, others_week_end)
        ## Expenditure
        expenditure_week_starts = all_post_data['expenditure_week_start']
        expenditure_week_ends = all_post_data['expenditure_week_end']
        all_weeks += merge(expenditure_week_starts, expenditure_week_ends)

        ##print("All Weeks: " + str(all_weeks))

        ## Page 1:
        ### Mileage Rows:

        departure_froms = all_post_data['departure_from']
        destination_tos = all_post_data['destination_to']
        dates = all_post_data['date']  # Get keys that contain this
        mileages = all_post_data["mileage"]
        amounts = all_post_data["amount"]
        try:
            mileage_ids = all_post_data["mileage_id"]  # This field only exists on a saved form
        except:
            mileage_ids = None
        total = request.POST.get('total')
        print("GL ACCOUNT:" + all_post_data['gl_account'][0] + "END")
        gl_account = GLAccount.objects.get(glCode=all_post_data['gl_account'][0])

        print("***************************REQUEST.FILES: " + str(request.FILES))
        all_files = dict(request.FILES)
        print("all files: " + str(all_files))
        # print("\nall post data: " + str(all_post_data))
        all_files_with_index = []

        # Use mileage weeks to determine how many supporting documents there should be
        # Change name of supporting document somehow to figure out what it is assigned to
        # If it has a document to upload, an object is added to all_files['supporting_document'] list
        #   Otherwise, it is added to all_post_data['supporting_document'] list as empty string
        # If I could change the name to have -rownumber I could parse the name to get the index
        # I would have to create a javascript function that would allow me to do that
        # It would have to update if a row in the middle was deleted

        number_of_weeks = len(all_post_data['week_begin'])
        # all_supporting_documents = {}

        count = 0

        # Get weeks from forms_Mileages
        mileage_week_ids = []

        # print("Forms mileagees: " + str(forms_Mileages))

        if str(forms_Mileages)[0] == '[':
            for milage in forms_Mileages:
                if milage.dayID.weekID.pk not in mileage_week_ids:
                    mileage_week_ids.append(milage.dayID.weekID.pk)
        else:
            mileage_week_ids = [0]

        ## Page 2:
        ### Personal Expenses:
        #### Meal:
        from travel.models import ItemType
        personal_breakfasts = [all_post_data['personal_breakfast'], all_post_data['personal_meal_date'],
                               ItemType.objects.get(itemName='Breakfast'), "personal_breakfast"]
        personal_lunches = [all_post_data['personal_lunch'], all_post_data['personal_meal_date'],
                            ItemType.objects.get(itemName='Lunch'), "personal_lunch"]
        personal_dinners = [all_post_data['personal_dinner'], all_post_data['personal_meal_date'],
                            ItemType.objects.get(itemName='Dinner'), "personal_dinner"]
        try:

            personal_meal_ids = all_post_data["meal_id"]  # This field only exists on a saved form
        except:
            personal_meal_ids = None
        personal_meal_per_diem = [all_post_data['personal_meal_perdiem'], all_post_data['personal_meal_perdiem_date'],
                                  ItemType.objects.get(itemName='Per Diem'), "personal_meal_perdiem"]

        #### Hotel:
        hotel_room_charges = [all_post_data['hotel_room_change'], all_post_data['hotel_date'],
                              ItemType.objects.get(itemName='Hotel Room Charge'), "hotel_room_change"]
        hotel_laundries = [all_post_data['hotel_laundry'], all_post_data['hotel_date'],
                           ItemType.objects.get(itemName='Laundry'), "hotel_laundry"]
        hotel_telephones = [all_post_data['hotel_telephone'], all_post_data['hotel_date'],
                            ItemType.objects.get(itemName='Telephone'), "hotel_telephone"]
        hotel_others = [all_post_data['hotel_others'], all_post_data['hotel_date'],
                        ItemType.objects.get(itemName='Others'), "hotel_others"]
        try:
            hotel_ids = all_post_data["hotel_id"]  # This field only exists on a saved form
        except:
            hotel_ids = None

        #### Transportation:
        try:
            parkings = [all_post_data['parking'], all_post_data['transportation_date'],
                        ItemType.objects.get(itemName='Parking'), "parking"]
        except:
            print('\n'.join(traceback.format_exception(*sys.exc_info())))
            error_messages['fatal_errors'] = "error getting parking data"
            return error_messages
        tolls = [all_post_data['tolls'], all_post_data['transportation_date'], ItemType.objects.get(itemName='Tolls'),
                 "tolls"]
        rides = [all_post_data['rides'], all_post_data['transportation_date'],
                 ItemType.objects.get(itemName='Car Rental/Bus/Taxi'), "rides"]
        transportation_others = [all_post_data['transportation_others'], all_post_data['transportation_date'],
                                 ItemType.objects.get(itemName='Others'), "transportation_others"]

        try:
            transportation_ids = all_post_data["transportation_id"]  # This field only exists on a saved form
        except:
            transportation_ids = None

        ### Business Expenses:
        #### Meal:
        business_breakfasts = [all_post_data['business_breakfast'], all_post_data['business_meal_date'],
                               ItemType.objects.get(itemName='Breakfast'), "business_breakfast"]
        business_lunches = [all_post_data['business_lunch'], all_post_data['business_meal_date'],
                            ItemType.objects.get(itemName='Lunch'), "business_lunch"]
        business_dinners = [all_post_data['business_dinner'], all_post_data['business_meal_date'],
                            ItemType.objects.get(itemName='Dinner'), "business_dinner"]
        try:
            business_meal_ids = all_post_data["business_breakfast_id"]  # This field only exists on a saved form
        except:
            business_meal_ids = None

        #### Others:
        others_telephones = [all_post_data['others_telephone'], all_post_data['others_date'],
                             ItemType.objects.get(itemName='Telephone'), "others_telephone"]
        others_gifts = [all_post_data['others_gift'], all_post_data['others_date'],
                        ItemType.objects.get(itemName='Gifts/Entertainment'), "others_gift"]
        others_miscs = [all_post_data['others_misc'], all_post_data['others_date'],
                        ItemType.objects.get(itemName='Miscellaneous'), "others_misc"]
        try:
            other_ids = all_post_data["other_id"]  # This field only exists on a saved form
        except:
            other_ids = None

        #### Expenditures: ### Different than other fields
        expenditure_airfares = [all_post_data['expenditure_airfare'], all_post_data['expenditure_date'],
                                ExpenditureType.objects.get(expenditureType='Airline Fare'), "expenditure_airfare"]
        expenditure_hotels = [all_post_data['expenditure_hotel'], all_post_data['expenditure_date'],
                              ExpenditureType.objects.get(expenditureType='Hotel'), "expenditure_hotel"]
        expenditure_autorentals = [all_post_data['expenditure_autorental'], all_post_data['expenditure_date'],
                                   ExpenditureType.objects.get(expenditureType='Auto Rental'), "expenditure_autorental"]
        expenditure_others = [all_post_data['expenditure_other'], all_post_data['expenditure_date'],
                              ExpenditureType.objects.get(expenditureType='Other'), "expenditure_other"]

        ### Expense Explaination (Pop Up)
        business_expense_amount = all_post_data['business_expense_amount']
        business_expense_place = all_post_data['business_expense_place']
        business_expense_purpose = all_post_data['business_expense_purpose']
        business_expense_detail = all_post_data['business_expense_detail']
        business_expense_counterparty = all_post_data['business_expense_counterparty']
        business_expense_name = all_post_data['business_expense_name']
        business_expense_title = all_post_data['business_expense_title']

        ## Page 3 (Summary):
        expenditure_reimbursed = request.POST.get('expenditure_reimbursed')
        expenditure_charged = request.POST.get('expenditure_charged')
        employee_amount_due = request.POST.get('employee_amount_due')
        company_amount_due = request.POST.get('company_amount_due')
        total_expenditures = request.POST.get('total_expenditures')

        # region Save Data
        if request.POST.get('submit_button') in save_data_buttons:
            if form_is_declined:
                forms_approvers = TRApprovalProcess.objects.filter(formID=forms_TADetails)
                for approver in forms_approvers:
                    approver.delete()
            ## TADetails:
            if forms_TADetails.numOfWeeks is not None:  # Check if it exists yet
                forms_TADetails.isCompleted = is_completed
                forms_TADetails.save()
            else:
                forms_TADetails = TADetails()
                forms_TADetails.update_ta_detail(travel_app, 0, is_completed)
            ## TRWeek:
            # Delete old TR days:
            if forms_TRDays is not None:
                try:
                    for day in forms_TRDays:
                        day.delete()
                except:
                    print("No old days to delete")
            # Delete old TR Weeks:
            if forms_TAWeeks is not None:
                try:
                    for week in forms_TAWeeks:
                        week.delete()
                except:
                    print("No old weeks to delete")
            if forms_EmployeeExpenses is not None:
                try:
                    for exp in forms_EmployeeExpenses:
                        exp.delete()
                except:
                    print("No old employee expenses to delete")
            # Delete old MileageDays:
            if forms_Mileages is not None:
                try:
                    for daily_mileage in forms_Mileages:
                        daily_mileage.mileage.delete()
                        daily_mileage.delete()
                except:
                    print("No old mileage days to delete")
            # Delete old expenditures:
            if forms_ExpendaturesCharged is not None:
                try:
                    for exp in forms_ExpendaturesCharged:
                        exp.delete()
                except:
                    print("No old expenditures to delete")
            # Delete old business explanations:
            if forms_BEExplanations is not None:
                try:
                    for exp in forms_BEExplanations:
                        print("***************************************deleting explaination: " + str(exp))
                        exp.delete()
                except:
                    print("***************************************************No old expenditures to delete")
            else:
                print("it is none: " + str(forms_BEExplanations))
            # Delete old GL Accounts chosen:


            # TRWeek & TRDay to connect mileages/expenses with no dates to the form:
            unknown_TRWeek = TRWeek()
            unknown_TRWeek.save_tr_week(formID=forms_TADetails, startDate=None,
                                        endDate=None)
            unknown_TRDay = TRDay()
            unknown_TRDay.save_tr_day(weekID=unknown_TRWeek, date=None)

            # Create TRWeeks:
            TRWeek.create_multiple_TRWeeks(tuple_list=all_weeks, travel_reimbursement=forms_TADetails)

            # Create GL Account data:
            gl_account_names = ['gl_account_p_meal', 'gl_account_hotel', 'gl_account_transportation', 'gl_account_b_meal', 'gl_account_others', 'gl_account_expenditure']
            count = 1
            for name in gl_account_names:
                gl = TRGLAccount()
                gl.sectionName = "Section" + str(count)
                gl.trForm = forms_TADetails
                gl.glAccount = GLAccount.objects.filter(glCode=request.POST.get(name)).first()
                # print("name: " + str(name))
                # print("Section name: " + gl.sectionName)
                # print("value: " + request.POST.get(name))
                # print("gl account: " + str(gl.glAccount))
                gl.save()
                count += 1

            # Files:
            # Personal Files:
            try:
                personal_files = all_files['personal_file']
            except:
                personal_files = None
            if personal_files != None:
                for file in all_files['personal_file']:
                    try:
                        personal_file = TRFileUpload()
                        personal_file.location = "travel/personal-expenses/"
                        personal_file.formLink = tr_files
                        personal_file.file = file
                        personal_file.save()
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "error personal expense files"
                        return error_messages

            # Business Files:
            try:
                business_files = all_files['business_file']
            except:
                business_files = None
            if business_files != None:
                for file in all_files['business_file']:
                    try:
                        business_file = TRFileUpload()
                        business_file.location = "travel/business-expenses/"
                        business_file.formLink = tr_files
                        business_file.file = file
                        business_file.save()
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "error uploading business expense files"
                        return error_messages

            # Payment Files:
            try:
                company_amount_due_files = all_files['company_amount_due_file']
                #print("*******************************************************************company amount due exists")
            except:
                company_amount_due_files = None
                #print("*******************************************************************company amount due doesnt exist")
            if company_amount_due_files != None:
                for file in all_files['company_amount_due_file']:
                    try:
                        payment_file = TRFileUpload()
                        payment_file.location = "travel/proof-of-payment/"
                        payment_file.formLink = tr_files
                        payment_file.file = file
                        payment_file.save()
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "error uploading company amount due files"
                        return error_messages

            # Mileage Files:
            try:
                supporting_documents = all_files['supporting_document']
            except:
                supporting_documents = None
            if supporting_documents != None:
                for file in all_files['supporting_document']:
                    try:
                        mileage_file = TRFileUpload()
                        mileage_file.location = "travel/mileage-expenses/"
                        mileage_file.formLink = tr_files
                        mileage_file.file = file
                        mileage_file.save()
                    except:
                        print('\n'.join(traceback.format_exception(*sys.exc_info())))
                        error_messages['fatal_errors'] = "error uploading mileage expense files"
                        return error_messages

            ## Mileages:
            index = 0
            # #print("All supporting documents: " + str(all_supporting_documents))
            for mileage in mileages:
                current_mileage = Mileage()
                try:
                    current_mileage.save_mileage(fromLoc=departure_froms[index], toLoc=destination_tos[index],
                                                 amount=amounts[index], glAccount=gl_account, miles=mileage,
                                                 supportingDoc=None)
                    # Check if there is a TRDay where TRDay__date=date
                    if dates[index] != '':
                        mileage_day = TRDay.objects.filter(date=dates[index],
                                                           weekID__formID__taDetail=forms_TADetails).first()
                    else:
                        mileage_day = unknown_TRDay
                    if mileage_day is not None:
                        # If there is, assign it's dayID to the Day Object
                        mileage_daily = DailyMileage()
                        mileage_daily.save_daily_mileage_entry(dayID=mileage_day, mileage=current_mileage)
                    else:
                        # Else, create a TRDay
                        # If there is no TRWeek Assocciated with that TRDay, create that TRWeek
                        # create dailymileage object with corrosponding dayID
                        if dates[index] != '':
                            current_TRWeek = TRWeek.objects.filter(formID=forms_TADetails, startDate__lte=dates[index],
                                                                   endDate__gte=dates[index]).first()
                            if current_TRWeek is not None:
                                current_TRDay = TRDay()
                                current_TRDay.save_tr_day(weekID=current_TRWeek, date=dates[index])
                                mileage_day = current_TRDay
                                mileage_daily = DailyMileage()
                                mileage_daily.save_daily_mileage_entry(dayID=mileage_day, mileage=current_mileage)
                            else:
                                new_TRWeek = TRWeek()
                                week_startDate = get_first_day_of_week(dates[index])
                                week_endDate = get_last_day_of_week(dates[index])
                                new_TRWeek.save_tr_week(formID=forms_TADetails, startDate=week_startDate,
                                                        endDate=week_endDate)
                                forms_TADetails.numOfWeeks += 1
                                forms_TADetails.save()
                                current_TRDay = TRDay()
                                current_TRDay.save_tr_day(weekID=new_TRWeek, date=dates[index])
                                mileage_day = current_TRDay
                                mileage_daily = DailyMileage()
                                mileage_daily.save_daily_mileage_entry(dayID=mileage_day, mileage=current_mileage)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = "Error saving mileage data. Please contact IT."
                    return error_messages
                index += 1

            ## EmployeeExpenses (Each Employee Expense represents one field of the second page of the TR. And they are all dynamic)
            ### Personal Expenses:
            # Get all fields from personal expenses
            # Map: (values(list), dates(list), ItemType, fieldName)}
            personal_expenses_fields = [
                personal_breakfasts,
                personal_lunches,
                personal_dinners,
                personal_meal_per_diem,
                hotel_room_charges,
                hotel_laundries,
                hotel_telephones,
                hotel_others,
                parkings,
                tolls,
                rides,
                transportation_others
            ]
            personal_expenseType = ExpenseType.objects.get(typeName="Personal Expense")
            save_fields_of_same_expense_type(expense_type=personal_expenseType,
                                             field_list=personal_expenses_fields,
                                             forms_TADetails=forms_TADetails)

            # # Get all fields from business expenses:
            business_expenses_fields = [
                business_breakfasts,
                business_lunches,
                business_dinners,
                others_telephones,
                others_gifts,
                others_miscs,
            ]

            business_expenseType = ExpenseType.objects.get(typeName="Business Expense")
            save_fields_of_same_expense_type(expense_type=business_expenseType,
                                             field_list=business_expenses_fields,
                                             forms_TADetails=forms_TADetails)

            # # Get Expenditures:
            expenditure_fields = [
                expenditure_airfares,
                expenditure_autorentals,
                expenditure_hotels,
                expenditure_others,
            ]
            save_expenditures(expenditure_fields, forms_TADetails)

            # Business Expense Explanation Popup:
            count = 0
            dayID = TRDay.objects.filter(weekID__formID=forms_TADetails).first()
            for bee in business_expense_detail:
                business_expense_explanation = BusinessExpenseExplanation()
                business_expense_explanation.save_be_explanation(amount=business_expense_amount[count],
                                                                 purpose=business_expense_purpose[count],
                                                                 place=business_expense_place[count],
                                                                 counterParty=business_expense_counterparty[count],
                                                                 name=business_expense_name[count],
                                                                 title=business_expense_title[count],
                                                                 dayID=dayID,
                                                                 detail=business_expense_detail[count])
                count += 1

            # region Advance Section:
            error_messages = merge_dictionaries(error_messages, update_travel_advance(request=request, all_post_data=all_post_data, company_amount_due=company_amount_due,
                                  is_completed=is_completed, tr_advance=tr_advance, tr_advances=tr_advances,
                                  travel_app=travel_app, travel_advance=travel_advance, tr_app=forms_TADetails))
            if error_messages['fatal_errors'] != '':
                return error_messages
            # endregion


        # endregion

        # region Approval Process
        if request.POST.get('submit_button') == 'Save':
            # Check if stage 0 needs to be created or if it was already created
            stage_zero = TRApprovalProcess.objects.filter(formID=forms_TADetails, stage=0,
                                                          approverID=travel_app.employee).first()
            if stage_zero is None:
                new_stage_zero = TRApprovalProcess()
                new_stage_zero.create_approval_stage(formID=forms_TADetails, stage=0,
                                                     approverID=travel_app.employee,
                                                     count=0)
            forms_TADetails.currentStage = 0
            forms_TADetails.save()
            return error_messages

        elif request.POST.get('submit_button') == 'Submit':
            # Delete travel rem approval stage thing that is stage 0
            stage_zero = TRApprovalProcess.objects.filter(formID=forms_TADetails, approverID=travel_app.employee,
                                                          stage=0).first()
            if stage_zero:
                stage_zero.delete()

            # Instantiate Approval List:
            error_messages = merge_dictionaries(error_messages, instantiate_tr_for_approval(travel_app=travel_app,
                                                        travel_rem=forms_TADetails, request=request))

            return error_messages

        elif request.POST.get('submit_button') == 'Send Modified':
            create_TRModifiedFields_objects(request, TR_form=forms_TADetails, old_mileages=sorted_mileages,
                                            old_p_meals=sorted_personal_meals, old_hotels=sorted_hotel,
                                            old_transportations=sorted_travel, old_b_meals=sorted_business_meals,
                                            old_others=sorted_others, old_expenditures=sorted_expenditures,
                                            p_meal_perdiem=sorted_personal_meal_perdiem,
                                            old_business_explanations=forms_BEExplanations, all_post_data=all_post_data,
                                            form_is_declined=form_is_declined, tr_advance=tr_advance)

            error_messages = merge_dictionaries(error_messages, update_stages_for_modification_request(request=request,
                                                                   form=forms_TADetails,
                                                                   approval_process_type=TRApprovalProcess))
            return error_messages

        elif request.POST.get('submit_button') == 'Change Approver List':
            if request.POST.get('add_approver_action') == 'Add to approval list':
                new_approvers = []
                for approver_pk in all_post_data['add_approvers_options']:
                    new_approvers.append(Employee.objects.get(pk=approver_pk))
                error_messages = merge_dictionaries(error_messages, add_approver(form=forms_TADetails,
                                             new_approvers=new_approvers,
                                             stage=forms_TADetails.currentStage,
                                             approval_process_type=TRApprovalProcess, request=request))
                return error_messages

            elif request.POST.get('add_approver_action') == 'Replace me in approval list':
                error_messages = merge_dictionaries(error_messages, replace_approver(form=forms_TADetails,
                                                 stage=forms_TADetails.currentStage,
                                                 new_approver=Employee.objects.get(
                                                     associateID=request.POST.get('add_approvers_options')),
                                                 old_approver=Employee.objects.get(associateID=request.session['user_id']),
                                                 approval_process_type=TRApprovalProcess, request=request))
                return error_messages
        elif request.POST.get('submit_button') == 'Approve':
            error_messages = merge_dictionaries(error_messages, approve_form(request, approval_process_type=TRApprovalProcess, form=forms_TADetails, advance_type=AdvanceReimbursementApp))
            return error_messages

        elif request.POST.get('submit_button') == 'Submit and Approve':
            error_messages = merge_dictionaries(error_messages, update_travel_advance(request=request, all_post_data=all_post_data,
                                               company_amount_due=company_amount_due,
                                               is_completed=is_completed, tr_advance=tr_advance,
                                               tr_advances=tr_advances,
                                               travel_app=travel_app, travel_advance=travel_advance, tr_app=forms_TADetails))
            if error_messages['fatal_errors'] != '':
                # TODO: Create errors to display to user and check for connection issues
                return error_messages

            error_messages = merge_dictionaries(error_messages, approve_form(request, approval_process_type=TRApprovalProcess, form=forms_TADetails, advance_type=AdvanceReimbursementApp))
            return error_messages

        elif request.POST.get('submit_button') == 'Approve Modifications':
            error_messages = merge_dictionaries(error_messages, approve_modifications(request=request,
                                                  form=forms_TADetails,
                                                  approval_process_type=TRApprovalProcess,
                                                  modified_fields_type=TRModifiedFields))
            return error_messages
            # endregion

        if request.POST.get('submit_button') == 'Decline Modifications':
            error_messages = merge_dictionaries(error_messages, decline_modifications(request=request,
                                                  form=forms_TADetails,
                                                  approval_process_type=TRApprovalProcess,
                                                  modified_fields_type=TRModifiedFields))

            return error_messages

        elif request.POST.get('submit_button') == 'Decline':
            error_messages = merge_dictionaries(error_messages, decline_form(request, form=forms_TADetails, approval_process_type=TRApprovalProcess))
            return error_messages

    return error_messages
        # endregion


'''
This instantiates Approval List for a travel reimbursement application
Author: Corrina Barr
:param request: the webpage request
:param expendatures: the expendatures from the travel reimbursement application
:param travel_app: the travel reimbursement tied to the travel reimbursement application
:param request: the webpage request
:return: nothing
'''
def instantiate_tr_for_approval(request, travel_app, travel_rem):
    from travel.models import TRApprovalProcess
    error_messages = {'fatal_errors': '', 'other_errors': []}

    # Get budget source code informations
    try:
        budgetSC = CostCenter.objects.get(costCenterCode=travel_app.budgetSourceCode)
    except:
        travel_rem.isCompleted = False
        travel_rem.currentStage = 0
        travel_rem.save()
        error_messages['fatal_errors'] = 'Error retrieving budget source code! Please contact IT.'
        return error_messages

    try:
        businessUnit = budgetSC.businessUnit
    except:
        travel_rem.isCompleted = False
        travel_rem.currentStage = 0
        travel_rem.save()
        error_messages['fatal_errors'] = 'Error retrieving business unit from budget source code! Please contact IT.'
        return error_messages

    try:
        businessGroup = businessUnit.businessGroup
    except:
        travel_rem.isCompleted = False
        travel_rem.currentStage = 0
        travel_rem.save()
        error_messages['fatal_errors'] = 'Error retrieving business group data! Please contact IT.'
        return error_messages


    error_messages = merge_dictionaries(error_messages, travel_rem.initiate_tr_approval_proccess(request=request))
    if error_messages['fatal_errors'] != '':
        travel_rem.isCompleted = False
        travel_rem.currentStage = 0
        travel_rem.save()
        return error_messages
    return error_messages
    # endregion


'''
Merges 2 lists into a tuple
Author: Geeks for Geeks
:param list1: list that will be the first element of the tuple
:param list2: list that will be second element of the tuple
:rerurn merged_list: returns the two lists as a merged tuple
'''
def merge(list1, list2):
    # print("Mergeing " + str(list1) + " with " + str(list2))
    # Make sure they are both lists
    if str(list1)[0] != '[':
        list1 = [list1]
        list2 = [list2]
    # Merge them
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    return merged_list


'''
Returns first day of the week
Author: Corrina Barr
:param day: Day of week that you want to get the first day of the week for
:return start: returns the first day of the week
'''
def get_first_day_of_week(day):
    dt = datetime.strptime(day, '%Y-%m-%d')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    return start


'''
Returns last day of the week
Author: Corrina Barr
:param day: Day of week that you want to get the first day of the week for
:return end: returns the last day of the week
'''
def get_last_day_of_week(day):
    dt = datetime.strptime(day, '%Y-%m-%d')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    return end


'''
Used for saving all fields of each expensetype
Author: Corrina Barr
:param expenseType: The ExpenseType
:param fieldList: a list of lists that contain information about every field that is of the same expensetype
                    Map:
                        for each item in fieldList:
                        (values, dates, itemType, fieldName)
                    Indexes:
                        values = [0]
                        dates = [1]
                        itemType object = [2]
                        fieldName = [3]
:param forms_TADetails: Gets the TADetail Object associated with the TR form
:return employee_expenses: returns list of all employeeExpense objects that were created
'''
def save_fields_of_same_expense_type(expense_type, field_list, forms_TADetails):
    from travel.models import ItemType
    from travel.models import TRWeek
    from travel.models import TRDay
    from travel.models import EmployeeExpenses
    from travel.models import ExpenseType
    from travel.models import Mileage
    from travel.models import ExpendituresCharged
    from travel.models import ExpenditureType
    employee_expenses = []

    for field in field_list:
        field_name = field[3]
        item_type = field[2]
        dates = field[1]
        values = field[0]

        ##print("\nField Name: " + str(field_name))
        ##print("Item Type: " + str(item_type))
        ##print("Dates: " + str(dates))
        ##print("Values: " + str(values))

        count = 0
        for value in values:
            ##print("Current value: " + str(value))
            current_date = dates[count]
            ##print("Current Date: " + str(current_date))
            if current_date == '':
                print("current date is none")
                # employee_expense = EmployeeExpenses()
                # employee_expense.save_expense(expenseType=expense_type, amount=value,
                #                               itemType=item_type, fieldName=field_name+"-"+str(count), dayID=unknown_date)
                # count += 1
                # employee_expenses.append(employee_expense)
            else:
                ## Get the week corrosponding with the item's date:
                current_TRWeek = TRWeek.objects.filter(formID=forms_TADetails, startDate__lte=current_date,
                                                       endDate__gte=current_date).first()
                if current_TRWeek is not None:
                    # check if tr day is made. If not, create one.
                    current_TRDay = TRDay.objects.filter(date=current_date, weekID__formID=forms_TADetails).first()
                    if current_TRDay is None:
                        current_TRDay = TRDay()
                        current_TRDay.save_tr_day(weekID=current_TRWeek, date=current_date)
                else:
                    current_TRWeek = TRWeek()
                    week_startDate = get_first_day_of_week(current_date)
                    week_endDate = get_last_day_of_week(current_date)
                    current_TRWeek.save_tr_week(formID=forms_TADetails, startDate=week_startDate, endDate=week_endDate)
                    forms_TADetails.numOfWeeks += 1

                    current_TRDay = TRDay()
                    current_TRDay.save_tr_day(weekID=current_TRWeek, date=current_date)
                    # Update number of weeks:
                    forms_TADetails.save()

                employee_expense = EmployeeExpenses()
                employee_expense.save_expense(expenseType=expense_type, amount=value,
                                              itemType=item_type, fieldName=field_name + "-" + str(count),
                                              dayID=current_TRDay)
                count += 1
                employee_expenses.append(employee_expense)

    return employee_expenses


'''
Used for saving all fields that are linked to expenditures
Author: Corrina Barr
:param fieldList: a list of lists that contain information about every field that is an expenditure. 
                Same format as fieldList parameter for save_fields_of_same_expense_type
                    Map:
                        for each item in fieldList:
                        (values, dates, expenditureType, fieldName)
                    Indexes:
                        values = [0]
                        dates = [1]
                        expenditureType object = [2]
                        fieldName = [3]
:param forms_TADetails: Gets the TADetail Object associated with the TR form
:return employee_expenses: returns list of all employeeExpense objects that were created
'''
def save_expenditures(field_list, forms_TADetails):
    from travel.models import ItemType
    from travel.models import TRWeek
    from travel.models import TRDay
    from travel.models import EmployeeExpenses
    from travel.models import ExpenseType
    from travel.models import Mileage
    from travel.models import ExpendituresCharged
    from travel.models import ExpenditureType
    employee_expenditures = []
    unknown_date = TRDay.objects.filter(weekID__formID=forms_TADetails, weekID__startDate=None,
                                        weekID__endDate=None).first()
    for field in field_list:
        field_name = field[3]
        expeniture_type = field[2]
        dates = field[1]
        expenditure_costs = field[0]
        ##print("Expenditure Field name: " + str(field_name))
        ##print("Expenditure Type: " + str(expeniture_type))
        ##print("Expenditure Dates: " + str(dates))
        ##print("Expenditure Costs: " + str(expenditure_costs))

        count = 0
        for cost in expenditure_costs:
            current_date = dates[count]
            ##print("Current Date: " + str(current_date))
            if current_date == '':
                expendture = ExpendituresCharged()
                expendture.save_expenditures_charged(expenditureType=expeniture_type, expenditureCost=cost,
                                                     fieldName=field_name + "-" + str(count), dayID=unknown_date)
                count += 1
                employee_expenditures.append(expendture)
            else:
                ## Get the week corrosponding with the item's date:
                current_TRWeek = TRWeek.objects.filter(formID=forms_TADetails, startDate__lte=current_date,
                                                       endDate__gte=current_date).first()
                if current_TRWeek is not None:
                    # check if tr day is made. If not, create one.
                    current_TRDay = TRDay.objects.filter(date=current_date, weekID__formID=forms_TADetails).first()
                    if current_TRDay is None:
                        current_TRDay = TRDay()
                        current_TRDay.save_tr_day(weekID=current_TRWeek, date=current_date)
                else:
                    current_TRWeek = TRWeek()
                    week_startDate = get_first_day_of_week(current_date)
                    week_endDate = get_last_day_of_week(current_date)
                    current_TRWeek.save_tr_week(formID=forms_TADetails, startDate=week_startDate, endDate=week_endDate)
                    forms_TADetails.numOfWeeks += 1

                    current_TRDay = TRDay()
                    current_TRDay.save_tr_day(weekID=current_TRWeek, date=current_date)
                    forms_TADetails.save()

                expendture = ExpendituresCharged()
                # print("Saving Expenditure")
                expendture.save_expenditures_charged(expenditureType=expeniture_type, expenditureCost=cost,
                                                     fieldName=field_name + "-" + str(count), dayID=current_TRDay)
                # print("Saved Expenditure")
                count += 1
                employee_expenditures.append(expendture)

    return employee_expenditures


'''
This function updates a list that holds information about each row for a section on page 2 of the Travel Reimbursement Form
In order for it to work you have to set the list to the function, like:
list_to_update = update_section_list(list_to_update, row_number, 'personal_breakfast', expense)
Author: Corrina Barr
:param section_list: the list that will be updated
                    The list is a list of dictionaries, each dictionary in the list representing a row in the form.
                    The list will be looped through in the template to display saved information for a section.
:param row_number: the row number that is associate with the field
:param field_name_without_number: the name of the field in the form
:param expense: the employee expense object associated with the field
:return: returns the updated list
'''
def update_section_list(section_list, row_number, field_name_without_number, expense):
    # Check if there is a dictionary in the sorted personal meals that has the key number with the value being the number after the dash in field_name_with_number:
    # print('Section List Before: ' + str(section_list))

    count = 0
    for dict in section_list:
        if dict["row"] == row_number:
            dict.update({field_name_without_number: expense.amount})
            # if field_name_without_number == 'others_perdiem_date':
            #     print("Update Dictionary: " + str(dict))
            # print('Section list after: ' + str(section_list))
            return section_list

    # If they didn't find it (if they found it the function would have ended by now because the return statement):
    day_of_week = int(row_number) % 7
    new_dictionary = {field_name_without_number: expense.amount, "row": row_number, "day_of_week": str(day_of_week),
                      "date": expense.dayID.date, "week": expense.dayID.weekID}
    # if field_name_without_number == 'others_perdiem_date':
    #     print("New Dictionary: " + str(new_dictionary))
    section_list.append(new_dictionary)
    sort_list_of_dictionaries_by_dictionary_key(section_list, "date")
    # print('Section list after: ' + str(section_list))
    return section_list


'''
same as update_section_list but for expenditures instead of expenses
This function updates a list that holds information about each row for a section on page 2 of the Travel Reimbursement Form
In order for it to work you have to set the list to the function, like:
list_to_update = update_section_list(list_to_update, row_number, 'personal_breakfast', expense)
Author: Corrina Barr
:param section_list: the list that will be updated
                    The list is a list of dictionaries, each dictionary in the list representing a row in the form.
                    The list will be looped through in the template to display saved information for a section.
:param row_number: the row number that is associate with the field
:param field_name_without_number: the name of the field in the form
:param expense: the employee expense object associated with the field
:return: returns the updated list
'''


def update_section_list_expenditure(section_list, row_number, field_name_without_number, expense):
    # Check if there is a dictionary in the sorted personal meals that has the key number with the value being the number after the dash in field_name_with_number:
    # print('Section List Before: ' + str(section_list))

    count = 0
    for dict in section_list:
        if dict["row"] == row_number:
            dict.update({field_name_without_number: expense.expenditureCost})
            # print('Section list after: ' + str(section_list))
            return section_list

    # If they didn't find it (if they found it the function would have ended by now because the return statement):
    day_of_week = int(row_number) % 7
    new_dictionary = {field_name_without_number: expense.expenditureCost, "row": row_number,
                      "day_of_week": str(day_of_week),
                      "date": expense.dayID.date, "week": expense.dayID.weekID}
    section_list.append(new_dictionary)
    sort_list_of_dictionaries_by_dictionary_key(section_list, "date")
    # print('Section list after: ' + str(section_list))
    return section_list


'''
This function will sort a list of dictionaries by a specific key in the dictionaries
Author: Corrina Barr
:param dict_key: the key that all the dictionaries have in the list that they will be sorted by
:param dict_list: the list of dictionaries that will be sorted
:return: returns the sorted list
'''


def sort_list_of_dictionaries_by_dictionary_key(dict_list, dict_key):
    sorted_list = []
    dict_position = 0
    for new_dict in dict_list:
        for sorted_dict in sorted_list:
            if new_dict[dict_key] != None and sorted_dict[dict_key] != None:
                if new_dict[dict_key] > sorted_dict[dict_key]:
                    dict_position = sorted_list.index(sorted_dict) + 1
        sorted_list.insert(dict_position, new_dict)
    return sorted_list




# I'm going to try to make it so that we can use the same functions for both forms
# '''
# Gets the link for a specific form
# Author: Corrina Barr
# :param form_object:
# :return: returns the link to the form
# '''
#
#
# def get_link(form_object):
#     form_type = form_object.form_type()
#     form_in_url = form_type.lower()
#     form_in_url = form_in_url.replace(' ', '_')
#     form_in_url = form_in_url.replace(" ", "_")
#     url = str(settings.BASE_URL) + "forms/" + form_in_url + "/" + str(form_object.formID)
#     # print("Form link: " + url)
#     return url
#
#
# '''
# Gets the path for a form, excluding the base url
# Author: Corrina Barr
# :param form_object:
# :return: returns the link to the form
# '''
#
#
# def get_form_path_without_base_url(form_object):
#     form_type = form_object.form_type()
#     form_in_url = form_type.lower()
#     form_in_url = form_in_url.replace(' ', '_')
#     form_in_url = form_in_url.replace(" ", "_")
#     url = "forms/" + form_in_url + "/" + str(form_object.formID)
#     ##print("Form link: " + url)
#     return url


'''
This function removes a file and all files that are associated with it from the project.
Author: Corrina Barr
:param document_object: The original file that will be deleted (can get it from the model it is a part of)
:param url_inside_media_folder: The path inside the media folder that the file is located in
                                example: "\media\\travel\mileage_expenses\\"
'''


def remove_file_and_associated_files(document_object, url_inside_media_folder):
    base_name = str(document_object)
    document_object.delete()
    base_name = base_name.split('.')
    base_name = base_name[: len(base_name) - 1]

    # If it has multiple periods it will return a list. I will have to concatinate it.
    if str(base_name)[0] == '[':
        final_base = ''
        count = 0
        for section in base_name:
            if count == 0:
                final_base += section
            else:
                final_base += "." + section
            count += 1
        base_name = final_base

    # now base name has 'media/travel/mileage_expenses/file_name (no ext)
    base_name = base_name.split('/')
    base_name = base_name[len(base_name) - 1]

    media_url = MEDIA_ROOT + url_inside_media_folder
    onlyfiles = [f for f in listdir(media_url) if isfile(join(media_url, f))]
    for i in onlyfiles:
        i_base = i
        i_base = i_base.split('_')
        i_base = i_base[: len(i_base) - 1]

        # If it has multiple periods it will return a list. I will have to concatinate it.
        if str(i_base)[0] == '[':
            final_i_base = ''
            count = 0
            for section in i_base:
                if count == 0:
                    final_i_base += section
                else:
                    final_i_base += "_" + section
                count += 1
            i_base = final_i_base

        if base_name == i_base:
            os.remove(media_url + i)


'''
Checks to see if a value is an empty string. if it is, return none. otherwise return the value
Author: Corrina Barr
:param value: the value being tested
:return: if it empty string, return none. otherwise return the value
'''


def convert_to_null_if_empty(value):
    if value == '':
        return None
    else:
        return value


# '''
# Author: Corrina Barr
# Helps update all documents dictionary.
# :param doc_name: document name that is being checked
# :param count: will be key
# :param all_post_data: all data from request.POST
# :param all_files: all data from request.FILES
# :param forms_Mileages: the forms current Daily Mileage objects
# :param mileage_week_ids: weeks ids associated with forms_Mileages
# :param all_supporting_documents: the dictionary that is goint to be updated
# :return: returns updated all_supporting_documents
# '''
# def update_all_documents_dictionary(doc_name, count, all_post_data, all_files, forms_Mileages, mileage_week_ids, all_supporting_documents):
#     print("Doc name: " + doc_name)
#     file_number = int(doc_name.split("-")[1])
#     if doc_name in all_post_data.keys():
#         # if in all_post_data then they did not upload a file or they did not upload a new file
#         file = all_post_data[doc_name]
#         # Check if there is an old file
#         if len(doc_name.split("-")) == 3:
#             # check if there is an old file:
#             for daily_mileage in forms_Mileages:
#                 if daily_mileage.dayID.weekID.pk == int(doc_name.split("-")[2]):
#                     file = daily_mileage.mileage.supportingDoc
#                     print("Line 1622")
#                     all_supporting_documents.update({file_number: file})
#         else:
#             # otherwise there is no file
#             print("Line 1626")
#             all_supporting_documents.update({file_number: None})
#         return all_supporting_documents
#     elif doc_name in all_files.keys():
#         file = all_files[doc_name]
#         # How do I find the old mileage that was associated with it so that I can delete old files?
#         #       I could put the week id at the end of the name '-' and then loop through mileage ids in forms_Mileages and check against each one
#         if str(forms_Mileages)[0] == "[":
#             for daily_mileage in forms_Mileages:
#                 if len(doc_name.split("-")) == 3:
#                     old_supporting_document = None
#                     if daily_mileage.dayID.weekID.pk == int(doc_name.split("-")[2]):
#                         old_supporting_document = daily_mileage.mileage.supportingDoc
#                     if old_supporting_document != None:
#                         remove_file_and_associated_files(old_supporting_document,
#                                                          '\media\\travel\mileage_expenses\\')
#                 else:
#                     print("no old supporting document to replace")
#         else:
#             if len(doc_name.split("-")) == 3:
#                 old_supporting_document = None
#                 if forms_Mileages.dayID.weekID.pk == int(doc_name.split("-")[2]):
#                     old_supporting_document = forms_Mileages.mileage.supportingDoc
#                 if old_supporting_document != None:
#                     remove_file_and_associated_files(old_supporting_document,
#                                                      '\media\\travel\mileage_expenses\\')
#             else:
#                 print("no old supporting document to replace")
#         all_supporting_documents.update({file_number: file})
#         print("File number: " + str(file_number))
#         print("File: " + str(file))
#         print("All supporting documents: " + str(all_supporting_documents))
#         print("Line 1646")
#         return all_supporting_documents
#     else:
#         for week_id in mileage_week_ids:
#             doc_name = "supporting_document-" + str(count) + "-" + str(week_id)
#             print("Doc name: " + doc_name)
#             if doc_name in all_post_data.keys():
#                 # if in all_post_data then they did not upload a file or they did not upload a new file
#                 file = all_post_data[doc_name]
#                 # Check if there is an old file
#                 if len(doc_name.split("-")) == 3:
#                     # check if there is an old file:
#                     for daily_mileage in forms_Mileages:
#                         if daily_mileage.dayID.weekID.pk == int(doc_name.split("-")[2]):
#                             file = daily_mileage.mileage.supportingDoc
#                             all_supporting_documents.update({file_number: file})
#                 else:
#                     # otherwise there is no file
#                     all_supporting_documents.update({file_number: None})
#                 print("Line 1665")
#                 return all_supporting_documents
#             elif doc_name in all_files.keys():
#                 file = all_files[doc_name]
#                 # How do I find the old mileage that was associated with it so that I can delete old files?
#                 #       I could put the week id at the end of the name '-' and then loop through mileage ids in forms_Mileages and check against each one
#                 for daily_mileage in forms_Mileages:
#                     if len(doc_name.split("-")) == 3:
#                         old_supporting_document = None
#                         if daily_mileage.dayID.weekID.pk == int(doc_name.split("-")[2]):
#                             old_supporting_document = daily_mileage.mileage.supportingDoc
#                         if old_supporting_document != None:
#                             remove_file_and_associated_files(old_supporting_document,
#                                                              '\media\\travel\mileage_expenses\\')
#                     else:
#                         print("no old supporting document to replace")
#                 all_supporting_documents.update({file_number: file})
#                 print("Line 1681")
#                 return all_supporting_documents
#     try:
#         all_supporting_documents.update({file_number: all_files[doc_name]})
#     except:
#         all_supporting_documents.update({file_number: None})
#     print("Line 1683")
#     return all_supporting_documents


'''
Author: Corrina Barr
This function checks objects that already exist that are associated with the TR form against values that are 
currently in the TR form to see if there are any differences. If there are differences, then it will create a 
modified TR object to show it.
:param request: the web page request
:param TR_form: the TaDetails object associated with the TR form
:param old_mileages: the sorted list of dictionaries used to display saved mileage data in the form.
:param old_p_meals: the sorted list of dictionaries used to display saved personal meal data in the form.
:param old_hotels: the sorted list of dictionaries used to display saved hotel data in the form.
:param old_transportations: the sorted list of dictionaries used to display saved transportations in the form.
:param old_b_meals: the sorted list of dictionaries used to display saved business meal data in the form.
:param old_others: the sorted list of dictionaries used to display saved other data in the form.
:param old_expenditures: the sorted list of dictionaries used to display saved expenditure data in the form.
:param p_meal_perdiem: the sorted list of dictionaries used to display saved personal meal perdiem information in the form.
:param old_business_explanations: the old business expense explanation object that is associated with the form.
:param all_post_data: dictionary version of request.POST that gets all post data, including data from multiple fields of the same name
:return: returns nothing
'''


def create_TRModifiedFields_objects(request, TR_form, old_mileages, old_p_meals, old_hotels, old_transportations,
                                    old_b_meals, old_others,
                                    old_expenditures, p_meal_perdiem, old_business_explanations, all_post_data,
                                    form_is_declined, tr_advance):
    # NOTE: If any dates are different then make sure to apply that to the start and end date fields as well

    # Mileage:
    index = 0
    for departure_from in all_post_data['departure_from']:
        check_if_date_value_changed(popup_date_name="date", sorted_list=old_mileages, all_post_data=all_post_data,
                                    TR_form=TR_form, start_week_name="week_begin", end_week_name="week_end",
                                    index=index)
        check_if_mileage_value_changed(fieldName="departure_from", TR_form=TR_form, all_post_data=all_post_data,
                                       sorted_list=old_mileages, is_a_num=False, index=index)
        check_if_mileage_value_changed(fieldName="destination_to", TR_form=TR_form, all_post_data=all_post_data,
                                       sorted_list=old_mileages, is_a_num=False, index=index)
        check_if_mileage_value_changed(fieldName="mileage", TR_form=TR_form, all_post_data=all_post_data,
                                       sorted_list=old_mileages, is_a_num=True, index=index)
        check_if_mileage_value_changed(fieldName="amount", TR_form=TR_form, all_post_data=all_post_data,
                                       sorted_list=old_mileages, is_a_num=True, index=index)
        index += 1

    # Personal Meals:
    index = 0
    for personal_breakfast in all_post_data['personal_breakfast']:
        check_if_date_value_changed(popup_date_name="personal_meal_date", sorted_list=old_p_meals,
                                    all_post_data=all_post_data,
                                    TR_form=TR_form, start_week_name="meal_week_start",
                                    end_week_name="meal_week_end", index=index)
        check_if_value_changed(fieldName="personal_breakfast", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_p_meals, is_a_num=True, index=index,
                               week_subtotal_name='meal_week_subtotal')
        check_if_value_changed(fieldName="personal_lunch", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_p_meals, is_a_num=True, index=index,
                               week_subtotal_name='meal_week_subtotal')
        check_if_value_changed(fieldName="personal_dinner", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_p_meals, is_a_num=True, index=index,
                               week_subtotal_name='meal_week_subtotal')
        index += 1

    # Personal Meal Perdiem:
    index = 0
    for perdiem in all_post_data['personal_meal_perdiem']:
        check_if_date_value_changed(popup_date_name="personal_meal_perdiem_date", sorted_list=p_meal_perdiem,
                                    all_post_data=all_post_data,
                                    TR_form=TR_form, start_week_name="meal_week_start",
                                    end_week_name="meal_week_end", index=index)
        check_if_value_changed(fieldName="personal_meal_perdiem", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=p_meal_perdiem, is_a_num=True, index=index,
                               week_subtotal_name='meal_week_subtotal')
        index += 1

    # Hotel:
    index = 0
    for hotel in all_post_data['hotel_room_change']:
        check_if_date_value_changed(popup_date_name="hotel_date", sorted_list=old_hotels,
                                    all_post_data=all_post_data,
                                    TR_form=TR_form, start_week_name="hotel_week_start",
                                    end_week_name="hotel_week_end", index=index)
        check_if_value_changed(fieldName="hotel_room_change", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_hotels, is_a_num=True, index=index,
                               week_subtotal_name='hotel_week_subtotal')
        check_if_value_changed(fieldName="hotel_laundry", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_hotels, is_a_num=True, index=index,
                               week_subtotal_name='hotel_week_subtotal')
        check_if_value_changed(fieldName="hotel_telephone", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_hotels, is_a_num=True, index=index,
                               week_subtotal_name='hotel_week_subtotal')
        check_if_value_changed(fieldName="hotel_others", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_hotels, is_a_num=True, index=index,
                               week_subtotal_name='hotel_week_subtotal')
        index += 1

    # Transportation:
    index = 0
    for transportation in all_post_data['parking']:
        check_if_date_value_changed(popup_date_name="transportation_date", sorted_list=old_transportations,
                                    all_post_data=all_post_data,
                                    TR_form=TR_form, start_week_name="transportation_week_start",
                                    end_week_name="transportation_week_end", index=index)
        check_if_value_changed(fieldName="parking", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_transportations, is_a_num=True, index=index,
                               week_subtotal_name='transportation_week_subtotal')
        check_if_value_changed(fieldName="tolls", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_transportations, is_a_num=True, index=index,
                               week_subtotal_name='transportation_week_subtotal')
        check_if_value_changed(fieldName="rides", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_transportations, is_a_num=True, index=index,
                               week_subtotal_name='transportation_week_subtotal')
        check_if_value_changed(fieldName="transportation_others", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_transportations, is_a_num=True, index=index,
                               week_subtotal_name='transportation_week_subtotal')
        index += 1

    # Business Meal:
    index = 0
    for meal in all_post_data['business_breakfast']:
        check_if_date_value_changed(popup_date_name="business_meal_date", sorted_list=old_b_meals,
                                    all_post_data=all_post_data,
                                    TR_form=TR_form, start_week_name="businessmeal_week_start",
                                    end_week_name="businessmeal_week_end", index=index)
        check_if_value_changed(fieldName="business_breakfast", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_b_meals, is_a_num=True, index=index,
                               week_subtotal_name='businessmeal_week_subtotal')
        check_if_value_changed(fieldName="business_lunch", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_b_meals, is_a_num=True, index=index,
                               week_subtotal_name='businessmeal_week_subtotal')
        check_if_value_changed(fieldName="business_dinner", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_b_meals, is_a_num=True, index=index,
                               week_subtotal_name='businessmeal_week_subtotal')
        index += 1

    # Others:
    index = 0
    for other in all_post_data['others_telephone']:
        check_if_date_value_changed(popup_date_name="others_date", TR_form=TR_form,
                                    all_post_data=all_post_data,
                                    sorted_list=old_others, start_week_name="others_week_start",
                                    end_week_name="others_week_end", index=index)
        check_if_value_changed(fieldName="others_telephone", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_others, is_a_num=True, index=index,
                               week_subtotal_name='others_week_subtotal')
        check_if_value_changed(fieldName="others_gift", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_others, is_a_num=True, index=index,
                               week_subtotal_name='others_week_subtotal')
        check_if_value_changed(fieldName="others_misc", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_others, is_a_num=True, index=index,
                               week_subtotal_name='others_week_subtotal')
        index += 1

    # Expenditure:
    index = 0
    for exp in all_post_data['expenditure_airfare']:
        check_if_date_value_changed(popup_date_name="expenditure_date", TR_form=TR_form,
                                    all_post_data=all_post_data,
                                    sorted_list=old_expenditures, start_week_name="expenditure_week_start",
                                    end_week_name="expenditure_week_end", index=index)
        check_if_value_changed(fieldName="expenditure_airfare", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_expenditures, is_a_num=True, index=index,
                               week_subtotal_name='expenditure_week_subtotal')
        check_if_value_changed(fieldName="expenditure_hotel", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_expenditures, is_a_num=True, index=index,
                               week_subtotal_name='expenditure_week_subtotal')
        check_if_value_changed(fieldName="expenditure_autorental", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_expenditures, is_a_num=True, index=index,
                               week_subtotal_name='expenditure_week_subtotal')
        check_if_value_changed(fieldName="expenditure_other", TR_form=TR_form, all_post_data=all_post_data,
                               sorted_list=old_expenditures, is_a_num=True, index=index,
                               week_subtotal_name='expenditure_week_subtotal')
        index += 1

    # Business Expense Explanation Popup:
    index = 0
    for old_business_explanation in all_post_data['business_expense_amount']:
        if request.POST.get('business_expense_amount') == '':
            exp_amount = 0
        else:
            exp_amount = all_post_data['business_expense_amount'][index]

        if exp_amount != None and old_business_explanations[index].amount != None:
            if float(exp_amount) != float(old_business_explanations[index].amount):
                TRModifiedFields().save_TRModifiedField(formID=TR_form.formID,
                                                        fieldID='business_expense_amount_saved_' + str(
                                                            old_business_explanations[index].pk),
                                                        fieldData=all_post_data['business_expense_amount'][index],
                                                        expenditureID=None, expenseID=None)
        if convert_to_null_if_empty(all_post_data['business_expense_place'][index]) != old_business_explanations[
            index].place:
            TRModifiedFields().save_TRModifiedField(formID=TR_form.formID,
                                                    fieldID='business_expense_place_saved_' + str(
                                                        old_business_explanations[index].pk),
                                                    fieldData=all_post_data['business_expense_place'][index],
                                                    expenditureID=None, expenseID=None)
        if convert_to_null_if_empty(all_post_data['business_expense_purpose'][index]) != old_business_explanations[
            index].purpose:
            TRModifiedFields().save_TRModifiedField(formID=TR_form.formID,
                                                    fieldID='business_expense_purpose_saved_' + str(
                                                        old_business_explanations[index].pk),
                                                    fieldData=all_post_data['business_expense_purpose'][index],
                                                    expenditureID=None, expenseID=None)
            TRModifiedFields().save_TRModifiedField(formID=TR_form.formID,
                                                    fieldID='bee_show_purpose_saved_' + str(
                                                        old_business_explanations[index].pk),
                                                    fieldData=all_post_data['business_expense_purpose'][index],
                                                    expenditureID=None, expenseID=None)
        if convert_to_null_if_empty(all_post_data['business_expense_detail'][index]) != old_business_explanations[
            index].detail:
            TRModifiedFields().save_TRModifiedField(formID=TR_form.formID,
                                                    fieldID='business_expense_detail_saved_' + str(
                                                        old_business_explanations[index].pk),
                                                    fieldData=all_post_data['business_expense_detail'][index],
                                                    expenditureID=None, expenseID=None)
        if convert_to_null_if_empty(all_post_data['business_expense_counterparty'][index]) != old_business_explanations[
            index].counterParty:
            TRModifiedFields().save_TRModifiedField(formID=TR_form.formID,
                                                    fieldID='business_expense_counterparty_saved_' + str(
                                                        old_business_explanations[index].pk),
                                                    fieldData=all_post_data['business_expense_counterparty'][index],
                                                    expenditureID=None, expenseID=None)
        if convert_to_null_if_empty(all_post_data['business_expense_name'][index]) != old_business_explanations[
            index].name:
            TRModifiedFields().save_TRModifiedField(formID=TR_form.formID, fieldID='business_expense_name_saved_' + str(
                old_business_explanations[index].pk),
                                                    fieldData=all_post_data['business_expense_name'][index],
                                                    expenditureID=None, expenseID=None)
        if convert_to_null_if_empty(all_post_data['business_expense_title'][index]) != old_business_explanations[
            index].title:
            TRModifiedFields().save_TRModifiedField(formID=TR_form.formID,
                                                    fieldID='business_expense_title_saved_' + str(
                                                        old_business_explanations[index].pk),
                                                    fieldData=all_post_data['business_expense_title'][index],
                                                    expenditureID=None, expenseID=None)
        index += 1
    # Deleted Fields:
    try:
        deleted_fields = all_post_data['deleted_fields']
        ##print("There are deleted fields")
    except:
        deleted_fields = None
        ##print("There are no deleted fields")
    if deleted_fields != None:
        for field in deleted_fields:
            if 'unsaved' not in field:  # Fields that were added then deleted by the modifier don't count
                ##print("Adding deleted field: " + field)
                TRModifiedFields().save_TRModifiedField(formID=TR_form.formID, fieldID=field,
                                                        fieldData='..DELETED_FIELD..',
                                                        expenditureID=None, expenseID=None)


'''
Author: Corrina Barr
This function checks old values with new values in the TR to see if a TRModifiedField object needs to be created.
Not to be used for date fields! For date fields, use check_
:param fieldName: The field's name
:param all_post_data: All Post data
:param sorted_list:
:param index: index being checked
:param is_a_num: boolean that checks if the value is a number or not
:return: returns nothing
'''


def check_if_value_changed(fieldName, sorted_list, all_post_data, TR_form, is_a_num, index, week_subtotal_name):
    old_value_exists = True
    try:
        print(str(sorted_list[index][fieldName]))
    except:
        old_value_exists = False
    if old_value_exists:
        if is_a_num:
            if all_post_data[fieldName][index] != '':
                new_data = all_post_data[fieldName][index]
            else:
                new_data = 0
            if sorted_list[index][fieldName] != None:
                old_data = sorted_list[index][fieldName]
            else:
                old_data = 0
            if float(new_data) != float(old_data):
                TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                        fieldID=all_post_data[fieldName + "-m"][index],
                                                        fieldData=all_post_data[fieldName][index],
                                                        expenseID=None, expenditureID=None)

                TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                        fieldID=week_subtotal_name + "_saved_" +
                                                                all_post_data[fieldName + "-m"][index].split("_")[len(
                                                                    all_post_data[fieldName + "-m"][index].split("_")) - 1],
                                                        fieldData=all_post_data[week_subtotal_name][math.floor(index / 7)],
                                                        expenseID=None, expenditureID=None)
        else:
            if all_post_data[fieldName][index] != sorted_list[index][fieldName]:
                TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                        fieldID=all_post_data[fieldName + "-m"][index],
                                                        fieldData=all_post_data[fieldName][index],
                                                        expenseID=None, expenditureID=None)
    else:
        if is_a_num:
            TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                    fieldID=all_post_data[fieldName + "-m"][index],
                                                    fieldData=all_post_data[fieldName][index],
                                                    expenseID=None, expenditureID=None)

            TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                    fieldID=week_subtotal_name + "_saved_" +
                                                            all_post_data[fieldName + "-m"][index].split("_")[len(
                                                                all_post_data[fieldName + "-m"][index].split(
                                                                    "_")) - 1],
                                                    fieldData=all_post_data[week_subtotal_name][
                                                        math.floor(index / 7)],
                                                    expenseID=None, expenditureID=None)
        else:
            TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                    fieldID=all_post_data[fieldName + "-m"][index],
                                                    fieldData=all_post_data[fieldName][index],
                                                    expenseID=None, expenditureID=None)


'''
Author: Corrina Barr
This function checks old values with new values in the TR to see if a TRModifiedField object needs to be created.
:param popup_date_name: The date's name that is in the popup
:param all_post_data: All Post data
:param sorted_list: he sorted list of dictionaries used to display saved data in the form.
:param index: index being checked
:param start_week_name: 
:return: returns nothing
'''


def check_if_date_value_changed(popup_date_name, start_week_name, end_week_name, sorted_list, all_post_data, TR_form,
                                index):
    from travel.models import TRModifiedFields
    print("sorted list: " + str(sorted_list))
    print("index: " + str(index))
    try:
        old_date = sorted_list[index]["date"]
    except:
        try:
            old_date = sorted_list[index]['mileage'].dayID.date
        except:
            old_date = None

    # #print("old date exists")
    if str(all_post_data[popup_date_name][index]) != str(old_date):
        # print("\nDate name: " + str(all_post_data[popup_date_name + "-m"][index]))
        # print("Comparing old date: " + str(old_date))
        # print("With new date: " + str(all_post_data[popup_date_name][index]))
        TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                fieldID=all_post_data[popup_date_name + "-m"][index],
                                                fieldData=all_post_data[popup_date_name][index],
                                                expenseID=None, expenditureID=None)
        TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                fieldID=all_post_data[start_week_name + "-m"][math.floor(index / 7)],
                                                fieldData=all_post_data[start_week_name][math.floor(index / 7)],
                                                expenseID=None, expenditureID=None)
        TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                fieldID=all_post_data[end_week_name + "-m"][math.floor(index / 7)],
                                                fieldData=all_post_data[end_week_name][math.floor(index / 7)],
                                                expenseID=None, expenditureID=None)


'''
Author: Corrina Barr
This function checks old values with new values in the TR to see if a TRModifiedField object needs to be created.
Not to be used for date fields! For date fields, use check_
:param fieldName: The field's name
:param all_post_data: All Post data
:param sorted_list:
:param is_a_num: boolean that checks if the value is a number or not
:return: returns nothing
'''


def check_if_mileage_value_changed(fieldName, sorted_list, all_post_data, TR_form, index, is_a_num):
    if all_post_data[fieldName][index] == None:
        all_post_data[fieldName][index] = 0
    existed_before = True
    try:
        print(str(sorted_list[index]))
    except:
        existed_before = False

    if existed_before:
        if fieldName == 'departure_from':
            if convert_to_null_if_empty(all_post_data[fieldName][index]) != sorted_list[index][
                "mileage"].mileage.fromLocation:
                # print("\nDeparture From: " + all_post_data[fieldName + "-m"][index])
                # print("Comparing old: " + str(sorted_list[index]["mileage"].mileage.fromLocation))
                # print("With new: " + str(all_post_data[fieldName][index]))
                TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                        fieldID=all_post_data[fieldName + "-m"][index],
                                                        fieldData=all_post_data[fieldName][index],
                                                        expenseID=None, expenditureID=None)
        elif fieldName == 'destination_to':
            if convert_to_null_if_empty(all_post_data[fieldName][index]) != sorted_list[index][
                "mileage"].mileage.toLocation:
                # print("\nDestination To: " + all_post_data[fieldName + "-m"][index])
                # print("Comparing old: " + str(sorted_list[index]["mileage"].mileage.toLocation))
                # print("With new: " + str(all_post_data[fieldName][index]))
                TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                        fieldID=all_post_data[fieldName + "-m"][index],
                                                        fieldData=all_post_data[fieldName][index],
                                                        expenseID=None, expenditureID=None)
        elif fieldName == 'mileage':
            if all_post_data[fieldName][index] == '':
                all_post_data[fieldName][index] = 0

            if sorted_list[index]["mileage"].mileage.miles == None:
                old_mileage = 0
            else:
                old_mileage = sorted_list[index]["mileage"].mileage.miles
            if float(all_post_data[fieldName][index]) != float(old_mileage):
                TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                        fieldID=all_post_data[fieldName + "-m"][index],
                                                        fieldData=all_post_data[fieldName][index],
                                                        expenseID=None, expenditureID=None)
                TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                        fieldID='weekly_mileage_saved_' +
                                                                all_post_data[fieldName + "-m"][index].split("_")[len(
                                                                    all_post_data[fieldName + "-m"][index].split("_")) - 1],
                                                        fieldData=all_post_data['weekly_mileage'][math.floor(index / 7)],
                                                        expenseID=None, expenditureID=None)
        elif fieldName == 'amount':
            if all_post_data[fieldName][index] == '':
                all_post_data[fieldName][index] = 0
            if sorted_list[index]["mileage"].mileage.amount == None:
                old_amount = 0
            else:
                old_amount = sorted_list[index]["mileage"].mileage.amount
            if float(all_post_data[fieldName][index]) != old_amount:
                TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                        fieldID=all_post_data[fieldName + "-m"][index],
                                                        fieldData=all_post_data[fieldName][index],
                                                        expenseID=None, expenditureID=None)
                TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                        fieldID="subtotal_saved_" +
                                                                all_post_data[fieldName + "-m"][index].split("_")[len(
                                                                    all_post_data[fieldName + "-m"][index].split("_")) - 1],
                                                        fieldData=all_post_data['subtotal'][math.floor(index / 7)],
                                                        expenseID=None, expenditureID=None)
    else:
        if fieldName == 'departure_from':
            TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                    fieldID=all_post_data[fieldName + "-m"][index],
                                                    fieldData=all_post_data[fieldName][index],
                                                    expenseID=None, expenditureID=None)
        elif fieldName == 'destination_to':
            TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                    fieldID=all_post_data[fieldName + "-m"][index],
                                                    fieldData=all_post_data[fieldName][index],
                                                    expenseID=None, expenditureID=None)
        elif fieldName == 'mileage':
            TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                    fieldID=all_post_data[fieldName + "-m"][index],
                                                    fieldData=all_post_data[fieldName][index],
                                                    expenseID=None, expenditureID=None)
            TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                    fieldID='weekly_mileage_saved_' +
                                                            all_post_data[fieldName + "-m"][index].split("_")[len(
                                                                all_post_data[fieldName + "-m"][index].split(
                                                                    "_")) - 1],
                                                    fieldData=all_post_data['weekly_mileage'][
                                                        math.floor(index / 7)],
                                                    expenseID=None, expenditureID=None)
        elif fieldName == 'amount':
            TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                    fieldID=all_post_data[fieldName + "-m"][index],
                                                    fieldData=all_post_data[fieldName][index],
                                                    expenseID=None, expenditureID=None)
            TRModifiedFields().save_TRModifiedField(formID=TR_form.taDetail.formID,
                                                    fieldID="subtotal_saved_" +
                                                            all_post_data[fieldName + "-m"][index].split("_")[len(
                                                                all_post_data[fieldName + "-m"][index].split(
                                                                    "_")) - 1],
                                                    fieldData=all_post_data['subtotal'][math.floor(index / 7)],
                                                    expenseID=None, expenditureID=None)






''''
Author: Corrina
Converts GL Account QueryDict into a Dictionary with the Section name being the key
:param gl_querydict: the query dictionary that is going to get converted
:return: returns a Dictionary with the Section name being the key
'''
def convert_gl_dictionary(gl_querydict):
    final_dict = {}
    for gl in gl_querydict:
        final_dict.update({gl.sectionName: gl})
    return final_dict




'''
Author: Jacob Lattergrass
'''
def parse_data_file():
    return



'''
Author: Corrina Barr
Updates travel advance information for the tr and saves in SAP format
:param request: http object
:param travel_app: travel application assciated with the TR
:param travel_advance: travel advance associated with travel_app
:param tr_advances: current travel reimbursement sap info
:param all_post_data: dict(request.POST)
:param is_completed: whether the tr is completed(submitted) or not
:param company_amount_due: int(request.POST.get('company_amount_due'))
:param tr_advance: the sap information used to display data on the form
return: if there is an error, it returns an error message. else, it returns None
'''
def update_travel_advance(request, travel_app, travel_advance, tr_advances, all_post_data, is_completed, company_amount_due, tr_advance, tr_app):
    from travel.models import AdvanceReimbursementApp
    can_update_advance = True

    error_messages = {'fatal_errors': '', 'other_errors': []}

    try:
        doc_num = request.POST.get('ta_doc_num')
    except:
        can_update_advance = False
    if can_update_advance:
        if travel_advance != None:
            try:
                adv_amount = validate_number(request.POST.get("advance_amount"), 999999999.99)
                print("advance amount: " + str(adv_amount))
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error getting advance amount from the form! Please try again or contact IT."
                return error_messages
            try:
                company_code = request.POST.get("company_code")
                if len(company_code) > 50:
                    error_messages[
                        'fatal_errors'] = "Company Code cannot exceed 50 characters!"
                    return error_messages
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error getting advance company code from the form! Please try again or contact IT."
                return error_messages
            try:
                currency = request.POST.get("currency")
                if len(currency) > 50:
                    error_messages['fatal_errors'] = "Currency mut not exceed 50 characters!"
                    return error_messages
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = "Error getting currency from the form! Please try again or contact IT."
                return error_messages
            try:
                invoice_date = request.POST.get("invoice_date")
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = "Error getting invoice date from the form! Please try again or contact IT."
                return error_messages
            try:
                cost_center_code = request.POST.get('cost_center')
                if len(cost_center_code) > 50:
                    error_messages[
                        'fatal_errors'] = "Cost Center Code must not exceed 50 characters!"
                    return error_messages
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error getting cost center code from the form! Please try again or contact IT."
                return error_messages
            try:
                ta_doc_num = request.POST.get('ta_doc_num')
                if len(ta_doc_num) > 20:
                    error_messages['fatal_errors'] = "TA Doc number must not exceed 50 characters! Please try again or contact IT."
                    return error_messages
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages['fatal_errors'] = "Error TA doc number from the form! Please try again or contact IT."
                return error_messages
            try:
                head_text = request.POST.get('head_text')
                if len(head_text) > 50:
                    error_messages[
                        'fatal_errors'] = "Head text cannot exceed 50 characters! Please try again or contact IT."
                    return error_messages
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = "Error getting head text from the form! Please try again or contact IT."
                return error_messages
            try:
                vendor_code = request.POST.get('vendor_code')
                if len(vendor_code) > 15:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages['fatal_errors'] = "Vendor Code cannot exceed 15 characters."
                    return error_messages
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = "Error getting vendor code from the form! Please try again or contact IT."
                return error_messages
            try:
                assignment = request.POST.get('assignment')
                if len(assignment) > 100:
                    error_messages['fatal_errors'] = "Assignment cannot exceed 100 characters!"
                    return error_messages
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = "Error getting assignment from the form! Please try again or contact IT."
                return error_messages
            try:
                text = request.POST.get('text')
                if len(text) > 50:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages[
                        'fatal_errors'] = "Advance text cannot exceed 50 characters."
                    return error_messages
            except:
                error_messages[
                    'fatal_errors'] = "Error getting advance text from the form! Please try again or contact IT."
                return error_messages
            try:
                invoice_num = request.POST.get('invoice_number')
                if len(invoice_num) > 25:
                    error_messages[
                        'fatal_errors'] = "Invoice number cannot exceed 25 characters."
                    return error_messages
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = "Error getting invoice number from the form! Please try again or contact IT."
                return error_messages
            try:
                date_applied = request.POST.get('invoice_date')
                if date_applied != '':
                    datetime.strptime(date_applied, '%Y-%m-%d')
                else:
                    date_applied = None
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = "Error getting date applied from the form! Please try again or contact IT."
                return error_messages

            if request.POST.get('submit_button') == 'Submit':
                date_applied = datetime.today()
            if tr_advances and tr_advances != None:
                if request.POST.get('submit_button') == 'Submit':
                    date_applied = datetime.today()
                else:
                    date_applied = tr_advance.dateApplied
                for adv in tr_advances:
                    adv.delete()
            # for first couple rows, adv amount is the combination of all costs associated with gl account.
            #       vendor code is not used

            # Get subtotals that are linked to certain GL Accounts
            # Get GL Accounts:
            gl_account_and_subtotal_names = [['gl_account', all_post_data['subtotal']],
                                             ['gl_account_p_meal', all_post_data['meal_week_subtotal']],
                                             ['gl_account_hotel', all_post_data['hotel_week_subtotal']],
                                             ['gl_account_transportation',
                                              all_post_data['transportation_week_subtotal']],
                                             ['gl_account_b_meal', all_post_data['businessmeal_week_subtotal']],
                                             ['gl_account_others', all_post_data['others_week_subtotal']],
                                             ['gl_account_expenditure', all_post_data['expenditure_week_subtotal']]]
            count = 1

            gl_account_amounts = {}
            for pair in gl_account_and_subtotal_names:
                gl_account = request.POST.get(pair[0])
                subtotal = 0.00
                for sub in pair[1]:
                    if sub == '':
                        sub = 0
                    subtotal += float(sub)
                gl_account_exists = True
                try:
                    gl_account_amounts[gl_account]
                except:
                    gl_account_exists = False
                if gl_account_exists:
                    gl_account_amounts[gl_account] += subtotal
                else:
                    gl_account_amounts.update({gl_account: subtotal})
            count = 0
            for account in gl_account_amounts:
                try:
                    AdvanceReimbursementApp().save_advance_reimbursement(form=tr_app, invoiceNo=invoice_num,
                                                                         advAmount=gl_account_amounts[account],
                                                                         costCenterCode=cost_center_code,
                                                                         profitCenter=travel_advance.profitCenter,
                                                                         assignment=assignment,
                                                                         companyCode=company_code,
                                                                         currency=currency,
                                                                         dateApplied=date_applied,
                                                                         dateApproved=datetime.today(),
                                                                         isCompleted=is_completed,
                                                                         taDocNo=ta_doc_num,
                                                                         text=text,
                                                                         headText=head_text,
                                                                         vendorCode=None,
                                                                         glCode=account)
                except:
                    print('\n'.join(traceback.format_exception(*sys.exc_info())))
                    error_messages[
                        'fatal_errors'] = "Error saving travel advance section of the TR! Please contact IT."
                    return error_messages
                count += 1

            # for last rows, gl account not used but vendor code is.
            #       first adv amount is advance amount from TA
            #       second adv amount is how much employee owes company
            try:
                AdvanceReimbursementApp().save_advance_reimbursement(form=tr_app, invoiceNo=invoice_num,
                                                                     advAmount=adv_amount,
                                                                     costCenterCode=cost_center_code,
                                                                     profitCenter=travel_advance.profitCenter,
                                                                     assignment=assignment,
                                                                     companyCode=company_code, currency=currency,
                                                                     dateApplied=date_applied, dateApproved=datetime.today(),
                                                                     isCompleted=is_completed, taDocNo=ta_doc_num,
                                                                     text=text,
                                                                     headText=head_text, vendorCode=vendor_code,
                                                                     glCode=None)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = "Error saving travel advance section of TR! Please try again or contact IT."
                return error_messages
            try:
                AdvanceReimbursementApp().save_advance_reimbursement(form=tr_app, invoiceNo=invoice_num,
                                                                     advAmount=(int(company_amount_due) * -1),
                                                                     costCenterCode=cost_center_code,
                                                                     profitCenter=travel_advance.profitCenter,
                                                                     assignment=assignment,
                                                                     companyCode=company_code, currency=currency,
                                                                     dateApplied=date_applied, dateApproved=datetime.today(),
                                                                     isCompleted=is_completed, taDocNo=ta_doc_num,
                                                                     text=text,
                                                                     headText=head_text, vendorCode=vendor_code,
                                                                     glCode=None)
            except:
                print('\n'.join(traceback.format_exception(*sys.exc_info())))
                error_messages[
                    'fatal_errors'] = "Error saving travel advance section of the TR! Please try again or contact IT."
                return error_messages
    return error_messages


'''
Author: Corrina Barr
checks if value is empty string or null
:param value: value being checked
:return: true if it is "" or None, false if it is not
'''
def is_nothing(value):
    if value == "" or value == None:
        return True
    else:
        return False
