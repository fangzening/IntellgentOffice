// Author: Corrina Barr
// These Javascripts control whether fields are readonly or not

// Initializing Global Variables:
var mileage_field_names = ['week_begin', 'week_end', 'total_mileage', 'subtotal', 'date', 'departure_from',
    'destination_to', 'mileage', 'amount'];
var personal_meal_field_names = ['meal_week_start', 'meal_week_end', 'meal_week_subtotal', 'personal_breakfast',
    'personal_lunch', 'personal_dinner', 'personal_meal_date', 'personal_meal_perdiem', 'personal_meal_perdiem_date'];
var hotel_field_names = ['hotel_week_start', 'hotel_week_end', 'hotel_week_subtotal', 'hotel_room_change',
    'hotel_laundry', 'hotel_telephone', 'hotel_others', 'hotel_date'];
var transportation_field_names = ['transportation_week_start', 'transportation_week_end', 'transportation_week_subtotal',
    'parking', 'tolls', 'rides', 'transportation_others', 'transportation_date'];
var business_meal_field_names = ['businessmeal_week_start', 'businessmeal_week_end', 'businessmeal_week_subtotal',
    'business_breakfast', 'business_lunch', 'business_dinner', 'business_meal_date'];
var others_field_names = ['others_week_start', 'others_week_end', 'others_week_subtotal', 'others_telephone', 'others_gift',
    'others_misc', 'others_date'];
var expenditure_field_names = ['expenditure_week_start', 'expenditure_week_end', 'expenditure_week_subtotal',
    'expenditure_airfare', 'expenditure_hotel', 'expenditure_autorental', 'expenditure_other', 'expenditure_date',
    'expenditure_week_subtotal'];

// class: switchable_field_id
//      Items with this class name hold ids of switchable fields in their value attribute
// class: select_field_id
//      Items with this class name hold ids of select fields that switch with readonly input fields in their value attribute
// initialize_readonly_function is called on page load
// It controls whether fields are readonly, and
// shows which fields were modified if there were any modified
function initialize_readonly_function(sap_editable){
    // SHOW MODIFIED FIELDS
    var read_modified_fields = document.getElementsByClassName("modified_fields");
    var sap_field_ids = ['advance_amount', 'company_code', 'currency', 'invoice_date', 'cost_center', 'ta_doc_num',
                        'head_text', 'vendor_code', 'assignment', 'text', 'invoice_number'];

    // Loop through all modified field objects
    for (let i = 0; i < read_modified_fields.length; i++) {
        console.log("Looking at field: " + read_modified_fields[i].name);
        var field_to_update = document.getElementById(read_modified_fields[i].name);

        // If field exists, edit the field
        if (field_to_update !== null){
            if (field_to_update.getAttribute("type") !== "file"){
                if (read_modified_fields[i].value !== '..DELETED_FIELD..'){
                    field_to_update.style.backgroundColor = "lightgreen";
                    field_to_update.style.font.bold();
                    field_to_update.value = read_modified_fields[i].value;
                }
                else{
                    if (isNaN(read_modified_fields[i].id.split('_')[read_modified_fields[i].id.split('_').length - 1]) === false){
                        delete_field_and_associated_fields(field_to_update.id);
                    }
                }
            }
        }
        //If field does not exist, that means it was created by the modifier and needs to be added to the HTML
        else{
            console.log("creating field and associated fields");
            create_field_and_associated_fields(read_modified_fields[i].name);
        }
    } //End Loop through all modified field objects

    // MAKE FIELDS READONLY
    var switchable_fields_query = document.querySelectorAll(":read-write");

    for (let i = 0; i < switchable_fields_query.length; i++) {
        if (switchable_fields_query[i].id.toString() !== "comment" && switchable_fields_query[i].id.toString() !== 'chat-input'){
            //console.log("Switchable field: " + switchable_fields_query[i].id.toString());

            // class: switchable_field_id
            //      Items with this class name hold ids of switchable fields in their value attribute
            console.log("field id: " + switchable_fields_query[i].id.toString());
            console.log("sap editable: " + sap_editable.toString());
            console.log("in sap: " + (sap_field_ids.includes(switchable_fields_query[i].id).toString()));

            if((sap_editable) && (sap_field_ids.includes(switchable_fields_query[i].id.toString()) === false)){
                $('#re_form').append("<input hidden readonly class='switchable_field_id' value='" + switchable_fields_query[i].id +"'>");
                console.log("adding to thing");
                switchable_fields_query[i].setAttribute("readonly", true);
            }
            if (sap_editable === false){
                $('#re_form').append("<input hidden readonly class='switchable_field_id' value='" + switchable_fields_query[i].id +"'>");
                switchable_fields_query[i].setAttribute("readonly", true);
            }

        }
    }

    var switchable_buttons_query = $('a[id^="delete_week"]');
    for (let i = 0; i < switchable_buttons_query.length; i++) {
        switchable_buttons_query[i].setAttribute("hidden", true);
    }

    switchable_buttons_query = $('a[id^="addnew"]');
    for (let i = 0; i < switchable_buttons_query.length; i++) {
        switchable_buttons_query[i].setAttribute("hidden", true);
    }

    var calculations_elements_ids = ['expenditure_reimbursed', 'expenditure_charged', 'travel_advance', 'employee_amount_due', 'company_amount_due', 'total_expenditures'];
    for (let i = 0; i < calculations_elements_ids.length; i++) {
        // class: switchable_field_id
            //      Items with this class name hold ids of switchable fields in their value attribute
            $('#re_form').append("<input hidden readonly class='switchable_field_id' value='" + calculations_elements_ids[i] +"'>");
    }

    var select_fields_query = document.querySelectorAll("select");

    for (let i = 0; i < select_fields_query.length; i++) {
        if (select_fields_query[i].id !== "add_approver_action" && select_fields_query[i].id !== "add_approvers_options"){
            //console.log("SELECT field: " + select_fields_query[i].id.toString());

             // class: select_field_id
            //      Items with this class name hold ids of select fields that switch with readonly input fields in their value attribute
            $('#re_form').append("<input hidden readonly class='select_field_id' value='" + select_fields_query[i].id +"'>");

            //console.log("Select Field: " + select_fields_query[i].id.toString());

            //create input feilds base off of select fields
            var input_field = "<input readonly value='"+ select_fields_query[i].options[select_fields_query[i].selectedIndex].text.toString() +"' id='"+ select_fields_query[i].id.toString() +"_input' class='" + select_fields_query[i].className.toString() +"'>";

            //console.log("Input field HTML: " + input_field);

            select_fields_query[i].insertAdjacentHTML("beforebegin", input_field);

            //console.log("Input feild id: " + document.getElementById(select_fields_query[i].id.toString() +"_input"));

            select_fields_query[i].setAttribute("hidden", true);
        }
    }

    try{
        document.getElementById('add_approver_form').setAttribute("hidden", true);
        document.getElementById('ask_approval_button').value = 'Edit Approver List';
    }
    catch (e) {
        console.log("Viewer cannot approve the form")
    }

    set_up_sum_calculations();
    get_sum();

}



function modify_button_clicked(){
     //get ids of all fields that need to not be readonly anymore
    var switchable_field_id_fields = document.getElementsByClassName("switchable_field_id");
    for (let i = 0; i < switchable_field_id_fields.length; i++) {
        document.getElementById(switchable_field_id_fields[i].value).removeAttribute("readonly");
    }

    //hide input fields based on select boxes and show the select boxes
    var select_box_id_fields = document.getElementsByClassName("select_field_id");

    for (let i = 0; i < select_box_id_fields.length; i++) {
        console.log("select id: " + select_box_id_fields[i].value.toString());
        document.getElementById(select_box_id_fields[i].value.toString() + '_input').setAttribute("hidden", true);
        document.getElementById(select_box_id_fields[i].value).removeAttribute("hidden");
    }
    try{
        document.getElementById("modify_button").setAttribute("hidden", true);
        document.getElementById("allow_modify").setAttribute("hidden", true);
        document.getElementById("send_modify_hidden").removeAttribute("hidden");
        document.getElementById("send_modify_hidden").innerHTML = '<input class="btn btn-success ml-auto " id="send_modify_button" name="submit_button" type="submit" title="Next" value="Send Modified" onclick="document.getElementById(\'submit_button\').value=\'Send Modified\'">';
    }
    catch (e) {
        console.log(e.toString());
    }


    // var switchable_buttons_query = $('a[id^="delete_week"]');
    // for (let i = 0; i < switchable_buttons_query.length; i++) {
    //     switchable_buttons_query[i].removeAttribute("hidden");
    // }
    //
    // switchable_buttons_query = $('a[id^="addnew"]');
    // for (let i = 0; i < switchable_buttons_query.length; i++) {
    //     switchable_buttons_query[i].removeAttribute("hidden");
    // }
}


function create_fields_associated_with_ids(){
    // CREATING FIELDS TO HELP ASSOCIATE IDS WITH NAMES IN POST DATA
    try{
        document.getElementById("send_modify_button").setAttribute("readonly", true);
    }
    catch(e){
        console.log(e.toString());
    }
    var all_elements = document.querySelectorAll("input, select, textarea");
    for (let i = 0; i < all_elements.length; i++) {
        try{
            var element_value = all_elements[i].id;
        }
        catch (e) {
            console.log("ERROR getting ID: " + e.toString());
            continue;
        }
        try{
            var element_name = all_elements[i].name.toString() + "-m";
        }
        catch (e) {
            console.log("ERROR getting name: " + e.toString());
            continue;
        }
        if (element_name !== null && element_name !== '' && element_value !== '' && element_value !== null){
            var hidden_field = "<input hidden readonly value='" + element_value +"' name='" + element_name + "'>";
            console.log("Modified Field: " + hidden_field);

            $('#re_form').append(hidden_field);
        }

    }
}


function show_approver_form() {
    if (document.getElementById('ask_approval_button').value === 'Cancel') {
        document.getElementById('add_approver_form').hidden = true;
        document.getElementById('ask_approval_button').value = 'Edit Approver List';
    } else {
        document.getElementById('add_approver_form').hidden = false;
        document.getElementById('ask_approval_button').value = 'Cancel'
    }

}

function delete_field_and_associated_fields(field_id){
    console.log("Field ID: " + field_id);
    var checkbox_id = get_checkbox_id_from_field_id(field_id);
    console.log("checkbox id: " + checkbox_id);
    var checkbox_exists = true;
    try{
        document.getElementById(checkbox_id).setAttribute("checked", true);
    }
    catch{
        checkbox_exists = false;
    }
    if (checkbox_exists){
        var table_id = get_table_name_from_id(field_id);
        deleteRow(table_id);
    }
}

function create_field_and_associated_fields(field_id) {
    var does_element_exist = document.getElementById(field_id);
    if (does_element_exist === null){
        var field_name = get_name_from_id(field_id);
        var row = get_row_from_id(field_id);
        var rows_table_id = get_table_from_id(field_id);
        $('#' + rows_table_id).append(row);
        create_popup_from_field_id(field_id);
    }
}


function get_name_from_id(field_id){
    // Get field name so we know where to put it
    var field_name_list = field_id.split("_");
    var add_to_name = true;
    var field_name = "";
    for (let i = 0; i < field_name_list.length; i++) {
        if (i===0){
            field_name += field_name_list[i];
        }
        else{
            if(isNaN(field_name_list[i])){
                if(field_name_list[i] !== 'unsaved' && field_name_list[i] !== 'saved'){
                    if (add_to_name){
                        field_name += "_" + field_name_list[i];
                    }
                }
                else{
                    add_to_name = false;
                }
            }
            else{
                add_to_name = false;
            }
        }
    }
    return field_name
}


function get_row_from_id(field_id){
    // Get field name
    var field_name = get_name_from_id(field_id);
    console.log("**Field name: " + field_name);
    // Get what is after field name
    var long_field_specifics = field_id.replace(field_name, '').split('_');
    var field_specifics = long_field_specifics[long_field_specifics.length-2] + '_' + long_field_specifics[long_field_specifics.length-1];
    console.log('field specifics: ' + field_specifics);
    var row = "";

    if (mileage_field_names.includes(field_name)){
        var start_date_id = "week_begin_" + field_specifics;
        console.log('start_date_id: ' + start_date_id);
        var start_date_value = document.getElementsByName(start_date_id)[0].value;
        var end_date_id = "week_end_" + field_specifics;
        var end_date_value = document.getElementsByName(end_date_id)[0].value;
        row = "<tr>\n" +
            "                                                <td colspan=\"1\"><input type=\"checkbox\" id='row_checkbox_mileage_" + field_specifics + "'></td>\n" +
            "                                                <td><input type=\"date\" class=\"form-control\" id=\"week_begin_" + field_specifics + "\" name=\"week_begin\" value=\"" + start_date_value +"\"\n" +
            "                                                           onfocusout=\"set_week('week_begin_"+ field_specifics +"', 'week_end_" + field_specifics + "', 'date', '')\" readonly>\n" +
            "                                                </td>\n" +
            "                                                <td><input type=\"date\" class=\"form-control\" id=\"week_end_"+ field_specifics +"\" name=\"week_end\"\n" +
            "                                                           placeholder=\"To\" value=\"" + end_date_value + "\" readonly></td>\n" +
            "                                                <td colspan=\"1\"><input type=\"text\" width=\"48\"\n" +
            "                                                                       class=\"form-control\" id=\"total_mileage\" name=\"total_mileage\"\n" +
            "                                                                       data-toggle=\"modal\"\n" +
            "                                                                       data-target=\"#Travel_Modal_" + field_specifics +"\" readonly></td>\n" +
            "                                                <td><input type=\"text\" class=\"form-control\" id=\"subtotal\" name=\"subtotal\"\n" +
            "                                                           placeholder=\"subtotal\" data-toggle=\"modal\"\n" +
            "                                                           data-target=\"#Travel_Modal_" + field_specifics + "\" readonly></td>\n" +
            "                                                <td>\n" +
            "                                                    <input type=\"button\" class=\"btn btn-outline-primary form-control\"\n" +
            "                                                           value=\"Edit\" id=\"view\"\n" +
            "                                                           data-toggle=\"modal\" data-target=\"#Travel_Modal_" + field_specifics + "\">\n" +
            "                                                </td>\n" +
            "                                            </tr>";
        }
        return row;
}

function get_table_from_id(field_id){
    var field_name = get_name_from_id(field_id);
    if (mileage_field_names.includes(field_name)){
        return 'tableadd';
    }
    else if (personal_meal_field_names.includes(field_name)){
        return 'tableadd_expense_meal';
    }
    else if (hotel_field_names.includes(field_name)){
        return 'tableadd_expense_hotel';
    }
    else if (transportation_field_names.includes(field_name)){
        return 'tableadd_expense_transportation';
    }
    else if (business_meal_field_names.includes(field_name)){
        return 'tableadd_business_expense_meal';
    }
    else if (others_field_names.includes(field_name)){
        return 'tableadd_others';
    }
    else if (expenditure_field_names.includes(field_name)){
        return 'tableadd_expenditure';
    }

}


function get_checkbox_id_from_field_id(field_id){
    var field_name = get_name_from_id(field_id);
    var split_id = field_id.split('_');
    var check_box_end_of_id = split_id[split_id.length-2] + '_' + split_id[split_id.length-1];

    if (mileage_field_names.includes(field_name)){
       return "row_checkbox_mileage_" + check_box_end_of_id;
    }
    else if(personal_meal_field_names.includes(field_name)){
        return "row_checkbox_personal_meal_" + check_box_end_of_id;
    }
    else if(hotel_field_names.includes(field_name)){
        return "row_checkbox_hotel_" + check_box_end_of_id;
    }
    else if(transportation_field_names.includes(field_name)){
        return "row_checkbox_transportation_" + check_box_end_of_id;
    }
    else if(business_meal_field_names.includes(field_name)){
        return "row_checkbox_business_meal_" + check_box_end_of_id;
    }
    else if(others_field_names.includes(field_name)){
        return "row_checkbox_other_" + check_box_end_of_id;
    }
    else if(expenditure_field_names.includes(field_name)){
        return "row_checkbox_expenditure_" + check_box_end_of_id;
    }
}

function get_table_name_from_id(field_id){
    var field_name = get_name_from_id(field_id);
    console.log("Field Name: " + field_name);
    var split_id = field_id.split('_');
    var check_box_end_of_id = split_id[split_id.length-2] + '_' + split_id[split_id.length-1];

    if (mileage_field_names.includes(field_name)){
       return "tableadd";
    }
    else if (personal_meal_field_names.includes(field_name)){
        return "tableadd_expense_meal";
    }
    else if(hotel_field_names.includes(field_name)){
        return "tableadd_expense_hotel";
    }
    else if(transportation_field_names.includes(field_name)){
        return "tableadd_expense_transportation";
    }
    else if(business_meal_field_names.includes(field_name)){
        return "tableadd_business_expense_meal";
    }
    else if(others_field_names.includes(field_name)){
        return "tableadd_others";
    }
    else if(expenditure_field_names.includes(field_name)){
        return "tableadd_expenditure";
    }
}


function create_popup_from_field_id(field_id){
    var rowIndex = field_id.split('_')[field_id.split('_').length - 1];
    var field_name = get_name_from_id(field_id);

    if (mileage_field_names.includes(field_name)){
        var column_titles = ['DATE', 'DEPARTURE', 'DESTINATION', 'MILEAGE', 'AMOUNT'];
        var column_field_names = ['date', 'departure_from', 'destination_to', 'mileage', 'amount'];
        create_section_popup(rowIndex, column_titles, column_field_names, 'mileage_popup_subtotal_' + rowIndex, false, "Travel_Modal", "mileage_popups", true, '', "Mileage Expenses");
    }
}

function work_from_declined_form(){
    var submit_buttons = document.getElementsByName("submit_button");
    for (let i = 0; i < submit_buttons.length; i++) {
        if (submit_buttons[i].id !== "submit_button"){
            submit_buttons[i].removeAttribute("hidden");
        }
    }

    // Upload document tables
    var upload_document_ids = ["mileage_doc_table", "personal_doc_table", "business_doc_table", "pay_doc_table",
                                "addnew_pay_file", "delete_pay_file", "addnew_b_file", "delete_b_file", "addnew_p_file",
                                "delete_p_file", "addnew_mileage_file", "delete_mileage_file"];
    for (let i = 0; i < upload_document_ids.length; i++) {
        document.getElementById(upload_document_ids[i]).removeAttribute("hidden");
    }

    var switchable_buttons_query = $('a[id^="delete_week"]');
    for (let i = 0; i < switchable_buttons_query.length; i++) {
        switchable_buttons_query[i].removeAttribute("hidden");
    }

    switchable_buttons_query = $('a[id^="addnew"]');
    for (let i = 0; i < switchable_buttons_query.length; i++) {
        switchable_buttons_query[i].removeAttribute("hidden");
    }

    document.getElementById("work_from_declined_form_button").setAttribute("hidden", true);

    modify_button_clicked();

    var calculation_element_ids = ['expenditure_reimbursed', 'expenditure_charged', 'travel_advance', 'employee_amount_due', 'company_amount_due', 'total_expenditures'];

    for (let i = 0; i < calculation_element_ids.length; i++) {
        document.getElementById(calculation_element_ids[i]).setAttribute("readonly", true);
    }
}


function check_if_start_date_already_exists_in_section(start_date_id, end_date_id) {
    var start_date_name = get_name_from_id(start_date_id);
    var start_dates_in_section = document.getElementsByName(start_date_name);
    for (let i = 0; i < start_dates_in_section.length; i++) {
        if(start_dates_in_section[i].id !== start_date_id){
            //check if value = start date id value
            if (start_dates_in_section[i].value === document.getElementById(start_date_id).value){
                alert("There cannot be two of the same week in a section.");
                // Set all dates in row/popup to nothing
                document.getElementById(start_date_id).value = '';
                document.getElementById(end_date_id).value = '';
                var dates_to_make_empty = get_dates_from_start_date_id(start_date_id);
                for (let j = 0; j < dates_to_make_empty.length; j++) {
                    //console.log("Date id: " + dates_to_make_empty[j].toString());
                    document.getElementById(dates_to_make_empty[j]).value = '';
                }
                return true;
            }
        }
    }
    return false;
}


function get_dates_from_start_date_id(start_date_id) {
    var start_date_name = get_name_from_id(start_date_id);
    var date_specifics = start_date_id.split('_')[start_date_id.split('_').length-2] + '_' + start_date_id.split('_')[start_date_id.split('_').length-1];
    var popup_date_field_ids = [];

    if(mileage_field_names.includes(start_date_name)){
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("date_" + i.toString() + "_" + date_specifics);
        }
    }
    else if(personal_meal_field_names.includes(start_date_name)){
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("personal_meal_date_" + i.toString() + "_" + date_specifics);
        }
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("personal_meal_perdiem_date_" + i.toString() + "_" + date_specifics);
            console.log("personal_meal_perdiem_date_" + i.toString() + "_" + date_specifics);
        }
    }
    else if(hotel_field_names.includes(start_date_name)){
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("hotel_date_" + i.toString() + "_" + date_specifics);
        }
    }
    else if(transportation_field_names.includes(start_date_name)){
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("transportation_date_" + i.toString() + "_" + date_specifics);
        }
    }
    else if(business_meal_field_names.includes(start_date_name)){
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("business_meal_date_" + i.toString() + "_" + date_specifics);
        }
    }
    else if(business_meal_field_names.includes(start_date_name)){
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("business_meal_date_" + i.toString() + "_" + date_specifics);
        }
    }
    else if(others_field_names.includes(start_date_name)){
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("others_date_" + i.toString() + "_" + date_specifics);
        }
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("others_date_" + i.toString() + "_" + date_specifics);
        }
    }
    else if(expenditure_field_names.includes(start_date_name)){
        for (let i = 0; i < 7; i++) {
            popup_date_field_ids.push("expenditure_date_" + i.toString() + "_" + date_specifics);
        }
    }
    return popup_date_field_ids;
}

function add_new_file_field(file_type){
        var div_id = '';
        if (file_type === 'personal_file'){
            div_id = 'personal_files';
        }
        else if (file_type === 'business_file'){
            div_id = 'business_files';
        }
        else{
            div_id = 'payment_files';
        }
        $('#'+div_id).append('<input name="'+ file_type +'" class="multisteps-form__input form-control"\n type="file" onclick="add_new_file_field(\''+ file_type +'\')>');
        console.log("DIV: " + div_id);
        console.log("INPUT: " + '<input name="'+ file_type +'" class="multisteps-form__input form-control"\n type="file" onclick="add_new_file_field(\''+ file_type +'\')>');
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
                    console.log("Start Date ID: " + startDateID);

                    // Loop through all elements of row but first and last (because they are buttons and checkboxes) and create a deleted_fields object
                    for (let j = 1; j < row.cells.length - 1; j++) {
                        var field_being_deleted = row.cells[j].childNodes[0];
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
                    console.log("Popup Specifics: " + popup_specifics.toString());

                    for (let j = 0; j < start_date_split.length - 2; j++) {
                        start_date_type += start_date_split[j];
                    }

                    console.log("Start Date Type: " + start_date_type.toString());

                    //Get first part of popup name based on start date type
                    if (start_date_type === 'weekbegin'){
                        popup_type = "Travel_Modal";
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
                    else{
                        popup_type="Transportation_Expense_Modal";
                    }

                    var popup_id = popup_type + "_" + start_date_split[start_date_split.length - 2] + "_" + start_date_split[start_date_split.length - 1];
                    //console.log("Popup ID: " + popup_id);

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
                            // console.log("Supporting Document: " + supporting_document_elements[j].id.toString());
                        }

                        // update number of mileage weeks
                        document.getElementById("number_of_mileage_weeks").value = parseInt(document.getElementById("number_of_mileage_weeks").value) - 1;
                    }

                    if (popup_id.includes('unsaved') === false){
                        // Get all input fields within the popup and add them to deleted fields:
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
        // } catch (e) {
        //     alert(e);
        // }
    }

