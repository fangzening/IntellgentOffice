// Used to be on html but now on js
    function removeNone(){
        var inputs = document.querySelectorAll("input");
        for (let j = 0; j < inputs.length; j++) {
            if (inputs[j].value === 'None'){
                inputs[j].value = '';
            }
        }
    }



    // instantiates tr advance values
    function get_tr_advance_values(ta_header, ta_invoice, ta_assignment, ta_item_text, cost_center, ta_doc_num, users_vendorcode, ta_currency, ta_budget_sc_code, ta_advance_amount, ta_company_code) {
        document.getElementById("head_text").value = "RIEMB. " + ta_header.replace('TRAVEL ADV.', 'TER');

        // invoice:
        var invoice_value = ta_item_text.split("-")[ta_header.split("-").length - 1].replace(' TRAVEL ADVANCE', '').replace("-", "") + "-TER";
        var invoice_values = invoice_value.split('/');
        // clear invoice value
        invoice_value = "";
        for (let j = 0; j < invoice_values.length; j++) {
            if (invoice_values[j].length < 2){
                invoice_values[j] = "0" + invoice_values[j];
            }
            invoice_value += invoice_values[j];
        }

        document.getElementById('invoice_number').value = invoice_value;
        document.getElementById('assignment').value = ta_assignment;
        document.getElementById('text').value = ta_item_text;
        document.getElementById('cost_center').value = ta_budget_sc_code;
        document.getElementById('vendor_code').value = users_vendorcode;
        document.getElementById('currency').value = ta_currency;
        document.getElementById('advance_amount').value = ta_advance_amount;
        document.getElementById('company_code').value = ta_company_code;

        if(ta_doc_num !== "" && ta_doc_num !== "None"){
            document.getElementById('ta_doc_num').value = ta_doc_num;
        }
        else{
            document.getElementById('ta_doc_num').value = "0"
        }

    }




// on load figure out how many mileage rows there are
    // and set that value to the hidden field number_of_mileage_weeks

    var departure_froms = document.getElementsByName("departure_from");
    var number_of_departure_froms = departure_froms.length;
    var number_of_weeks = Math.floor(number_of_departure_froms/7);

    //document.getElementById("number_of_mileage_weeks").value = number_of_weeks;
    //console.log("number_of_mileage_weeks: " + document.getElementById("number_of_mileage_weeks").value.toString());

    //add new table
    function addRow(tableID) {

        var table = document.getElementById(tableID);

        var rowCount = table.row.length;
        var row = table.insertRow(rowCount);

        var colCount = table.row[0].cells.length;

        for (var i = 0; i < colCount; i++) {
            var newcell = row.insertCell(i);

            newcell.innerHTML = table.row[0].cells[i].innerHTML;

            //newcell.childNodes[0].id += ("_" + rowCount.toString()); HEY JOSUA: I made this but then I realized id doesn't matter to me, you can uncomment it if you find it useful, it works.

            //alert(newcell.childNodes);
            switch (newcell.childNodes[0].type) {
                case "text":
                    newcell.childNodes[0].value = "";
                    break;
                case "checkbox":
                    newcell.childNodes[0].checked = false;
                    break;
                case "select-one":
                    newcell.childNodes[0].selectedIndex = 0;
                    break;
            }
        }
    }

    //delete the added table using a checkbox
    function deleteRow(tableID) {
        //try {
            var table = document.getElementById(tableID);
            var rowCount = table.rows.length;


            for (var i = 0; i < rowCount; i++) {
                var row = table.rows[i];
                var chkbox = row.cells[0].childNodes[0];
                var startDate = row.cells[1].childNodes[0];
                var startDateID = startDate.id.toString();
                if (null != chkbox && true === chkbox.checked) {
                    if (rowCount <= 1) {
                        alert("Cannot delete all the rows.");
                        break;
                    }
                    //console.log("Start Date ID: " + startDateID);

                    // Loop through all elements of row but first and last (because they are buttons and checkboxes) and create a deleted_fields object
                    for (let j = 1; j < row.cells.length - 1; j++) {
                        var field_being_deleted = row.cells[j].childNodes[0];
                        //console.log("field created: " + field_being_deleted.id.toString());
                        $('#re_form').append("<input hidden readonly name='deleted_fields' value='"+ field_being_deleted.id +"'>");
                    }
                    table.deleteRow(i);
                    rowCount--;
                    i--;

                    //check which popup matches the start date id
                    var start_date_split =  startDateID.split("_");     //Start date id split into substrings by "_"
                    var start_date_type = "";   //First Part of start date before the saved/unsaved_weekID
                    var popup_type = "";        //First Part of Popup ID before the saved/unsaved_weekID
                    var popup_specifics = "";   //Start date specifics and popups specifics are the same thing

                    popup_specifics = start_date_split[start_date_split.length - 2] + start_date_split[start_date_split.length - 1];
                    //console.log("Popup Specifics: " + popup_specifics.toString());

                    for (let j = 0; j < start_date_split.length - 2; j++) {
                        start_date_type += start_date_split[j];
                    }

                    console.log("Start Date Type: " + start_date_type.toString());

                    //Get first part of popup name based on start date type
                    if (start_date_type === 'weekbegin'){
                        popup_type = "Travel_Modal";
                        console.log("setting to: " + popup_type);
                    }
                    else if (start_date_type === 'mealweekstart'){
                        popup_type="Meal_Expense_Modal";
                    }
                    else if (start_date_type === 'hotelweekstart'){
                        popup_type="Hotel_Expense_Modal";
                    }
                    else if (start_date_type === 'othersweekstart'){
                        popup_type="Others_Expense_Modal";
                    }
                    else if (start_date_type === 'expenditureweekstart'){
                        popup_type="Expenditure_Expense_Modal";
                    }
                    else if (start_date_type === 'businessmealweekstart'){
                        popup_type="BusinessMeal_Expense_Modal";
                    }
                    else if (start_date_type === "beeshowpurpose"){
                        popup_type = "Bee_Modal";
                    }
                    else{
                        popup_type="Transportation_Expense_Modal";
                        console.log("setting to: " + popup_type);
                    }

                    var popup_id = popup_type + "_" + start_date_split[start_date_split.length - 2] + "_" + start_date_split[start_date_split.length - 1];
                    console.log("Popup ID: " + popup_id);

                    // Update mileage supporting document weeks:
                    if (start_date_type ==='weekbegin'){
                        // 1: Get number after "-" in the supporting doc id which is inside the popup
                        var elements_in_popup = document.getElementById(popup_id).querySelectorAll("*");
                        // If it was a saved week the element index will be 114.
                        //       If it is unsaved it will be 105
                        //       If element id at 105 does not exist check element at 114
                        if (elements_in_popup[105].id === '' || elements_in_popup[105].id === null){
                            var document_id = elements_in_popup[114].id.toString();
                        }
                        else{
                            var document_id = elements_in_popup[105].id.toString();
                        }
                        var document_number = parseInt(document_id.split("-")[1]);

                        // 2: Get all elements whose id starts with 'supporting_document' and 'old_supporting_document'
                        var supporting_document_elements = document.querySelectorAll('*[id^="supporting_document"]');
                        var old_supporting_document_elements = document.querySelectorAll('*[id^="old_supporting_document"]');

                        // update names and ids where their number is greater than the row deleted
                        for (let j = 0; j < supporting_document_elements.length; j++) {
                            var current_doc_num = parseInt(supporting_document_elements[j].id.toString().split("-")[1]);
                            if (current_doc_num > document_number){
                                current_doc_num -= 1;
                                var length_of_current_substring = supporting_document_elements[j].id.toString().split("-").length.toString();
                                if (length_of_current_substring === 2){
                                    supporting_document_elements[j].name = "supporting_document-" + current_doc_num.toString();
                                    supporting_document_elements[j].id = "supporting_document-" + current_doc_num.toString();
                                    old_supporting_document_elements[j].name = "old_supporting_document-" + current_doc_num.toString();
                                    old_supporting_document_elements[j].id = "old_supporting_document-" + current_doc_num.toString();
                                }
                                else{
                                    var mileage_id = supporting_document_elements[j].id.toString().split("-")[2];
                                    supporting_document_elements[j].name = "supporting_document-" + current_doc_num.toString() + "-" + mileage_id;
                                    supporting_document_elements[j].id = "supporting_document-" + current_doc_num.toString() + "-" + mileage_id;
                                    old_supporting_document_elements[j].name = "old_supporting_document-" + current_doc_num.toString() + "-" + mileage_id;
                                    old_supporting_document_elements[j].id = "old_supporting_document-" + current_doc_num.toString() + "-" + mileage_id;
                                }
                            }
                            //console.log("Supporting Document: " + supporting_document_elements[j].id.toString());
                        }

                        // update number of mileage weeks
                        document.getElementById("number_of_mileage_weeks").value = parseInt(document.getElementById("number_of_mileage_weeks").value) - 1;
                    }

                    if (popup_id.includes('unsaved') === false){
                        // Get all input fields within the popup and add them to deleted fields:
                        console.log("popup id: " + popup_id.toString());
                        var popup_fields_to_delete =  document.getElementById(popup_id).querySelectorAll("input");
                        //console.log("all deleted fields to make: " + popup_fields_to_delete.toString());
                        for (let j = 0; j < popup_fields_to_delete.length; j++) {
                            //console.log("field created: " + popup_fields_to_delete[j].id.toString());
                            $('#re_form').append("<input hidden readonly name='deleted_fields' value='"+ popup_fields_to_delete[j].id +"'>");
                        }
                    }
                    document.getElementById(popup_id).innerHTML = ""; //removes all fields in the popup that could mess with the post
                }
            }
            get_sum();
        //} catch (e) {
        //    alert(e);
        //}
    }

    function submit() {
        var table = document.getElementById(tableID);
        var rowCount = table.rows.length;
    }



    // check box auth
    function disableSubmit() {
        document.getElementById("accept").disabled = true;
    }

    function activateButton(element) {

        if (element.checked) {
            document.getElementById("accept").disabled = false;
        } else {
            document.getElementById("accept").disabled = true;
        }

    }



    var rowIndex = 0;

    $("#addnew").on('click', function () {

        rowIndex++;

        var start_id = "week_begin_unsaved_" + rowIndex;
        var end_id = "week_end_unsaved_" + rowIndex;

        var newRow = '<tr><td colspan="1"><input id="row_checkbox_mileage_unsaved_' + rowIndex + '" name="row_checkbox' + rowIndex + '" type="checkbox" /></td>"' +
            '<td><input id= "' + start_id +'" name="week_begin" placeholder="Date' + rowIndex + '" type="date" class="form-control" onfocusout="set_week(\'' +start_id + '\'' + ', ' + '\'' + end_id + '\', \'date\', \'\')"></td>"' +
            '<td><input id= "' + end_id + '" name="week_end" placeholder="Date' + rowIndex + '" type="date" class="form-control" readonly></td>"' +
            '<td><input name="weekly_mileage' + '" id="weekly_mileage_unsaved_' + rowIndex + '" placeholder="Mileage' + rowIndex + ' " data-toggle="modal" data-target="#Travel_Modal_unsaved_' + rowIndex +'" readonly type="text" class="form-control subtotal"></td>" ' +
            '<td><input name="subtotal' + '" id="subtotal_unsaved_' + rowIndex + '" placeholder="SubTotal' + rowIndex + ' " data-toggle="modal" data-target="#Travel_Modal_unsaved_' + rowIndex +'" readonly type="text" class="form-control subtotal" readonly ></td>" ' +
            '<td><input name="view' + '"value="Edit ' + rowIndex + '" id="view_unsaved_' + rowIndex + '" placeholder="Edit" data-toggle="modal" data-target="#Travel_Modal_unsaved_' + rowIndex + '" type="button" class="form-control btn btn-outline-primary"></td>" ' +
            '</tr>';

        if ($("#mileage_information > tbody > tr").is("*"))
            $("#mileage_information > tbody > tr:last").after(newRow)
        else $("#mileage_information > tbody").append(newRow)

        var column_titles = ['DATE', 'DEPARTURE', 'DESTINATION', 'MILEAGE', 'AMOUNT'];
        var column_field_names = ['date', 'departure_from', 'destination_to', 'mileage', 'amount'];

        create_section_popup(rowIndex, column_titles, column_field_names, 'mileage_popup_subtotal_' + rowIndex, false, "Travel_Modal", "mileage_popups", true, '', "Mileage Expenses");
    });




    var rowIndex = 0;

    $("#addnew_meal").on('click', function () {

        rowIndex++;

        var start_id = "meal_week_start_unsaved_" + rowIndex;
        var end_id = "meal_week_end_unsaved_" + rowIndex;
        var base_date = "personal_meal_date";

        var newRow = '<tr><td colspan="1"><input id="row_checkbox_personal_meal_unsaved_' + rowIndex + '" name="row_checkbox' + rowIndex + ' " type="checkbox" /></td>"' +
            '<td><input name= "meal_week_start' + '" id="' + start_id + '" placeholder="Date' + rowIndex + ' " type="date" class="form-control" onfocusout="set_week(\'' +start_id + '\'' + ', ' + '\'' + end_id+ '\', \'' + base_date + '\', \'personal_meal_perdiem_date\')"></td>"' +
            '<td><input name= "meal_week_end' + '" id="' + end_id + '" placeholder="Date' + rowIndex + ' " type="date" class="form-control" readonly></td>"' +
            '<td><input name="meal_week_subtotal' + '" id="meal_week_subtotal_unsaved_' + rowIndex + '" placeholder="SubTotal' + rowIndex + ' " data-toggle="modal" data-target="#Meal_Expense_Modal_unsaved_' + rowIndex + '" readonly type="text" class="form-control subtotal" readonly></td>" ' +
            '<td><input name="view' + '"value="Edit ' + rowIndex + '" id="view_unsaved_' + rowIndex + '" placeholder="Edit' + rowIndex + ' " data-toggle="modal" data-target="#Meal_Expense_Modal_unsaved_' + rowIndex + '" type="button" class="form-control btn btn-outline-primary"></td>" ' +

            '</tr>';

        if ($("#expense_meal_table > tbody > tr").is("*"))
            $("#expense_meal_table > tbody > tr:last").after(newRow)
        else $("#expense_meal_table > tbody").append(newRow)

        column_titles = ['BREAKFAST', 'LUNCH', 'DINNER', 'DATE'];
        column_field_names = ['personal_breakfast', 'personal_lunch', 'personal_dinner', 'personal_meal_date'];

        create_section_popup(rowIndex, column_titles, column_field_names, 'personal_meal_popup_subtotal_' + rowIndex, true, "Meal_Expense_Modal", "personal_meal_popups", false, "personal_meal_perdiem", "Personal Meal Expenses");
    });



    var rowIndex = 0;

    $("#addnew_hotel").on('click', function () {

        rowIndex++;

        var start_id = "hotel_week_start_unsaved_" + rowIndex;
        var end_id = "hotel_week_end_unsaved_" + rowIndex;


        var newRow = '<tr><td colspan="1"><input id="row_checkbox_hotel_unsaved_' + rowIndex + '" name="row_checkbox' + rowIndex + ' " type="checkbox" /></td>"' +
            '<td><input name= "hotel_week_start' + '" id="' + start_id + '" placeholder="Date' + rowIndex + ' " type="date" class="form-control" onfocusout="set_week(\'' +start_id + '\'' + ', ' + '\'' + end_id + '\', \'hotel_date\', \'\')"></td>"' +
            '<td><input name= "hotel_week_end' + '" id="' + end_id + '"placeholder="Date' + rowIndex + ' " type="date" class="form-control" readonly></td>"' +
            '<td><input name="hotel_week_subtotal' + '" id="hotel_week_subtotal_unsaved_' + rowIndex + '" placeholder="SubTotal' + rowIndex + ' " data-toggle="modal" data-target="#Hotel_Expense_Modal_unsaved_' + rowIndex +'" readonly type="text" class="form-control subtotal" readonly></td>" ' +
            '<td><input name="view' + '"value="Edit ' + rowIndex + '" id="view2' + rowIndex + '" placeholder="Edit' + rowIndex + ' " data-toggle="modal" data-target="#Hotel_Expense_Modal_unsaved_' + rowIndex +'" type="button" class="form-control btn btn-outline-primary"></td>" ' +

            '</tr>';

        if ($("#hotel_expense_table > tbody > tr").is("*"))
            $("#hotel_expense_table > tbody > tr:last").after(newRow)
        else $("#hotel_expense_table > tbody").append(newRow)

        var popup_column_headers = ['HOTEL ROOM CHARGE', 'LAUNDRY', 'TELEPHONE', 'OTHERS', 'DATE'];
        var column_field_names = ['hotel_room_change', 'hotel_laundry', 'hotel_telephone', 'hotel_others', 'hotel_date'];
        create_section_popup(rowIndex, popup_column_headers, column_field_names, 'hotel_week_subtotal', false, 'Hotel_Expense_Modal', 'hotel_popups', false, '', "Hotel Expenses")
    });




    var rowIndex = 0;

    $("#addnew_transportation").on('click', function () {

        rowIndex++;

        var start_id = "transportation_week_start_unsaved_" + rowIndex;
        var end_id = 'transportation_week_end_unsaved_' + rowIndex;

        var newRow = '<tr><td colspan="1"><input id="row_checkbox_transportation_unsaved_' + rowIndex + ' " name="row_checkbox' + rowIndex + ' " type="checkbox" /></td>"' +
            '<td><input name= "transportation_week_start' + '" id="' + start_id +'"placeholder="Date' + rowIndex + ' " type="date" class="form-control" onfocusout="set_week(\'' +start_id + '\'' + ', ' + '\'' + end_id + '\', \'transportation_date\', \'\')"></td>"' +
            '<td><input name= "transportation_week_end' + '" id="' + end_id +'"placeholder="Date' + rowIndex + ' " type="date" class="form-control" readonly></td>"' +
            '<td><input name="transportation_week_subtotal' + '" id="transportation_week_subtotal_unsaved_' + rowIndex + ' " placeholder="SubTotal' + rowIndex + ' " data-toggle="modal" data-target="#Transportation_Expense_Modal_unsaved_' + rowIndex +'" readonly type="text" class="form-control subtotal"></td>" ' +
            '<td><input name="view' + '"value="Edit ' + rowIndex + '" id="view2' + rowIndex + ' " placeholder="Edit' + rowIndex + ' " data-toggle="modal" data-target="#Transportation_Expense_Modal_unsaved_' + rowIndex + '" type="button" class="form-control btn btn-outline-primary"></td>" ' +
            '</tr>';

        if ($("#transportation_expense_table > tbody > tr").is("*"))
            $("#transportation_expense_table > tbody > tr:last").after(newRow)
        else $("#transportation_expense_table > tbody").append(newRow)

        var popup_column_headers = ['PARKING', 'TOLLS', 'RIDES', 'OTHERS', 'DATE'];
        var column_field_names = ['parking', 'tolls', 'rides', 'transportation_others', 'transportation_date'];
        create_section_popup(rowIndex, popup_column_headers, column_field_names, 'transportation_subtotal', false, 'Transportation_Expense_Modal', 'transportation_popups', false, '', "Transportation Expenses")
    });




    var rowIndex = 0;

    $("#addnew_business_meal").on('click', function () {

        rowIndex++;

        var start_id = "businessmeal_week_start_unsaved_" + rowIndex;
        var end_id = "businessmeal_week_end_unsaved_" + rowIndex;

        var newRow = '<tr><td colspan="1"><input id="row_checkbox_business_meal_unsaved_' + rowIndex + ' " name="row_checkbox' + rowIndex + ' " type="checkbox" /></td>"' +
            '<td><input name= "businessmeal_week_start' + '" id="' + start_id + '"placeholder="Date' + rowIndex + ' " type="date" class="form-control" onfocusout="set_week(\'' +start_id + '\'' + ', ' + '\'' + end_id+ '\', \'business_meal_date\', \'\')"></td>"' +
            '<td><input name= "businessmeal_week_end' + '" id="' + end_id + '"placeholder="Date' + rowIndex + ' " type="date" class="form-control" readonly></td>"' +
            '<td><input name="businessmeal_week_subtotal' + '" id="businessmeal_week_subtotal_unsaved_' + rowIndex + ' " placeholder="SubTotal' + rowIndex + ' " data-toggle="modal" data-target="#BusinessMeal_Expense_Modal_unsaved_' + rowIndex + '" readonly type="text" class="form-control subtotal"></td>" ' +
            '<td><input name="view' + '"value="Edit ' + rowIndex + '" id="view2' + rowIndex + ' " placeholder="Edit' + rowIndex + ' " data-toggle="modal" data-target="#BusinessMeal_Expense_Modal_unsaved_' + rowIndex + '" type="button" class="form-control btn btn-outline-primary"></td>" ' +

            '</tr>';

        if ($("#business_meal_table > tbody > tr").is("*"))
            $("#business_meal_table > tbody > tr:last").after(newRow)
        else $("#business_meal_table > tbody").append(newRow)

        var popup_column_headers = ['BREAKFAST', 'LUNCH', 'DINNER', 'DATE'];
        var column_field_names = ['business_breakfast', 'business_lunch', 'business_dinner', 'business_meal_date'];
        create_section_popup(rowIndex, popup_column_headers, column_field_names, 'business_meal_subtotal', false, 'BusinessMeal_Expense_Modal', 'business_meal_popups', false, '', "Business Meal Expenses")
    });

    var rowIndex = 0;

    $("#addnew_others").on('click', function () {

        rowIndex++;

        var start_id = "others_week_start_unsaved_" + rowIndex;
        var end_id = "others_week_end_unsaved_" + rowIndex;

        var newRow = '<tr><td colspan="1"><input id="row_checkbox_others_unsaved_' + rowIndex + ' " name="row_checkbox' + rowIndex + ' " type="checkbox" /></td>"' +
            '<td><input name= "others_week_start' + '" id="' + start_id + '"placeholder="Date' + rowIndex + ' " type="date" class="form-control" onfocusout="set_week(\'' +start_id + '\'' + ', ' + '\'' + end_id+ '\', \'others_date\', \'\')"></td>"' +
            '<td><input name= "others_week_end' + '" id="' + end_id + '"placeholder="Date' + rowIndex + ' " type="date" class="form-control" readonly></td>"' +
            '<td><input name="others_week_subtotal' + '" id="others_week_subtotal_unsaved_' + rowIndex + ' " placeholder="SubTotal' + rowIndex + ' " data-toggle="modal" data-target="#Others_Expense_Modal_unsaved_'+ rowIndex +'" readonly type="text" class="form-control subtotal"></td>" ' +
            '<td><input name="view' + '"value="Edit ' + rowIndex + '" id="view2' + rowIndex + ' " placeholder="Edit' + rowIndex + ' " data-toggle="modal" data-target="#Others_Expense_Modal_unsaved_'+ rowIndex +'" type="button" class="form-control btn btn-outline-primary"></td>" ' +

            '</tr>';

        if ($("#business_others_table > tbody > tr").is("*"))
            $("#business_others_table > tbody > tr:last").after(newRow)
        else $("#business_others_table > tbody").append(newRow)

        var popup_column_headers = ['TELEPHONE OR FAX', 'GIFT/ENTERTAINMENT', 'MISCELLANEOUS', 'DATE'];
        var column_field_names = ['others_telephone', 'others_gift', 'others_misc', 'others_date'];
        create_section_popup(rowIndex, popup_column_headers, column_field_names, 'others_week_subtotal', false, 'Others_Expense_Modal', 'other_popups', false, '', "Other Expenses");
    });

    var rowIndex = 0;

    $("#addnew_bee").on('click', function () {

        rowIndex++;

        var newRow = "<tr>\n" +
            "                                                                <td><input type=\"checkbox\" id=\"row_checkbox_other_unsaved_" + rowIndex +" \"></td>\n" +
            "                                                                <td colspan=\"5\"><input type=\"text\" class=\"form-control subtotal\"\n" +
            "                                                                           name=\"bee_show_purpose\"\n" +
            "                                                                           id=\"bee_show_purpose_unsaved_" + rowIndex +"\"\n" +
            "                                                                           placeholder=\"Purpose of Expense\"\n" +
            "                                                                           data-toggle=\"modal\"\n" +
            "                                                                           data-target=\"#Bee_Modal_unsaved_"+ rowIndex + "\"\n" +
            "                                                                           readonly></td>\n" +
            "                                                                <td colspan=\"1\"><input type=\"button\" width=\"48\"\n" +
            "                                                                               class=\"form-control btn btn-outline-primary\"\n" +
            "                                                                               name=\"view\" value=\"Edit\"\n" +
            "                                                                               id=\"view\" data-toggle=\"modal\"\n" +
            "                                                                               data-target=\"#Bee_Modal_unsaved_" + rowIndex + "\">\n" +
            "                                                                </td>\n" +
            "                                                            </tr>";

        if ($("#bee_table > tbody > tr").is("*"))
            $("#bee_table > tbody > tr:last").after(newRow)
        else $("#bee_table > tbody").append(newRow)

        create_bee_popup('_unsaved_' + rowIndex);
    });



    var rowIndex = 0;

    $("#addnew_expenditure").on('click', function () {

        rowIndex++;

        var start_id = "expenditure_week_start_unsaved_" + rowIndex;
        var end_id = "expenditure_week_end_unsaved_" + rowIndex;

        var newRow = '<tr><td colspan="1"><input id="row_checkbox_expenditure_unsaved_' + rowIndex + '" name="row_checkbox' + rowIndex + ' " type="checkbox" /></td>"' +
            '<td><input name= "expenditure_week_start' + '" id="' + start_id + '"placeholder="Date' + rowIndex + ' " type="date" class="form-control" onfocusout="set_week(\'' +start_id + '\'' + ', ' + '\'' + end_id+ '\', \'expenditure_date\', \'\')"></td>"' +
            '<td><input name= "expenditure_week_end' + '" id="' + end_id + '"placeholder="Date' + rowIndex + ' " type="date" class="form-control" readonly></td>"' +
            '<td><input name="expenditure_week_subtotal' + '" id="expenditure_week_subtotal_unsaved_' + rowIndex + '" placeholder="SubTotal' + rowIndex + ' " data-toggle="modal" data-target="#Expenditure_Expense_Modal_unsaved_' + rowIndex +'" readonly type="text" class="form-control subtotal"></td>" ' +
            '<td><input name="view' + '"value="Edit ' + rowIndex + '" id="view2' + rowIndex + ' " placeholder="Edit' + rowIndex + ' " data-toggle="modal" data-target="#Expenditure_Expense_Modal_unsaved_'+ rowIndex +'" type="button" class="form-control btn btn-outline-primary"></td>" ' +

            '</tr>';

        if ($("#expenditure_table > tbody > tr").is("*"))
            $("#expenditure_table > tbody > tr:last").after(newRow)
        else $("#expenditure_table > tbody").append(newRow)

        var popup_column_headers = ['AIRLINE FARE', 'HOTEL', 'AUTO RENTALS', 'OTHERS', 'DATE'];
        var column_field_names = ['expenditure_airfare', 'expenditure_hotel', 'expenditure_autorental', 'expenditure_other', 'expenditure_date'];
        create_section_popup(rowIndex, popup_column_headers, column_field_names, 'expenditure_week_subtotal', false, 'Expenditure_Expense_Modal', 'expenditure_popups', false, '', "Expenditures");

    });




//     <!-- Corrina's script that makes sure user selects a Monday for start date--->
// <!-- It also sets end date and days for the week in the popup --------------->
function set_week(start_id, end_id, date_name, perdiem_name){
    //console.log("\n\n***********************************START SET WEEK");
    if(check_if_start_date_already_exists_in_section(start_id, end_id) === false){
        var start_date_field = document.getElementById(start_id);
        var end_date_field = document.getElementById(end_id);

        if (start_date_field.value !== 'None' || start_date_field.value !== '' || start_date_field.value !== null){
            var start_date = new Date(start_date_field.value);
        }
        else{
            var start_date = new Date();
        }

        if(end_date_field.value !== 'None' || end_date_field.value !== '' || end_date_field.value !== null){
            var end_date = new Date(end_date_field.value.toString());
        }
        else{
            var end_date = new Date();
        }

        if (start_date_field.value !== 'None' || start_date_field.value !== '' || start_date_field.value !== null){
            // check if day is on a Monday
            //console.log("HTML Value: " + start_date_field.value.toString());
           // console.log("******Start Date: " + start_date.toString());
            //console.log("Start Date day: " + start_date.getDay().toString());
            if (start_date.getDay() === 0) {
                start_date.setDate(start_date.getDate() + 1);
                //var new_end_date = new Date();
                //new_end_date.setDate(start_date.getDate() + 7);
                //console.log("*****New End Date: " + new_end_date.toDateString());

                //Use this to compare to end time
                var start_m = start_date.getMonth();
                var start_d = start_date.getDate();
                var start_y = start_date.getFullYear();

                var this_end_date = new Date();

                //Initailize this_end_date
                this_end_date.setFullYear(start_date.getFullYear());
                this_end_date.setMonth(start_date.getMonth());

                //change date
                this_end_date.setDate(start_date.getDate() + 6);
                //console.log("End date: " + this_end_date.toString());

                var dd = this_end_date.getDate();
                var dd_str = dd.toString();
                if (dd_str.length === 1){
                    dd_str = "0" + dd_str;
                }

                var mm = this_end_date.getMonth();
                //console.log("end date mm before: " + mm.toString());
                //console.log("start_m: " + start_m.toString());
                //console.log("end date dd before: " + dd.toString());
                //console.log("start_d: " + start_d.toString());
                while (mm < start_m + 1 || (mm === start_m + 1 && dd < start_d)){
                    mm += 1;
                }
                if(mm > 12){
                    mm = 1;
                }
                //console.log("***end date mm after: " + mm.toString());
                var mm_str = mm.toString();
                if (mm_str.length === 1){
                    mm_str = "0" + mm_str;
                }


                var yyyy = this_end_date.getFullYear();
                //console.log("***start_y: " + start_y.toString());
                //console.log("End date year before: " + yyyy.toString());
                while (yyyy < start_y || (yyyy === start_y && mm < start_m)){
                    yyyy += 1;
                }
                //console.log("End date year after: " + yyyy.toString());

                //COMPLETE END DATE:
                this_end_date.setFullYear(yyyy, mm, dd);


                var yyyy_str = yyyy.toString();
                end_date_field.value = (yyyy_str + "-" + mm_str + "-" + dd_str);

                var monday;
                monday = new Date();
                monday.setDate(start_date.getDate());
            }
            else{
                alert("Week start date must be a Monday!");
                var day = start_date.getDay();
                //console.log("***DAY: " + day.toString());
                var monday;
                monday = new Date();
                monday.setDate(start_date.getDate() - day + 1);
                monday.setMonth(start_date.getMonth());
                monday.setFullYear(start_date.getFullYear());
                //console.log("***MONDAY: " + monday.toString());

                //Start Date
                var dd = monday.getDate();
                var dd_str = dd.toString();
                if (dd_str.length === 1){
                    dd_str = "0" + dd_str;
                }
                //console.log("Monday Date Day: " + dd.toString());

                var mm = monday.getMonth()+1;
                while (mm > start_m + 1 || (mm === start_m + 1 && dd > start_d)){
                    mm -= 1;
                }
                year_go_down = false;
                if(mm < 1){
                    mm = 12;
                    year_go_down = true
                }
                var mm_str = mm.toString();
                if (mm_str.length === 1){
                    mm_str = "0" + mm_str;
                }
                //console.log("Monday Month: " + mm.toString());
                monday.setMonth(mm-1);


                var yyyy = monday.getFullYear();
                if (year_go_down){
                    yyyy -= 1;
                }
                monday.setFullYear(yyyy-1, mm, dd);
                var yyyy_str = yyyy.toString();
                start_date_field.value = (yyyy_str + "-" + mm_str + "-" + dd_str);
                ////console.log("Monday year: " + yyyy.toString());

                check_if_start_date_already_exists_in_section(start_date_field.id, end_id);

                //Use this to compare to end time
                var start_m = mm;
                var start_d = dd;
                var start_y = yyyy;

                //End Date
                var this_end_date = new Date();

                //Initailize this_end_date
                this_end_date.setFullYear(monday.getFullYear());
                this_end_date.setMonth(monday.getMonth());
                //change date
                this_end_date.setDate(monday.getDate() + 7);
                //console.log("End date: " + this_end_date.toString());

                var dd = this_end_date.getDate();
                var dd_str = dd.toString();
                if (dd_str.length === 1){
                    dd_str = "0" + dd_str;
                }

                var mm = monday.getMonth();
                //console.log("end date mm before: " + mm.toString());
                //console.log("start_m: " + start_m.toString());
                //console.log("end date dd before: " + dd.toString());
                //console.log("start_d: " + start_d.toString());
                while (mm < start_m || (mm === start_m && dd < start_d)){
                    mm += 1;
                }
                if(mm > 12){
                    mm = 1;
                }
                //console.log("***end date mm after: " + mm.toString());
                var mm_str = mm.toString();
                if (mm_str.length === 1){
                    mm_str = "0" + mm_str;
                }

                var yyyy = this_end_date.getFullYear();
                //console.log("***start_y: " + start_y.toString());
                //console.log("End date year before: " + yyyy.toString());
                while (yyyy < start_y || (yyyy === start_y && mm < start_m)){
                    yyyy += 1;
                }
                //console.log("End date year after: " + yyyy.toString());

                //COMPLETE END DATE:
                this_end_date.setFullYear(yyyy, mm, dd);

                var yyyy_str = yyyy.toString();
                end_date_field.value = (yyyy_str + "-" + mm_str + "-" + dd_str);
            }

            // SECTION fill in popup dates:
            var dates_for_whole_section = document.getElementsByName(date_name);
            fill_popup_dates(dates_for_whole_section, start_date_field);

            //SECTION PER DIEM
            try{
                var perdiem_dates = document.getElementsByName(perdiem_name);
                fill_popup_dates(perdiem_dates, start_date_field);
                }
            catch (e) {
                //console.log("No perdiem dates")
            }

        }
    }
}



function fill_popup_dates(dates_for_whole_section, start_date_field){
    var false_monday = new Date(start_date_field.value);
    var start_id = start_date_field.id;

    monday = new Date(false_monday);
    monday.setDate(monday.getDate() + 1);

    if(monday.getDate() < false_monday.getDate()) {
        monday.setMonth(false_monday.getMonth() + 1);
    }

    if (monday.getMonth() > 11){
        monday.setMonth(0);
        monday.setFullYear(false_monday.getFullYear() + 1, monday.getMonth(), monday.getDate());
    }

    for (let j = 0; j < dates_for_whole_section.length + 1; j++) {
        //console.log("Dates for whole section: " +  dates_for_whole_section[j]);
    }

    var start_string_broken_up = start_id.toString().split('_');
    //console.log("Start String Broken Up: " + start_string_broken_up.toString());

    var week_id = start_string_broken_up[start_string_broken_up.length - 2] + start_string_broken_up[start_string_broken_up.length - 1];
    //console.log("week_id: " + week_id.toString());


    for (let item of dates_for_whole_section) {
        var item_string_broken_up = item.id.toString().split('_');
        ////console.log("\nItem String Broken Up: " + item_string_broken_up.toString());

        var item_week_id = item_string_broken_up[item_string_broken_up.length - 2] + item_string_broken_up[item_string_broken_up.length - 1];
        //console.log("item_week_id: " + item_week_id.toString());
        //console.log("week_id: " + week_id.toString());

        if (week_id === item_week_id) {
            // Get Day of week between end date and start date that corrosponds the item_day_of_week
            // item_day_of_week is a number 0-6 with 0 representing first day of week (Monday)

            var item_day_of_week = parseInt(item_string_broken_up[item_string_broken_up.length - 3]);
            //console.log("item_day_of_week: " + item_day_of_week.toString());

            //console.log("monday: " + monday.toDateString());

            var item_date = new Date(monday);
            item_date.setDate(monday.getDate() + parseInt(item_day_of_week));
            //item_date.setDate(item_date.getDate() + 1);

            //console.log("Item Date before: " + item_date.toDateString());

            //console.log("monday date: " + (monday.getDate() + 1).toString());
            //console.log("item date: " + item_date.getDate().toString());

            //console.log("item_date after: " + item_date.toDateString());
            // Convert Date to format readable by datefield:
            dd = item_date.getDate();
            dd_str = dd.toString();
            if (dd_str.length === 1) {
                dd_str = "0" + dd_str;
            }

            mm = item_date.getMonth() + 1;
            mm_str = mm.toString();
            if (mm_str.length === 1) {
                mm_str = "0" + mm_str;
            }

            yyyy = item_date.getFullYear();
            yyyy_str = yyyy.toString();

            //console.log("Setting item value to: " + yyyy_str + "-" + mm_str + "-" + dd_str);
            item.value = (yyyy_str + "-" + mm_str + "-" + dd_str);
            //console.log("item.value: " + item.value.toString())
        }
    }
}




    // forceNumeric() plug-in implementation Author:Josh
    jQuery.fn.forceNumeric = function () {
        return this.each(function () {
            $(this).keydown(function (e) {
                var key = e.which || e.keyCode;

                if (!e.shiftKey && !e.altKey && !e.ctrlKey &&
                    // numbers
                    key >= 48 && key <= 57 ||
                    // Numeric keypad
                    key >= 96 && key <= 105 ||
                    // comma, period and minus, . on keypad
                    key == 190 || key == 188 || key == 109 || key == 110 ||
                    // Backspace and Tab and Enter
                    key == 8 || key == 9 || key == 13 ||
                    // Home and End
                    key == 35 || key == 36 ||
                    // left and right arrows
                    key == 37 || key == 39 ||
                    // Del and Ins
                    key == 46 || key == 45)
                    return true;

                return false;
            });
        });
    }





    function limitInput(){
        $(".numberinput").forceNumeric();
        var number_boxes = document.getElementsByClassName("numberinput");
        var invalidChars = [
          "-",
          "+",
          "e",
        ];
        for (let j = 0; j < number_boxes.length; j++) {
            number_boxes[j].addEventListener("keydown", function(e) {
              if (invalidChars.includes(e.key)) {
                e.preventDefault();
              }
            });
        }
    }


    $(document).ready(function () {

        //iterate through each textboxes and add keyup
        //handler to trigger sum event
        $(".txt").each(function () {

            $(this).keyup(function () {
                calculateSum();
            });
        });

    });

    function calculateSum() {

        var sum = 0;
        //iterate through each textboxes and add the values
        $(".txt").each(function () {

            //add only if the value is number
            if (!isNaN(this.value) && this.value.length != 0) {
                sum += parseFloat(this.value);
            }

        });
        //.toFixed() method will roundoff the final sum to 2 decimal places
        $("#sum").html(sum.toFixed(2));
    }

//<!--this javascript calls the travel advance application section-->
    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function () {
            this.classList.toggle("active");
            var travel_advance = this.nextElementSibling;
            if (travel_advance.style.display === "block") {
                travel_advance.style.display = "none";
            } else {
                travel_advance.style.display = "block";
            }
        });
    }




    function set_up_sum_calculations(){
       var elements = document.getElementsByClassName("numberinput");
        for (let j = 0; j < elements.length; j++) {
            elements[j].setAttribute("onkeyup", 'get_sum()');
        }
    }

    function get_sum () {
        var mileage_number_field_names = ['amount'];
        var personal_meal_number_field_names = ['personal_breakfast', 'personal_lunch', 'personal_dinner', 'personal_meal_perdiem'];
        var hotel_number_field_names = ['hotel_room_change', 'hotel_laundry', 'hotel_telephone', 'hotel_others'];
        var transportation_number_field_names = ['parking', 'tolls', 'rides', 'transportation_others'];
        var business_meal_number_field_names = ['business_breakfast', 'business_lunch', 'business_dinner',];
        var others_number_field_names = ['others_telephone', 'others_gift', 'others_misc',];
        var expenditure_number_field_names = ['expenditure_airfare', 'expenditure_hotel', 'expenditure_autorental', 'expenditure_other'];
        var expenditures_reimbursed_number_names = ['subtotal', 'meal_week_subtotal', 'hotel_week_subtotal', 'transportation_week_subtotal', 'businessmeal_week_subtotal', 'others_week_subtotal'];

        //console.log("Number input changed");
        // connect subtotals to fields using ids
        var all_subtotal_fields = document.getElementsByClassName('subtotal');

        var personal_total = 0;
        var business_total = 0;

        for (let j = 0; j < all_subtotal_fields.length; j++) {
            //console.log("Checking Subtotal field: " + all_subtotal_fields[j].id.toString());
            var sum = 0;
            var field_specifics = all_subtotal_fields[j].id.split('_')[all_subtotal_fields[j].id.split('_').length - 2] + "_" + all_subtotal_fields[j].id.split('_')[all_subtotal_fields[j].id.split('_').length - 1];

            if (all_subtotal_fields[j].name === 'subtotal' || all_subtotal_fields[j].name === 'Travel_Modal_subtotal') {
                for (let k = 0; k < 7; k++) {
                    for (let l = 0; l < mileage_number_field_names.length; l++) {
                        var field_id = '#' + mileage_number_field_names[l] + '_' + k.toString() + "_" + field_specifics;
                        //console.log("Adding field ID: " + field_id);
                        sum += parseFloat($(field_id).val()) || 0;
                    }
                }
                document.getElementById('subtotal_' + field_specifics).value = sum;
                document.getElementById('Travel_Modal_subtotal_' + field_specifics).value = sum;
                personal_total += sum;
            }
            else if (all_subtotal_fields[j].name === 'sub_mileage' || all_subtotal_fields[j].name === 'weekly_mileage') {
                for (let k = 0; k < 7; k++) {
                    var field_id = '#mileage_' + k.toString() + "_" + field_specifics;
                    //console.log("Adding Field ID: " + field_id);
                    sum += parseFloat($(field_id).val()) || 0;
                }
                all_subtotal_fields[j].value = sum;
                document.getElementById('weekly_mileage_' + field_specifics).value = sum;
                document.getElementById('sub_mileage_' + field_specifics).value = sum;
            }
            else if (all_subtotal_fields[j].name === 'meal_week_subtotal' || all_subtotal_fields[j].name === 'Meal_Expense_Modal_subtotal') {
                for (let k = 0; k < 7; k++) {
                    for (let l = 0; l < personal_meal_number_field_names.length; l++) {
                        var field_id = '#' + personal_meal_number_field_names[l] +'_' + k.toString() + "_" + field_specifics;
                        //console.log("Adding Field ID: " + field_id);
                        var add_this = parseFloat($(field_id).val()) || 0;
                        if (add_this !== 0){
                            //console.log(add_this.toString() + " coming from " + field_id);
                        }
                        sum += parseFloat($(field_id).val()) || 0;
                    }
                }
                document.getElementById('meal_week_subtotal_' + field_specifics).value = sum;
                document.getElementById('Meal_Expense_Modal_subtotal_' + field_specifics).value = sum;
                personal_total += sum;
            }
            else if (all_subtotal_fields[j].name === 'hotel_week_subtotal' || all_subtotal_fields[j].name === 'Hotel_Expense_Modal_subtotal') {
                for (let k = 0; k < 7; k++) {
                    for (let l = 0; l < hotel_number_field_names.length; l++) {
                        var field_id = '#' + hotel_number_field_names[l] +'_' + k.toString() + "_" + field_specifics;
                        //console.log("Adding Field ID: " + field_id);
                        sum += parseFloat($(field_id).val()) || 0;
                    }
                }
                all_subtotal_fields[j].value = sum;
                personal_total += sum;
            }
            else if (all_subtotal_fields[j].name === 'transportation_week_subtotal' || all_subtotal_fields[j].name === 'Transportation_Expense_Modal_subtotal') {
                for (let k = 0; k < 7; k++) {
                    for (let l = 0; l < transportation_number_field_names.length; l++) {
                        var field_id = '#' + transportation_number_field_names[l] +'_' + k.toString() + "_" + field_specifics;
                        //console.log("Adding Field ID: " + field_id);
                        sum += parseFloat($(field_id).val()) || 0;
                    }
                }
                all_subtotal_fields[j].value = sum;
                personal_total += sum;
            }
            else if (all_subtotal_fields[j].name === 'businessmeal_week_subtotal' || all_subtotal_fields[j].name === 'BusinessMeal_Expense_Modal_subtotal') {
                for (let k = 0; k < 7; k++) {
                    for (let l = 0; l < business_meal_number_field_names.length; l++) {
                        var field_id = '#' + business_meal_number_field_names[l] +'_' + k.toString() + "_" + field_specifics;
                        //console.log("Adding Field ID: " + field_id);
                        sum += parseFloat($(field_id).val()) || 0;
                    }
                }
                all_subtotal_fields[j].value = sum;
                business_total += sum;
            }
            else if (all_subtotal_fields[j].name === 'others_week_subtotal' || all_subtotal_fields[j].name === 'Others_Expense_Modal_subtotal') {
                for (let k = 0; k < 7; k++) {
                    for (let l = 0; l < others_number_field_names.length; l++) {
                        var field_id = '#' + others_number_field_names[l] +'_' + k.toString() + "_" + field_specifics;
                        //console.log("Adding Field ID: " + field_id);
                        sum += parseFloat($(field_id).val()) || 0;
                    }
                }
                all_subtotal_fields[j].value = sum;
                business_total += sum;
            }
            else if (all_subtotal_fields[j].name === 'expenditure_week_subtotal' || all_subtotal_fields[j].name === 'Expenditure_Expense_Modal_subtotal') {
                for (let k = 0; k < 7; k++) {
                    for (let l = 0; l < expenditure_number_field_names.length; l++) {
                        var field_id = '#' + expenditure_number_field_names[l] +'_' + k.toString() + "_" + field_specifics;
                        //console.log("Adding Field ID: " + field_id);
                        sum += parseFloat($(field_id).val()) || 0;
                    }
                }
                document.getElementById('expenditure_week_subtotal_' + field_specifics).value = sum;
                document.getElementById('Expenditure_Expense_Modal_subtotal_' + field_specifics).value = sum;
            }
        }

        // Calculate Expenditures to be Reimbursed:
        sum = 0;
        for (let l = 0; l < expenditures_reimbursed_number_names.length; l++) {
            var subtotals_of_same_type = document.getElementsByName(expenditures_reimbursed_number_names[l]);
            for (let k = 0; k < subtotals_of_same_type.length; k++) {
                var field_id = subtotals_of_same_type[k].id;
                sum += parseFloat(subtotals_of_same_type[k].value || 0);
            }
        }
        document.getElementById('expenditure_reimbursed').value = sum;
        var total_expense_sum = sum;
        var total_expenditure_sum = sum;

        // Calculate Expenditures Charged to Company:
        sum = 0;
        var subtotals_of_same_type = document.getElementsByName('expenditure_week_subtotal');
        for (let k = 0; k < subtotals_of_same_type.length; k++) {
            var field_id = subtotals_of_same_type[k].id;
            console.log("ID: " + field_id);
            console.log("Value: " + subtotals_of_same_type[k].value);
            sum += parseFloat(subtotals_of_same_type[k].value || 0);
            console.log("Sum: " + sum.toString());
        }
        document.getElementById('expenditure_charged').value = sum;
        total_expenditure_sum += sum;

        // Calculate total expenditures
        document.getElementById('total_expenditures').value = total_expenditure_sum;

        // Calculate Amount Due to Employee / Company:
        var adv_amount = parseFloat(document.getElementById("travel_advance").value);

        // Check if Proof of Payment Back To Company Back To Company is Required
        if (total_expense_sum - adv_amount >= 0){
            document.getElementById("employee_amount_due").value = parseFloat(document.getElementById('expenditure_reimbursed').value) - adv_amount;
            document.getElementById("company_amount_due").value = 0;

            document.getElementById("company_amount_due_file_label").innerHTML = " Proof of Payment Back To Company <b>Not Required</b>:";
        }
        else{
            document.getElementById("employee_amount_due").value = 0;
            document.getElementById("company_amount_due").value = (parseFloat(document.getElementById('expenditure_reimbursed').value) - adv_amount) * -1;

            document.getElementById("company_amount_due_file_label").innerHTML = " Proof of Payment Back To Company <b>Required</b>:";
        }

        sum = 0;

        // Calculate total Cost for Mileage:
        var sub_mileages = document.getElementsByName('subtotal');
        for (let j = 0; j < sub_mileages.length; j++) {
            sum += parseFloat(sub_mileages[j].value || 0);
        }
        document.getElementById("total").value = sum;


        // Check if Mileage Proof is required:
        var mileage_subtotals = document.getElementsByName('subtotal');
        var mileage_mileages = document.getElementsByName('weekly_mileage');
        var mileage_proof_needed = false;
        for (let j = 0; j < mileage_subtotals.length; j++) {
            if(parseFloat(mileage_mileages[j].value || 0) > 0 || parseFloat(mileage_subtotals[j].value || 0) > 0){
                mileage_proof_needed = true;
            }
        }
        if (mileage_proof_needed){
            //console.log("Setting it tp rwuired");
            document.getElementById('mileage_document_header').innerHTML = "Mileage Document <b>Required</b>:";
        }
        else{
            //console.log("Setting it tp not rwuired");
            document.getElementById('mileage_document_header').innerHTML = "Mileage Document <b>Not Required</b>:";
        }

        // Check if personal proof is needed:
        if (personal_total > 0){
            document.getElementById('personal_expense_file_label').innerHTML = "Upload Documents Proving Personal Expenses <b>Required</b>:";
        }
        else{
            document.getElementById('personal_expense_file_label').innerHTML = "Upload Documents Proving Personal Expenses <b>Not Required</b>:";
        }

        // Check if business proof is needed:
        if (business_total > 0){
            document.getElementById('business_expense_file_label').innerHTML = "Upload Documents Proving Business Expenses <b>Required</b>:";
        }
        else{
            document.getElementById('business_expense_file_label').innerHTML = "Upload Documents Proving Business Expenses <b>Not Required</b>:";
        }

    }




$(document).on('hidden.bs.modal', function (e) {
    if ($(e.target).attr('data-refresh') === 'true') {
        // Remove modal data
        $(e.target).removeData('bs.modal');
        // Empty the HTML of modal
        $(e.target).html('');
    }
});



    //<!-- This script by corrina updates the business expense explanation purpose field to match what it is in the popup-->
    function update_purpose(field_specifics){
        document.getElementById('bee_show_purpose'+field_specifics).value = document.getElementById('business_expense_purpose'+ field_specifics).value;
    }




    function update_gl(){
        // Mileage
        var select_box = document.getElementById('gl_account');
        var label = document.getElementsByName("gl_account_label")[0];
        label.innerHTML = "GL Account : " + select_box.value;

        // Personal Meal
        select_box = document.getElementById('gl_account_p_meal');
        label = document.getElementsByName("gl_account_label_p_meal")[0];
        label.innerHTML = "GL Account : " + select_box.value;

        // Hotel
        select_box = document.getElementById('gl_account_hotel');
        label = document.getElementsByName("gl_account_label_hotel")[0];
        label.innerHTML = "GL Account : " + select_box.value;

        // Transportation
        select_box = document.getElementById('gl_account_transportation');
        label = document.getElementsByName("gl_account_label_transportation")[0];
        label.innerHTML = "GL Account : " + select_box.value;

        // Business Meal
        select_box = document.getElementById('gl_account_b_meal');
        label = document.getElementsByName("gl_account_label_b_meal")[0];
        label.innerHTML = "GL Account : " + select_box.value;

        // Others
        select_box = document.getElementById('gl_account_others');
        label = document.getElementsByName("gl_account_label_others")[0];
        label.innerHTML = "GL Account : " + select_box.value;

        // Expenditures
        select_box = document.getElementById('gl_account_expenditure');
        label = document.getElementsByName("gl_account_label_expenditure")[0];
        label.innerHTML = "GL Account : " + select_box.value;
    }
    
    
