var actual_stage_count = 1;
var stage_count = 0;
var condition_count = 0;
var processApproversOptions = document.getElementById('stageApprover-0').innerHTML;


function fill_fields_for_editing(response){
    try{
        console.log("js response: " + JSON.stringify(response).toString());


        // stages part:
         document.getElementById("stages").innerHTML = "";
        var html_inside_stages_div = [];

        for (let i = 0; i > -1; i++) {
            // when it can't find another stage, catch the error and break the loop
            try{
                var next_stage = response['js_context']['stage-' + i.toString()];
                console.log("\nNext Stage: " + JSON.stringify(next_stage).toString())
            }
            catch (e) {
                console.log(e);
                break;
            }

            // stage conditions
            var stage_condition_html = "";
            var stage_condition_connectors = next_stage['connectors'].split(",");

            for (let j = 0; j > -1; j++) {
                var operator_html = "<div id='condition_id-" + condition_count.toString() + "'>";

                try{
                    var next_condition = next_stage['conditions']['condition-' + j.toString()];
                    if (next_condition === undefined){
                        break;
                    }
                }
                catch (e) {
                    console.log(e);
                    break;
                }

                // check if and/or are needed:
                if (j > 0){
                    var option_selected = stage_condition_connectors[j-1];
                    if (option_selected === "and"){
                        operator_html = "<div id='condition_id-" + condition_count.toString() + "'><div class=\"form-row\">\n" +
                            "                    <div class=\"form-group\">\n" +
                            "                        <select id=\"and_or_" + condition_count.toString() + "-" + stage_count + "\" name=\"and_or-" + stage_count + "\" class=\"form-control\">" +
                            "                            <option value=\"and\" selected>and</option>\n" +
                            "                            <option value=\"or\">or</option>\n" +
                            "                        </select>\n" +
                            "                    </div>\n" +
                            "                </div><br>";
                    }
                    else {
                        operator_html = "<div id='condition_id-" + condition_count.toString() + "'><div class=\"form-row\">\n" +
                            "                    <div class=\"form-group\">\n" +
                            "                        <select id=\"and_or_" + condition_count.toString() + "-" + stage_count + "\" name=\"and_or-" + stage_count + "\" class=\"form-control\">\n" +
                            "                            <option value=\"and\">and</option>\n" +
                            "                            <option value=\"or\" selected>or</option>\n" +
                            "                        </select>\n" +
                            "                    </div>\n" +
                            "                </div>\n" +
                            "\n" +
                            "                <br>";
                    }

                }

                // get condition values and types
                if (next_condition['constant_value_1'] !== ''){
                    var condition_value_1 = next_condition['constant_value_1'];
                    var value_type_1_options = '<option value="literal" selected>literal value</option><option value="field name" title="Gets the value of the field with the name attribute specified on the form.">field name</option>';
                }
                else{
                    var condition_value_1 = next_condition['field_name_1'];
                    var value_type_1_options = '<option value="literal">literal value</option><option selected value="field name" title="Gets the value of the field with the name attribute specified on the form.">field name</option>';
                }

                if (next_condition['constant_value_2'] !== ''){
                    var condition_value_2 = next_condition['constant_value_2'];
                    var value_type_2_options = '<option value="literal" selected>literal value</option><option value="field name" title="Gets the value of the field with the name attribute specified on the form.">field name</option>';
                }
                else{
                    var condition_value_2 = next_condition['field_name_2'];
                    var value_type_2_options = '<option value="literal">literal value</option><option selected value="field name" title="Gets the value of the field with the name attribute specified on the form.">field name</option>';
                }

                var remove_condition_button = "<div class=\"col-md-2\">\n" +
                                                "<div class=\"form-group form-inline\"><button type=\"button\" class=\"btn btn-danger\" id=\"remove_condition_btn_" + condition_count.toString() + "-" + stage_count + "\" onclick=\"remove_condition('" + condition_count.toString() +"', '" + stage_count.toString() +"')\">Remove Condition</button></div></div></div>";

                var operator_options = '<option value="is the same as">is the same as</option>' +
                                        '<option value="is not the same as">is not the same as</option>' +
                                        '<option value="is less than">is less than</option>' +
                                        '<option value="is greater than">is greater than</option>'+
                                        '<option value="is greater than or equal to">is greater than or equal to</option>' +
                                        '<option value="is less than or equal to">is less than or equal to</option>';

                operator_options = convert_to_have_selected(operator_options, next_condition['operator'].toString(), 8);

                stage_condition_html += operator_html + "<div class=\"form-row\">\n" +
                "                            <input readonly value=\"if\" class=\"form-control col-md-1\">\n" +
                "                            <input name=\"condition_value-" + stage_count + "\" class=\"form-control col-md-3\" value='" + condition_value_1 +"'>\n" +
                "                            <select name=\"operator-" + stage_count + "\" class=\"form-control col-md-2\">\n"
                    +
                    operator_options
                    +
                "                            </select>\n" +
                "                            <input name=\"condition_value-" + stage_count + "\" class=\"form-control col-md-3\" value='" + condition_value_2 + "'>\n" +
                "                   </div>\n" +
                "                        <div class=\"form-row\">\n" +
                "                            <input class=\"form-control col-md-1\" style=\"visibility: hidden\">\n" +
                "                            <select name=\"condition_value_type-" + stage_count + "\" class=\"form-control col-md-3\">\n" +
                                                value_type_1_options +
                "                            </select>\n" +
                "                            <input class=\"form-control col-md-2\" style=\"visibility: hidden\">\n" +
                "                            <select name=\"condition_value_type-" + stage_count + "\" class=\"form-control col-md-3\">\n" +
                                                value_type_2_options +
                "                            </select>\n" +
                "                   </div>\n" +
                "                    <br>" + remove_condition_button;
                condition_count += 1;
            }

            var add_and_clear_conditions_html = "<div class=\"col-md-2\">\n" +
                "                        <div class=\"form-group form-inline\">\n" +
                "                            <button type=\"button\" class=\"btn btn-secondary\" id=\"add_condition_btn-" + stage_count +"\" onclick=\"add_condition('" + stage_count.toString() +"')\">+ Add Condition</button> <!-- This is the add condition button -->\n" +
                "                        </div>\n" +
                "                    </div>\n" +
                "                    <div class=\"col-md-2\">\n" +
                "                        <div class=\"form-group form-inline\">\n" +
                "                            <button type=\"button\" class=\"btn btn-danger\" name='clear_conditions_btn' id=\"clear_conditions_btn-" + stage_count +"\" onclick=\"clear_conditions('" + stage_count.toString() +"')\" hidden>Remove All Conditions</button> <!-- This is the add condition button -->";

            var border_div = "<div style=\"border: 1px solid lightgrey; padding: 10px; margin: 10px;\" id=\"stage-" + stage_count +"\">";

            // when appended to stages, conditions html seems to have a comman in-between the stage_condition_html things, because stage_condition_html is an array.
            var conditions_html = "<h4>Conditions</h4><br><div id='conditions-" + stage_count + "'>" + stage_condition_html + "</div>" + add_and_clear_conditions_html + "</div>";

            var selected_approver_type = next_stage['stageApprover_roleID'];

            processApproversOptions = convert_to_have_selected(processApproversOptions, selected_approver_type, 7);

            var radio_options = "";
            if (next_stage['field_name'] !== ""){
                radio_options = "<input type=\"radio\" value='users data' name='get_approver_by-" + stage_count + "'> Users Data <br>" +
                    "<input type=\"radio\" value='field data' name='get_approver_by-" + stage_count + "' checked> Form Data from field with name attribute: " +
                    "<input name=\"field_name\" id=\"field_name\" placeholder=\"field name attribute\" value='" + next_stage['field_name'] + "'>";
            }
            else{
                radio_options = "<input type=\"radio\" value='users data' name='get_approver_by-" + stage_count + "' checked> Users Data <br>" +
                    "<input type=\"radio\" value='field data' name='get_approver_by-" + stage_count + "'> Form Data from field with name attribute: " +
                    "<input name=\"field_name\" id=\"field_name\" placeholder=\"field name attribute\" value='" + next_stage['field_name'] + "'>";
            }

            var approver_section_html_1 = "";
            var approver_section_html_2 = "";

            //if select is "Specific Person from Employees"
            if (selected_approver_type === 18) {
                let options = "";
                for (var key in employees) {
                    if (key === next_stage['field_name'])
                       options += "<option selected value=" + key + ">" + employees[key] + "</option>"
                    else
                        options += "<option value=" + key + ">" + employees[key] + "</option>"
                }

                approver_section_html_1 = "</div><h4>Approver</h4>\n" +
                    "                    <br>\n" +
                    "                    <!-- stage number--------------------------------------->\n" +
                    "                    <div class=\"form-row\">\n" +
                    "                            <div class=\"col-md-3\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <label class=\"form-label\" for=\"stage_number\">Stage Number</label>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                            <div class=\"col-md-1\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <input class=\"form-control\" type=\"number\" name=\"stage_number\" value='" + next_stage['stage'] + "'>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                        </div>\n" +
                    "                    <!-- approver role --------------------------------------->\n" +
                    "                    <div class=\"form-row\" id=\"select-row-" + stage_count + "\">\n" +
                    "                            <div class=\"col-md-3\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <label class=\"form-label\" for=\"processForm\">Approver Role</label>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                            <div class=\"col-md-4\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <select class=\"form-control \" data-size=\"10\" id='stageApprover-" + stage_count + "' name=\"stageApprover-" + stage_count + "\" onchange=\"select_approver($(this).prop('id'), $(this).find('option:selected').text())\" required>\n"
                    + processApproversOptions +
                    "                                    </select>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                        </div>\n" +
                       " <div class=\"form-row\" id=\"employee-row-" + stage_count + "\">\n" +
                        "                                <div class=\"col-md-3\">\n" +
                        "                                    <div class=\"form-group\">\n" +
                        "                                        <label class=\"form-label\" for=\"processForm\">Employee</label>\n" +
                        "                                    </div>\n" +
                        "                                </div>\n" +
                        "                                <div class=\"col-md-4\">\n" +
                        "                                    <div class=\"form-group\">\n" +
                        "                                        <select class=\"form-control\" data-size=\"10\" name=\"field_name\" required>\n" +
                                                                    options +
                        "                                        </select>\n" +
                        "                                    </div>\n" +
                        "                                </div>\n" +
                        "                            </div>\n" +
                                        "                    <!--Get Approver Based on------------------------------------------------>\n" +
                    "                    <div class=\"form-row\" id=\"based-row-" + stage_count + "\" style='display: none'>\n" +
                    "                            <div class=\"col-md-3\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <label class=\"form-label\" for=\"processForm\">Get Approver Based on</label>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                            <div class=\"col-md-4\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "<radiogroup name='get_approver_by-" + stage_count + "' >\n";

                // have to split approver section html into 2 parts otherwise the radio button options show up as NaN

                approver_section_html_2 = "\n</radiogroup>" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                        </div>\n" +
                    "<button type=\"button\" class=\"btn btn-danger\" name=\"remove_stage_btn\" id=\"remove_stage_btn-" + stage_count + "\" onclick=\"remove_stage('" + stage_count + "');\">Remove Stage</button>" +
                    "                    </div>";
            } else {
                approver_section_html_1 = "</div><h4>Approver</h4>\n" +
                    "                    <br>\n" +
                    "                    <!-- stage number--------------------------------------->\n" +
                    "                    <div class=\"form-row\">\n" +
                    "                            <div class=\"col-md-3\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <label class=\"form-label\" for=\"stage_number\">Stage Number</label>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                            <div class=\"col-md-1\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <input class=\"form-control\" type=\"number\" name=\"stage_number\" value='" + next_stage['stage'] + "'>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                        </div>\n" +
                    "                    <!-- approver role --------------------------------------->\n" +
                    "                    <div class=\"form-row\" id=\"select-row-" + stage_count + "\">\n" +
                    "                            <div class=\"col-md-3\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <label class=\"form-label\" for=\"processForm\">Approver Role</label>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                            <div class=\"col-md-4\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <select class=\"form-control \" data-size=\"10\" id='stageApprover-" + stage_count + "' name=\"stageApprover-" + stage_count + "\" onchange=\"select_approver($(this).prop('id'), $(this).find('option:selected').text())\" required>\n"
                    + processApproversOptions +
                    "                                    </select>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                        </div>\n" +
                    "                    <!--Get Approver Based on------------------------------------------------>\n" +
                    "                    <div class=\"form-row\" id=\"based-row-" + stage_count + "\">\n" +
                    "                            <div class=\"col-md-3\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "                                    <label class=\"form-label\" for=\"processForm\">Get Approver Based on</label>\n" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                            <div class=\"col-md-4\">\n" +
                    "                                <div class=\"form-group\">\n" +
                    "<radiogroup name='get_approver_by-" + stage_count + "' >\n";

                // have to split approver section html into 2 parts otherwise the radio button options show up as NaN

                approver_section_html_2 = "\n</radiogroup>" +
                    "                                </div>\n" +
                    "                            </div>\n" +
                    "                        </div>\n" +
                    "<button type=\"button\" class=\"btn btn-danger\" name=\"remove_stage_btn\" id=\"remove_stage_btn-" + stage_count + "\" onclick=\"remove_stage('" + stage_count + "');\">Remove Stage</button>" +
                    "                    </div>";
            }

            html_inside_stages_div.length = 0;

            html_inside_stages_div.push(border_div + conditions_html + approver_section_html_1 + radio_options + approver_section_html_2 + "</div>");


            // add html_inside_stages_div to stages div, then clear it for next round
            for (let j = 0; j < html_inside_stages_div.length; j++) {
                if (html_inside_stages_div[j] !== undefined &&
                    html_inside_stages_div[j] !== "undefined"){
                    $('#stages').append(html_inside_stages_div[j]);
                    // 'undefined' appears only after the html is appended to stages
                }
            }
            stage_count += 1;
            actual_stage_count += 1;
            html_inside_stages_div.length = 0;
            border_div = "";
            conditions_html = "";
            approver_section_html_1 = "";
            radio_options = "";
            approver_section_html_2 = "";
        }
        // vv this seems to remove the values inside proccess name and process description
        // remove_undefined();
        //
        // // vv have to do these last cuz otherwise it gets wiped out by remove_undefined
        document.getElementById("processName").value = response['js_context']['processType']['processName'];
        document.getElementById("processDesc").value = response['js_context']['processType']['processDesc'];
        //
        // $('#add_approvalprocess_btn').click(function () {
        //     let form = $('#stage_approvers');
        //     validate_and_collect_form_data(form, 'POST')
        // });
    }
    catch (e) {
        console.log(e);
        return "There was an error retrieving data for the process. Please contact IT";
    }

     $([document.documentElement, document.body]).animate({
        scrollTop: parseInt($("#add_approval_process").offset().top - 60)
    }, 500);

    return "Data Loaded Successfully";
}

function remove_undefined(){
   var whole_page = document.body.innerHTML;
   whole_page = whole_page.replace("undefined", "");
   document.body.innerHTML = whole_page;
}


function convert_to_have_selected(innerht, selected_value, difference){
    innerht = innerht.replace("selected", "");

    var option_index = parseInt(innerht.indexOf('<option value="' + selected_value + '"')) + difference;

    innerht = [innerht.slice(0, option_index), " selected ", innerht.slice(option_index)].join('');

    return innerht;
}

function update_clear_condition_buttons(){
    var clear_conditions_buttons = document.getElementsByName('clear_conditions_btn');
    for (let i = 0; i < clear_conditions_buttons.length; i++) {
        // check if there are any conditions for the stage
        var stage_id = clear_conditions_buttons[i].id.toString().split("-")[1];
        var condition_count_for_stage = document.getElementsByName('operator-'+stage_id).length;
        if (condition_count_for_stage > 0){
            clear_conditions_buttons[i].removeAttribute("hidden");
        }
    }
}

function add_condition(stage_count) {
    var stage_conditions = document.getElementsByName('operator-'+stage_count);
    var conditions_for_this_stage = stage_conditions.length;
    var and_or_condition = "";

    if (conditions_for_this_stage > 0){
         and_or_condition = "<div class=\"form-row\" id=\"select-row-" + stage_count + "\">\n" +
            "                    <div class=\"form-group\">\n" +
            "                        <select id=\"and_or_" + condition_count.toString() + "-" + stage_count + "\" name=\"and_or-" + stage_count + "\" class=\"form-control\">\n" +
            "                            <option value=\"and\">and</option>\n" +
            "                            <option value=\"or\">or</option>\n" +
            "                        </select>\n" +
            "                    </div>\n" +
            "                </div>\n" +
            "\n" +
            "                <br>";
    }

    var main_condition = "<div class=\"form-row\">\n" +
        "                            <input readonly value=\"if\" class=\"form-control col-md-1\">\n" +
        "                            <input name=\"condition_value-" + stage_count + "\" class=\"form-control col-md-3\">\n" +
        "                            <select name=\"operator-" + stage_count + "\" class=\"form-control col-md-2\">\n" +
        "                                <option value=\"is the same as\">is the same as</option><option value=\"is not the same as\">is not the same as</option><option value=\"is less than\">is less than</option><option value=\"is greater than\">is greater than</option><option value=\"is greater than or equal to\">is greater than or equal to</option><option value=\"is less than or equal to\">is less than or equal to</option>\n" +
        "                            </select>\n" +
        "                            <input name=\"condition_value-" + stage_count + "\" class=\"form-control col-md-3\">\n" +
        "                   </div>\n" +
        "                        <div class=\"form-row\">\n" +
        "                            <input class=\"form-control col-md-1\" style=\"visibility: hidden\">\n" +
        "                            <select name=\"condition_value_type-" + stage_count + "\" class=\"form-control col-md-3\">\n" +
        "                                <option value=\"literal\">literal value</option>\n" +
        "                                <option selected value=\"field name\" title=\"Gets the value of the field with the name attribute specified on the form.\">field name</option>\n" +
        "                            </select>\n" +
        "                            <input class=\"form-control col-md-2\" style=\"visibility: hidden\">\n" +
        "                            <select name=\"condition_value_type-" + stage_count + "\" class=\"form-control col-md-3\">\n" +
        "                                <option value=\"literal\">literal value</option>\n" +
        "                                <option value=\"field name\" title=\"Gets the value of the field with the name attribute specified on the form.\">field name</option>\n" +
        "                            </select>\n" +
        "                   </div>\n" +
        "                    <br>";

    var remove_condition_button = "<div class=\"col-md-2\">\n" +
        "                        <div class=\"form-group form-inline\"><button type=\"button\" class=\"btn btn-danger\" id=\"remove_condition_btn_" + condition_count + "-" + stage_count + "\" onclick=\"remove_condition('" + condition_count.toString() +"', '" + stage_count.toString() +"')\">Remove Condition</button></div></div>";


    $("#conditions-"+ stage_count).append("<div id='condition_id-" + condition_count + "'>" + and_or_condition + main_condition + remove_condition_button);

    document.getElementById("clear_conditions_btn-"+stage_count).removeAttribute('hidden');

    condition_count += 1;
}


function clear_conditions(stage_count) {
    swal.fire({
        title: "Are you sure?",
        text: "If you proceed, all of the conditions for this stage will be cleared.",
        icon: "warning",
        showCancelButton: true,
        cancelButtonText: 'Cancel',
        confirmButtonText: 'Clear Anyway'
        }).then((result) => {
            if (result.value) {
                document.getElementById("conditions-" + stage_count).innerHTML = "";
                //document.getElementById("clear_conditions_btn-"+stage_count).setAttribute('hidden', true);
            }
        }
    );
}

function remove_condition(condition_id, stage_count){
    swal.fire({
        title: "Are you sure?",
        text: "Are you sure you want to remove this condition from the stage?",
        icon: "warning",
        showCancelButton: true,
        cancelButtonText: 'Cancel',
        confirmButtonText: 'Remove'
        }).then((result) => {
            if (result.value) {
                document.getElementById("condition_id-" + condition_id).innerHTML = "";

                // If the condition id is the highest for this stage, then remove the and/or underneath it.
                // and_or_(lowest_condition_id_for_stage)-(stage_count)

                var lowest_existing_condition_id_for_stage =  get_lowest_condition_id_for_stage(stage_count);
                if (lowest_existing_condition_id_for_stage > parseInt(condition_id)){
                    $("#and_or_" + lowest_existing_condition_id_for_stage.toString() + "-" + stage_count).remove();
                }

            }

        }
    );
}


function get_lowest_condition_id_for_stage(stage_count){
    var all_and_ors = document.getElementsByName('and_or-' + stage_count);
    var lowest_condition_id = -1;

    for (let i = 0; i < all_and_ors.length; i++) {

            var first_cut = all_and_ors[i].id.toString().split("_")[all_and_ors[i].id.toString().split("_").length - 1];
            var second_cut = first_cut.split("-")[0];


            if (lowest_condition_id !== -1){
                if (parseInt(second_cut) < lowest_condition_id){
                    lowest_condition_id = parseInt(second_cut);
                }
            }
            else{
                lowest_condition_id = parseInt(second_cut);
            }
    }

    return lowest_condition_id;
}


function remove_stage(stage_count) {
    document.getElementById("stage-"+stage_count).remove();
    actual_stage_count -= 1;
    if (actual_stage_count === 1){
        var delete_buttons =  document.getElementsByName("remove_stage_btn");
        for (let i = 0; i < delete_buttons.length; i++) {
            delete_buttons[i].setAttribute("hidden", true);
        }
    }
}


function add_stage() {
    actual_stage_count += 1;
    stage_count += 1;

    var new_stage = "<div style=\"border: 1px solid lightgrey; padding: 10px; margin: 10px;\" id=\"stage-" + stage_count +"\">\n" +
        "                    <!-- condition information section -->\n" +
        "                    <h4>Conditions</h4>\n" +
        "                    <br>\n" +
        "    \n" +
        "                    <div id=\"conditions-" + stage_count +"\"> <!-- This div will contain all conditions for the approver to appear in the process -->\n" +
        "                        \n" +
        "                    </div><!-- end conditions div -->\n" +
        "    \n" +
        "                    <div class=\"col-md-2\">\n" +
        "                        <div class=\"form-group form-inline\">\n" +
        "                            <button type=\"button\" class=\"btn btn-secondary\" id=\"add_condition_btn-" + stage_count +"\" onclick=\"add_condition('" + stage_count.toString() +"')\">+ Add Condition</button> <!-- This is the add condition button -->\n" +
        "                        </div>\n" +
        "                    </div>\n" +
        "                    <div class=\"col-md-2\">\n" +
        "                        <div class=\"form-group form-inline\">\n" +
        "                            <button type=\"button\" class=\"btn btn-danger\" name='clear_conditions_btn' id=\"clear_conditions_btn-" + stage_count +"\" onclick=\"clear_conditions('" + stage_count.toString() +"')\" hidden>Remove All Conditions</button> <!-- This is the add condition button -->\n" +
        "                        </div>\n" +
        "                    </div>\n" +
        "    \n" +
        "                    <!-- approver information section -->\n" +
        "                    <h4>Approver</h4>\n" +
        "                    <br>\n" +
        "                    <!-- stage number--------------------------------------->\n" +
        "                    <div class=\"form-row\">\n" +
        "                            <div class=\"col-md-3\">\n" +
        "                                <div class=\"form-group\">\n" +
        "                                    <label class=\"form-label\" for=\"stage_number\">Stage Number</label>\n" +
        "                                </div>\n" +
        "                            </div>\n" +
        "                            <div class=\"col-md-1\">\n" +
        "                                <div class=\"form-group\">\n" +
        "                                    <input class=\"form-control\" type=\"number\" name=\"stage_number\" required>\n" +
        "                                </div>\n" +
        "                            </div>\n" +
        "                        </div>\n" +
        "                    <!-- approver role --------------------------------------->\n" +
        "                    <div class=\"form-row\" id=\"select-row-" + stage_count + "\">\n" +
        "                            <div class=\"col-md-3\">\n" +
        "                                <div class=\"form-group\">\n" +
        "                                    <label class=\"form-label\" for=\"processForm\">Approver Role</label>\n" +
        "                                </div>\n" +
        "                            </div>\n" +
        "                            <div class=\"col-md-4\">\n" +
        "                                <div class=\"form-group\">\n" +
        "                                    <select class=\"form-control \" data-size=\"10\" id='stageApprover-" + stage_count + "' name=\"stageApprover-" + stage_count + "\" onchange=\"select_approver($(this).prop('id'), $(this).find('option:selected').text())\" required>\n"
                                                + processApproversOptions +
        "                                    </select>\n" +
        "                                </div>\n" +
        "                            </div>\n" +
        "                        </div>\n" +
        "                    <!--Get Approver Based on------------------------------------------------>\n" +
        "                    <div class=\"form-row\" id=\"based-row-" + stage_count + "\">\n" +
        "                            <div class=\"col-md-3\">\n" +
        "                                <div class=\"form-group\">\n" +
        "                                    <label class=\"form-label\" for=\"processForm\">Get Approver Based on</label>\n" +
        "                                </div>\n" +
        "                            </div>\n" +
        "                            <div class=\"col-md-4\">\n" +
        "                                <div class=\"form-group\">\n" +
        "<radiogroup name='get_approver_by-" + stage_count + "'>" +
        "                                    <input type=\"radio\" value='users data' name='get_approver_by-" + stage_count + "' checked> Users Data <br>\n" +
        "                                    <input type=\"radio\" value='field data' name='get_approver_by-" + stage_count + "'> Form Data from field with name attribute: <input name=\"field_name\" id=\"field_name\" placeholder=\"field name attribute\">\n" +
        "</radiogroup>" +
        "                                </div>\n" +
        "                            </div>\n" +
        "                        </div>\n" +
        "<button type=\"button\" class=\"btn btn-danger\" name=\"remove_stage_btn\" id=\"remove_stage_btn-" + stage_count +"\" onclick=\"remove_stage('" + stage_count + "');\">Remove Stage</button>" +
        "                    </div>";

        $("#stages").append(new_stage);

        var delete_buttons =  document.getElementsByName("remove_stage_btn");
        for (let i = 0; i < delete_buttons.length; i++) {
            delete_buttons[i].removeAttribute("hidden");
        }
}

$(function () {
    $('.selectpicker').selectpicker();
})



