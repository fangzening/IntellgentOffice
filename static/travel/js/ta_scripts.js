    $(document).ready(function() {
        $('form').keypress(function(e) {
            if ( e.which === 13 ) {
                $(this).next().focus();
                return false;
            }
        });
    });


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

<!--check box authentication for policy page Author:Josh-->
$(function () {
        var chk = $('#check');
        var btn = $('#btncheck');
        chk.on('change', function () {
            btn.prop("disabled", !this.checked);//true: disabled, false: enabled
        }).trigger('change'); //page load trigger event
    });


    function EstimateDate() {
        let date = 0;
        if (document.getElementById("travel_datefrom").value !== '' && document.getElementById("travel_dateto").value !== ''){
            let travelFrom = Date.parse(document.getElementById("travel_datefrom").value);
            let travelTo = Date.parse(document.getElementById("travel_dateto").value);
            let today = Date.parse(document.getElementById("current_date").value);

            var no_errors = true;
            if (travelFrom <= travelTo) {
                date = (travelTo - travelFrom) / (1000 * 3600 * 24) + 1;
                document.getElementById("estimated_period").value = date;
                document.getElementById("travel_datefrom").style.color = "";
                document.getElementById("travel_dateto").style.color = "";
            } else {

                if(travelFrom > travelTo){
                    swal({
                      icon: 'error',
                      title: 'Oops...',
                      text: 'Start Date must be before the End Date!',
                      footer: 'Please check date'
                    });
                    no_errors = false;
                }
                // if(travelFrom <= today){
                //      swal({
                //       icon: 'error',
                //       title: 'Oops...',
                //       text: 'Start date cannot be today and it cannot be before today!',
                //       footer: 'Please check date'
                //     });
                //     no_errors = false;
                // }

                document.getElementById("travel_datefrom").style.color = "red";
                document.getElementById("travel_dateto").style.color = "red";
            }
            totalValue();
            set_head_text();
            set_advance_text();
            if (no_errors){
                validate_visit_dates();
            }
        }
    }

$(function () {
        $('#allowance,#expense_transportation,#expense_accommodation,#other_expense,#airway_ticket,#advance_amount,#total_expense,#public_relationship').keyup(function () {
            var allowance = get_perdiem_amount_from_allowance_value();
            var expense_transportation = parseFloat($('#expense_transportation').val()) || 0;
            var other_expense = parseFloat($('#other_expense').val()) || 0;
            var airway_ticket = parseFloat($('#airway_ticket').val()) || 0;
            var advance = parseFloat($('#advance_amount').val()) || 0;
            var pub_expense = parseFloat($('#public_relationship').val()) || 0;
            var expense_accommodation = parseFloat($('#expense_accommodation').val()) || 0;


            var sum = allowance + expense_transportation + other_expense  + expense_accommodation + airway_ticket + pub_expense;
            if(sum > 99999999.99){
                alert("Total expense cannot exceed $99,999,999.99");
                document.activeElement.value = 0;

                allowance = get_perdiem_amount_from_allowance_value();
                expense_transportation = parseFloat($('#expense_transportation').val()) || 0;
                other_expense = parseFloat($('#other_expense').val()) || 0;
                airway_ticket = parseFloat($('#airway_ticket').val()) || 0;
                advance = parseFloat($('#advance_amount').val()) || 0;
                pub_expense = parseFloat($('#public_relationship').val()) || 0;
                expense_accommodation = parseFloat($('#expense_accommodation').val()) || 0;

                sum = allowance + expense_transportation + other_expense  + expense_accommodation + airway_ticket + pub_expense;
            }



            $('#total_expense').val(sum);
            $('#estimated_expense').val(sum);

            compareAdvance();
        });
    });



    function totalValue() {
        var airTicket = parseInt(document.getElementById("airway_ticket").value);
        var transportation = parseInt(document.getElementById("expense_transportation").value);
        var allowance = get_perdiem_amount_from_allowance_value();
        var otherExpense = parseInt(document.getElementById("other_expense").value);
        var expense_accommodation = parseInt(document.getElementById("expense_accommodation").value);
        var pub_expense = parseInt(document.getElementById("public_relationship").value);
        var total_expense = allowance + transportation + expense_accommodation + otherExpense + airTicket + pub_expense;

        if(total_expense > 99999999.99){
                alert("Total expense cannot exceed $99,999,999.99");
                document.activeElement.value = 0;

                allowance = get_perdiem_amount_from_allowance_value();
                transportation = parseFloat($('#expense_transportation').val()) || 0;
                otherExpense = parseFloat($('#other_expense').val()) || 0;
                airTicket = parseFloat($('#airway_ticket').val()) || 0;
                pub_expense = parseFloat($('#public_relationship').val()) || 0;
                expense_accommodation = parseFloat($('#expense_accommodation').val()) || 0;

                total_expense = allowance + transportation + expense_accommodation + otherExpense + airTicket + pub_expense;
            }

        console.log("Total value being saved");
        console.log("Allowance: " + allowance.toString());
        document.getElementById("total_expense").value = total_expense;
        document.getElementById("estimated_expense").value = total_expense;
        compareAdvance();
    }

    function compareAdvance() {
        var allowance = get_perdiem_amount_from_allowance_value();
        let transportation = parseInt(document.getElementById("expense_transportation").value);
        let advance = parseInt(document.getElementById("advance_amount").value);
        let pub_expense = parseInt(document.getElementById("public_relationship").value);
        let expense_accommodation = parseInt(document.getElementById("expense_accommodation").value);
        let otherExpense = parseInt(document.getElementById("other_expense").value);
        let airTicket = parseInt(document.getElementById('airway_ticket').value);
        let sum = allowance + expense_accommodation + pub_expense;
        document.getElementById("max_amount").innerHTML = "<i>Max: $ " + sum.toString() + "</i>";
        document.getElementById("max_advance_exp").innerHTML = "Max Advance Amount = total allowance(" + allowance.toString() + ") + total accommodation expenses(" + expense_accommodation.toString() + ") + total public relationship expenses(" + pub_expense.toString() + ")<br><br>";
        if (advance > sum) {
            alert("Advance amount can not exceed allowance + accommodation + public relationship expense. Kindly Correct and try again. " +
                "\nallowance + accommodation + public relationship expense: " + sum.toString() +
                "\nAdvance: " + advance.toString());
            document.getElementById("advance_amount").value = sum;
        }
    }

    // Function by Corrina to calculate the total perdiem cost
    function get_perdiem_amount_from_allowance_value(){
        var allowance_value = parseFloat(document.getElementById("allowance").value || 0);
        var total_allowance_amount = allowance_value * parseFloat(document.getElementById("estimated_period").value || 0);
        return total_allowance_amount;
    }


    <!--This function changes the ID of each table on the add function, preventing duplicate form ID's Author:Josh-->
    var rowIndex = 0;
    $("#adding").on('click', function () {
        rowIndex++;
        var newRow = '<tr><td colspan="1"><input id="row_checkbox2' + rowIndex + ' " name="row_checkbox' + rowIndex + ' " type="checkbox" /></td>"' +
            '<td colspan="1"><input name="visit_date' + '" id="visit_date2' + rowIndex + ' " type="date" width="48" class="form-control col-lg-12" ></td>"' +
            '<td><input name="visit_company' + '" id="visit_company2' + rowIndex + ' " placeholder="Company' + rowIndex + ' "  class="form-control" ></td>" ' +
            '<td><input name= "visit_department' + '" id="visit_department2' + rowIndex + ' "placeholder="Department' + rowIndex + ' "  class="form-control" ></td>"' +
            '<td><input name="company_contact' + '" id="company_contact2' + rowIndex + ' " placeholder="Contact' + rowIndex + ' "  class="form-control"></td>" ' +
            '<td><textarea id="visit_objective2' + rowIndex + '" name="visit_objective' + '"class="form-control" rows="5" cols="25"  placeholder="Kindly state objective"></textarea></td> " ' +
            '</tr>';

        if ($("#travel_information > tbody > tr").is("*"))
            $("#travel_information > tbody > tr:last").after(newRow)
        else $("#travel_information > tbody").append(newRow)

    });

//     <!-- This script by Corrina will make it so when the user decides to create a new form based on a declined form, ---->
// <!-- The fields will become not readonly any more and the formID field will become blank.---------------------------->
// <!-- Also the approval list page will be wiped clean and it will say again "You cannot approve this page"------------>
    function work_from_declined_form() {
        var current_date_value = document.getElementById('current_date').value;
        //Array to hold elements that approver will be able to modify when they click modify:
        var readOnlyElements = ["company", "business_group", "project", "travel_type", "cost_description_input", "travel_datefrom",
            "travel_dateto", "transportation", "departure_country", "factory_code", "country2", "state2",
            "destination_city", "accommodation", "adding", "removing",
            "departure_state",
            "airway_ticket", "explaination_airwayticket",
            "other_expense", "explaination_otherexpense", "expense_transportation",
            "explanation_transportation", "public_relationship", "explanation_publicrelationship",
            "advance_amount", "departure_state", "expense_accommodation", "country_currency"];
        document.getElementById("adding").hidden = false;
        document.getElementById("removing").hidden = false;
        var declined_form_buttons = document.getElementsByName('declined_form_button');
        for (let item of declined_form_buttons) {
            item.hidden = true;
        }
        readOnlyElements.forEach(make_not_read_only);
        function make_not_read_only(value, index, array) {
            document.getElementById(value).readOnly = false;
        }
        var save_button_divs = document.getElementsByName("save_button_div");
        for (let item of save_button_divs) {
            item.innerHTML = "<input class=\"btn btn-outline-info btn-lg btn-block\" type=\"submit\" name=\"submit_button\" value=\"Save and Return to Home\" title=\"Save\">";
            item.hidden = false;
        }
        document.getElementById("policy_options").innerHTML = "<input id=\"check\" name=\"checkbox\" type=\"checkbox\">\n" +
            "                                        <label for=\"check\" class=\"control-label\"> I have read and Understand the Foxconn Travel Policy.</label>\n" +
            "\n" +
            "                                        <div class=\"button-row d-flex mt-4\">\n" +
            "                                            <button class=\"btn btn-danger js-btn-prev\" type=\"button\" title=\"Prev\">Decline\n" +
            "                                            </button>\n" +
            "\n" +
            "                                            <input type=\"submit\" name=\"submit_button\" class=\"btn btn-success ml-auto\" id=\"btncheck\" value=\"Send\" />\n" +
            "                                        </div>";
        //Add ids for dynamic section 2
        var checkBoxes = document.getElementsByName("row_checkbox");
        var visitDates = document.getElementsByName("visit_date");
        var visitCompanies = document.getElementsByName("visit_company");
        var visitDepartments = document.getElementsByName("visit_department");
        var companyContacts = document.getElementsByName("company_contact");
        var visitObjectives = document.getElementsByName("visit_objective");
        for (let item of checkBoxes) {
            item.readOnly = false;
        }
        for (let item of visitDates) {
            item.readOnly = false;
        }
        for (let item of visitCompanies) {
            item.readOnly = false;
        }
        for (let item of visitDepartments) {
            item.readOnly = false;
        }
        for (let item of companyContacts) {
            item.readOnly = false;
        }
        for (let item of visitObjectives) {
            item.readOnly = false;
        }
        //Apply for travel advance button:
        document.getElementById("travel_advance_button").disabled = false;
        //Inputs based on select boxes:
        document.getElementById("travel_type_input").disabled = true;
        document.getElementById("travel_type_input").hidden = true;
        //document.getElementById("cost_description_input").disabled = true;
        document.getElementById("cost_description_input").hidden = true;
        document.getElementById("transportation_input").disabled = true;
        document.getElementById("transportation_input").hidden = true;
        document.getElementById("factory_code_input").disabled = true;
        document.getElementById("factory_code_input").hidden = true;
        document.getElementById("accommodation_input").disabled = true;
        document.getElementById("accommodation_input").hidden = true;
        document.getElementById("allowance_input_field").hidden = true;
        document.getElementById("allowance_input_field").disabled = true;
        //Select boxes:
        document.getElementById("allowance_select").disabled = false;
        document.getElementById("allowance_select").hidden = false;
        document.getElementById("travel_type").disabled = false;
        document.getElementById("travel_type").hidden = false;
        document.getElementById("cost_select_button").disabled = false;
        document.getElementById("cost_select_button").hidden = false;
        document.getElementById("transportation").disabled = false;
        document.getElementById("transportation").hidden = false;
        document.getElementById("transportation").readonly = false;
        document.getElementById("factory_code").disabled = false;
        document.getElementById("factory_code").hidden = false;
        document.getElementById("accommodation").disabled = false;
        document.getElementById("accommodation").hidden = false;
        document.getElementById("form_id").value = "";
        $("#approve_section").prepend("Once form is saved or submitted, approval Process will reset and form ID will change.");
        updateTravelAdvanceFields();
        $('#travel_form').append("<input hidden id=\"current_date\" value=\"" + current_date_value +"\" type=\"date\">");
    }


    <!-- Corrina's validation scripts -->
    /**
     * @return {boolean}
     */
    function SendButtonValidationFunction(button_clicked) {
        document.getElementById("submit_button").value = button_clicked;
        /*********************************************************************************************************/
        //Getting values section:
        /*******************************************************************************************************/
        var alert_message = "";
        var display_list = "";
        var elements_that_must_be_filled = [];
        var there_are_elements_that_need_to_be_filled = false;
        //These fields MUST ALWAYS be filled:
        // var fields_ids_to_check = ["project", "travel_datefrom", "travel_dateto", "departure_country", "country2", "state2", "destination_city", "departure_state",
        //     "airway_ticket", "departure_state", "explaination_airwayticket", "other_expense", "explaination_otherexpense", "expense_transportation", "explanation_transportation",
        //     "public_relationship", "explanation_publicrelationship"];

        var fields_ids_to_check = [{id:"project", message:"The Project Name"}, {id: "travel_datefrom", message: "Date of Travel"},
                                   {id: "departure_country", message: "Departure Country"}, {id: "country2", message: "The Country"},
                                   {id: "state2", message: " The State"},{id: "destination_city", message: "The Destination City"},
                                   {id: "departure_state", message: "The Departure City"},];


        // check if other expense or public relationship expense explanations are required
        var other_expense = document.getElementById("other_expense").value;
        if (other_expense === ''){
            other_expense = 0;
        }
        other_expense = parseFloat(other_expense);
        if (other_expense > 0){
            fields_ids_to_check.push({id: "explaination_otherexpense", message: "Explanation for Other Expense"})
        }

        var pub_expense = document.getElementById("public_relationship").value;
        if (pub_expense === ''){
            pub_expense = 0;
        }
        pub_expense = parseFloat(pub_expense);
        if (pub_expense > 0){
            fields_ids_to_check.push({id: "explanation_publicrelationship", message: "Explanation for Public Relationship"})
        }




        //These are the row fields:
        // var row_fields_names_to_check = [
            // document.getElementsByName("visit_date"),
            // document.getElementsByName("visit_company"),
            // document.getElementsByName("visit_department"),
            // document.getElementsByName("company_contact"),
            // document.getElementsByName("visit_objective")];
        var row_fields_names_to_check = [{name:"visit_date", text:"Your Visit Date"}, {name: "visit_company", text: "Your Visit Company"},
                                         {name: "visit_department", text: "The Visit Department"},{name: "company_contact", text: "The Company's Contact"},
                                         {name: "visit_objective", text: "Your Visit Objective"}];
        /*********************************************************************************************************/
        //Validating Section:
        /*******************************************************************************************************/
        // Constant fields:
        for (let item of fields_ids_to_check) {
            if (document.getElementById(item.id).value === "") {
                elements_that_must_be_filled.push(item.message);
                there_are_elements_that_need_to_be_filled = true;
            }//End if statement
        }//End for loop
        // Row fields:

        for (let category of row_fields_names_to_check) {
            for (let field of document.getElementsByName(category.name)) {
                if (field.value === "") {
                    elements_that_must_be_filled.push(category.text);
                    there_are_elements_that_need_to_be_filled = true;
                } // End if value is nothing
             } // End inner for loop
        }
        // for (let category of row_fields_names_to_check) {
        //     for (let field of category) {
        //         if (field.value === "") {
        //             elements_that_must_be_filled.push(field.placeholder);
        //             there_are_elements_that_need_to_be_filled = true;
        //         } // End if value is nothing
        //     } // End inner for loop
        // } //End outer for loop
        //Advance Field:
        if (document.getElementById("travel_advance_apply").value === "true") {
            if (document.getElementById("advance_amount") === "") {
                elements_that_must_be_filled.push("advance_amount");
                there_are_elements_that_need_to_be_filled = true;
            } // end if advance amount is ""
        } //End if travel advance was applied

        if (parseFloat(document.getElementById("total_expense")) > 99999999.99){
             alert_message += "Total expenses are too large. You must lower them.\n"


        }


        //Send Validation Error (if there is any):
        if (there_are_elements_that_need_to_be_filled)
        {

            for (let field of elements_that_must_be_filled)
            {
                display_list +=  '<br>' + field;
            } //end for

            swal({
                title: "Missing Fields",
                html: "These fields still need to be filled out:\n" + "\n" + display_list,
                type: "warning",
                showCancelButton: false,
                confirmButtonText: "Got it!",
                closeOnConfirm: true,
             })

        } //end if

         if (display_list !== "")
         {
             return false;
         }
         return true;



    }
    // End validation function





<!--MultiLevel Drop Down Function Author:Josh-->
    $(document).ready(function () {
        $('.dropdown-submenu a.test').on("click", function (e) {
            $(this).next('ul').toggle();
            e.stopPropagation();
            e.preventDefault();
        });
    });
    $('.submenu').mouseleave(function() {
        $('ul', this).hide("fast");
    });



    function changeInput(code, name, profitCenter) {
        document.getElementById("budget_sc").value = code;
        document.getElementById("cost_select_button").innerHTML = name + ' <span class=""></span>';
        var there_is_profit_center = true;

        //console.log("was doneeee");
        // console.log("About to update cost desc input to " + name.toString());
        // document.getElementById("cost_description_input").value = name;
        // console.log("it is now " + document.getElementById("cost_description_input").value.toString());
        set_advance_text();
        set_assignment();
        set_advance_cost_center();
        set_advance_profit_center(profitCenter);
    }




    <!--Auto-Complete Function. Author:Josh-->
    function autocomplete(inp, arr) {
        var currentFocus;
        inp.addEventListener("input", function (e) {
            var a, b, i, val = this.value;
            closeAllLists();
            if (!val) {
                return false;
            }
            currentFocus = -1;
            a = document.createElement("DIV");
            a.setAttribute("id", this.id + "autocomplete-list");
            a.setAttribute("class", "autocomplete-items");
            this.parentNode.appendChild(a);
            for (i = 0; i < arr.length; i++) {
                if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                    b = document.createElement("DIV");
                    b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                    b.innerHTML += arr[i].substr(val.length);
                    b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                    b.addEventListener("click", function (e) {
                        inp.value = this.getElementsByTagName("input")[0].value;
                        closeAllLists();
                    });
                    a.appendChild(b);
                }
            }
        });

        inp.addEventListener("keydown", function (e) {
            var x = document.getElementById(this.id + "autocomplete-list");
            if (x) x = x.getElementsByTagName("div");
            if (e.keyCode == 40) {
                currentFocus++;
                addActive(x);
            } else if (e.keyCode == 38) {
                currentFocus--;
                addActive(x);
            } else if (e.keyCode == 13) {
                e.preventDefault();
                if (currentFocus > -1) {
                    if (x) x[currentFocus].click();
                }
            }
        });

        function addActive(x) {
            if (!x) return false;
            removeActive(x);
            if (currentFocus >= x.length) currentFocus = 0;
            if (currentFocus < 0) currentFocus = (x.length - 1);
            x[currentFocus].classList.add("autocomplete-active");
        }

        function removeActive(x) {
            for (var i = 0; i < x.length; i++) {
                x[i].classList.remove("autocomplete-active");
            }
        }

        function closeAllLists(elmnt) {
            var x = document.getElementsByClassName("autocomplete-items");
            for (var i = 0; i < x.length; i++) {
                if (elmnt != x[i] && elmnt != inp) {
                    x[i].parentNode.removeChild(x[i]);
                }
            }
        }

        document.addEventListener("click", function (e) {
            closeAllLists(e.target);
        });
    }

    var countries = []

    /*An array containing all the country names in the world:*/
    var countries = ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua & Barbuda", "Argentina", "Armenia",
        "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize",
        "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia & Herzegovina", "Botswana", "Brazil", "British Virgin Islands", "Brunei",
        "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Cayman Islands", "Central Arfrican Republic",
        "Chad", "Chile", "China", "Colombia", "Congo", "Cook Islands", "Costa Rica", "Cote D Ivoire", "Croatia", "Cuba", "Curacao",
        "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador",
        "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands", "Faroe Islands", "Fiji", "Finland", "France",
        "French Polynesia", "French West Indies", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland",
        "Grenada", "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong", "Hungary",
        "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy", "Jamaica", "Japan", "Jersey",
        "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia",
        "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau", "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives",
        "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia",
        "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauro", "Nepal", "Netherlands", "Netherlands Antilles",
        "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "Norway", "Oman", "Pakistan", "Palau", "Palestine",
        "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Reunion", "Romania",
        "Russia", "Rwanda", "Saint Pierre & Miquelon", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
        "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea",
        "South Sudan", "Spain", "Sri Lanka", "St Kitts & Nevis", "St Lucia", "St Vincent", "Sudan", "Suriname", "Swaziland", "Sweden",
        "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor L'Este", "Togo", "Tonga", "Trinidad & Tobago",
        "Tunisia", "Turkey", "Turkmenistan", "Turks & Caicos", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
        "United States of America", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Virgin Islands (US)",
        "Yemen", "Zambia", "Zimbabwe"];

    /*initiate the autocomplete function*/
    autocomplete(document.getElementById("departure_country"), countries);
    autocomplete(document.getElementById("country2"), countries);



    // <!-- This function by Corrina changes the allowance explanation field to match the perdiem chosen --->
    $(document).ready(function(){
        $("#allowance").change(function(){
            var selected = $(this).children("option:selected");
            var selected_id = selected.attr('id').toString();
            var split_id = selected_id.split("-");
            var perdiem_explanation = "";
            for (let i = 0; i < split_id.length; i++) {
                if (i === 0){
                    perdiem_explanation += split_id[i];
                }
                else{
                    perdiem_explanation += " " + split_id[i];
                }

            }
            document.getElementById("explanation_allowance").value = perdiem_explanation;
        });
    });

    // This function sets the value of advance text
    function set_advance_text() {
        var cost_code = document.getElementById('budget_sc').value.toString();
        var start_date = new Date(document.getElementById("travel_datefrom").value);
        var trfm = (start_date.getMonth() + 1).toString();
        var trfd = (start_date.getDate()+1).toString();
        var trfy = start_date.getFullYear().toString()[start_date.getFullYear().toString().length - 2] + start_date.getFullYear().toString()[start_date.getFullYear().toString().length - 1];


        var end_date = new Date(document.getElementById("travel_dateto").value);
        var trtm = (end_date.getMonth() + 1).toString();
        var trtd = (end_date.getDate()+1).toString();
        var trty = end_date.getFullYear().toString()[end_date.getFullYear().toString().length - 2] + end_date.getFullYear().toString()[start_date.getFullYear().toString().length - 1];

        document.getElementById('text').value = cost_code + ", " + trfm + "/" + trfd + "/" + trfy + "-" + trtm + "/" + trtd + "/" + trty + " TRAVEL ADVANCE"
    }


    //<!--this Javascript by Corrina changes button value when it is clicked and controls if travel advance section is shown or not---->

    try {
        var item_in_modified_fields = false;

        var changeable_advance_field_names = ['advance_amount', 'gl_account', 'gl_description', 'memo', 'reference_document',
            'head_text', 'assignment', 'text', 'invoice_number'];

        for (let item of modified_fields) {
            if (item.value in changeable_advance_field_names) {
                item_in_modified_fields = true;
                console.log(item + " in modified fields!")
            }
        }
    } catch (e) {
        console.log("No modified fields");
    }

    if (
        ((document.getElementById("advance_amount").value === '' ||
            document.getElementById("advance_amount").value === 0 ||
            document.getElementById("advance_amount").value === null ||
            document.getElementById("advance_amount").value === 'None'))
        || item_in_modified_fields
    ) {
        document.getElementById("travel_advance_button").value = 'Apply for Travel Advance Application';
        document.getElementById("travel_advance_fields").style.display = "none";
    } else {
        document.getElementById("travel_advance_button").value = 'Un-Apply for Travel Advance Application';
        document.getElementById("travel_advance_fields").style.display = "block";
    }

    if (document.getElementById("travel_advance_button").value === 'Un-Apply for Travel Advance Application') {
        document.getElementById("travel_advance_fields").style.display = "block";
    } else {
        document.getElementById("travel_advance_fields").style.display = "none";
        document.getElementById("advance_amount").value = '';
    }

    function changeButtonValue() {
        var old_value = document.getElementById("travel_advance_apply").value;

        if (old_value === 'false') {
            document.getElementById("travel_advance_apply").value = 'true';
            document.getElementById("travel_advance_button").value = 'Un-Apply for Travel Advance Application';
            document.getElementById("travel_advance_fields").style.display = "block";
            check_if_user_has_vendor_code(true);
        } else if (old_value === 'true') {
            document.getElementById("travel_advance_apply").value = 'false';
            document.getElementById("travel_advance_button").value = 'Apply for Travel Advance Application';
            document.getElementById("travel_advance_fields").style.display = "none";
            document.getElementById('advance_amount').value = 0;
            check_if_user_has_vendor_code(false);
        }
    }

    function setButtonValue(value) {
        if (value === 'true') {
            //document.getElementById("travel_advance_apply").value = 'true';
            document.getElementById("travel_advance_button").value = 'Un-Apply for Travel Advance Application';
            document.getElementById("travel_advance_fields").style.display = "block";
            check_if_user_has_vendor_code(true);
        } else if (value === 'false') {
            //document.getElementById("travel_advance_apply").value = 'false';
            document.getElementById("travel_advance_button").value = 'Apply for Travel Advance Application';
            document.getElementById("travel_advance_fields").style.display = "none"; // Why is this not working??
            document.getElementById('advance_amount').value = 0;
            check_if_user_has_vendor_code(false);
        }
    }

    function updateTravelAdvanceFields() {
        var old_value = document.getElementById("travel_advance_apply").value;
        if (old_value === 'false') {
            document.getElementById("travel_advance_fields").style.display = "none";
        } else {
            document.getElementById("travel_advance_fields").style.display = "block";
        }
    }


    //<!--This script by Corrina will make the edit approvers options hidden until the button is clicked--->


    function show_approver_form() {
        if (document.getElementById('ask_approval_button').value === 'Cancel') {
            document.getElementById('add_approver_form').hidden = true;
            document.getElementById('ask_approval_button').value = 'Edit Approver List';
        } else {
            document.getElementById('add_approver_form').hidden = false;
            document.getElementById('ask_approval_button').value = 'Cancel'
        }

    }




//<!-- This function by Corrina changes the allowance explanation field to match the perdiem chosen --->
    $(document).ready(function(){
        $("#allowance").change(function(){
            var selected = $(this).children("option:selected");
            var selected_id = selected.attr('id').toString();
            var split_id = selected_id.split("-");
            var perdiem_explanation = "";
            for (let i = 0; i < split_id.length; i++) {
                if (i === 0){
                    perdiem_explanation += split_id[i];
                }
                else{
                    perdiem_explanation += " " + split_id[i];
                }

            }
            document.getElementById("explanation_allowance").value = perdiem_explanation;
        });
    });




    // Set assignment
function set_assignment(){
    var vendor_code = document.getElementById("vendor_code").value;
    var department_code = document.getElementById("budget_sc").value;
    var assignment_value = vendor_code.toString() + ", " + department_code.toString();
    document.getElementById('assignment').value = assignment_value;
}

function set_advance_cost_center(){
    document.getElementById('cost_center').value = document.getElementById("budget_sc").value;
}

function set_advance_profit_center(profitCenter){
    var there_is_profit_center = true;
    try {
            var profit_center_element = document.getElementById("advanceprofit_center");
        }
        catch {
            there_is_profit_center = false;
        }

        if (there_is_profit_center){
            profit_center_element.value = profitCenter;
        }
}

// set head text
function set_head_text(){
    var start_date = new Date(document.getElementById("travel_datefrom").value);
    var trfm = (start_date.getMonth() + 1).toString();
    var trfd = (start_date.getDate() + 1).toString();
    //var trfy = start_date.getFullYear().toString()[start_date.getFullYear().toString().length - 2] + start_date.getFullYear().toString()[start_date.getFullYear().toString().length - 1];

    var end_date = new Date(document.getElementById("travel_dateto").value);
    var trtm = (end_date.getMonth() + 1).toString();
    var trtd = (end_date.getDate() + 1).toString();
    //var trty = end_date.getFullYear().toString()[end_date.getFullYear().toString().length - 2] + end_date.getFullYear().toString()[start_date.getFullYear().toString().length - 1];

    document.getElementById("head_text").value = trfm + "/" + trfd + "-" + trtm + "/" + trtd + " TRAVEL ADV.";
}


//check if user has vendor code:
function check_if_user_has_vendor_code(is_opening){
    // Is called when apply for advance is clicked
    // if user does not have vendor code and is applying for advance then do not let them submit form
    if(is_opening) {
        var vendor_code = document.getElementById("user_vendor_code").value;
        if (vendor_code === "None" || vendor_code === "") {
            document.getElementById('vendor_message').innerHTML= "\n" +
            "                                                    <b>There is no vendor code attached to this account.\n" +
            "                                                    If you want to apply for travel advance, you will have to\n" +
            "                                                    go to K2 and apply for a vendor code first.</b>";
            document.getElementById("btncheck").hidden = true;
        }
        else{
            document.getElementById("btncheck").hidden = false;
            document.getElementById('vendor_message').innerHTML= "";
        }
    }
    else{
        document.getElementById('vendor_message').innerHTML= "";
        document.getElementById("btncheck").hidden = false;
    }
}


$(document).ready(function(){
  $("#check").click(function(){
    $('.toast').toast('show');
  });
});


function validate_visit_dates(){
    let date = 0;
    let travelFrom = Date.parse(document.getElementById("travel_datefrom").value);
    let travelTo = Date.parse(document.getElementById("travel_dateto").value);
    var visit_dates = document.getElementsByName('visit_date');

    var no_error_yet = true;
    for (let i = 0; i < visit_dates.length; i++) {
        var checking_date = Date.parse(visit_dates[0].value);
        if (travelTo < checking_date || (travelFrom > checking_date)){
            if (no_error_yet){
                swal({
                      icon: 'error',
                      title: 'Oops...',
                      text: 'Visit Date must be between start and end dates!',
                      footer: 'Please check date'
                    });
                no_error_yet = false
            }
            visit_dates[0].style.color = "red";
        }
        else{
            visit_dates[0].style.color = "";
        }
    }
}

function toggle() {
    let timerInterval
    Swal.fire({
        title: 'Sure! We are working on it!',
        html: 'Generating in <b></b> milliseconds.',
        timer: 1500,
        timerProgressBar: true,
        onBeforeOpen: () => {
            Swal.showLoading()
            timerInterval = setInterval(() => {
                const content = Swal.getContent()
                if (content) {
                    const b = content.querySelector('b')
                    if (b) {
                        b.textContent = Swal.getTimerLeft()
                    }
                }
            }, 100)
        },
        onClose: () => {
            clearInterval(timerInterval)
        }
    }).then((result) => {

        if (result.dismiss === Swal.DismissReason.timer) {
            console.log('Generated')


        }
    })


    var el1 = document.getElementById("main"),
        el2 = document.getElementById("summary_style");
    var sum_button = document.getElementById("summary")
    if (el1.disabled) {
        el1.disabled = false;
        el2.disabled = true;

    } else {
        el1.disabled = true;
        el2.disabled = false;
    }


}

$('#summary').click(function() {
    var change_text = $(this);
        change_text.html(change_text.text() === 'Page Summary' ? 'Go Back to Form' : 'Page Summary');
    return false;
});



    $("#summary").click(function(){



});