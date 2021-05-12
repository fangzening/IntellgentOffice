// Author: Corrina Barr
// This has a lot of parameters, but it's better than writing similar code over and over again
// Should work for all sections of TR that need popups
// column headers and column filed names are parallel arrays so make sure the indexes of the headers match up with the indexes of the column filed names

function create_section_popup(id_num, column_headers, column_field_names, subtotal_name, there_is_perdiem, modal_base_name, div_id_where_sections_popups_go, there_is_file_field, perdiem_base_name, overall_heading){
    var master_div = document.getElementById(div_id_where_sections_popups_go);
    var column_headers_html = "";
    var normal_fields_html = "";
    var perdiem_html = "";
    subtotal_name = modal_base_name + "_subtotal";
    var file_html = "";
    var mileage_sub_html = "";
    var file_number = document.getElementById("number_of_mileage_weeks").value;
    var sub_cols = '3';

    if (there_is_file_field){
        var sub_mileage_id = "sub_mileage_unsaved_" + id_num;
        mileage_sub_html = "<td>\n" +
            "                                                            <span class=\"input-group-text\"\n" +
            "                                                                  id=\"basic-addon1\"> Total Mileage:</span>\n" +
            "\n" +
            "                                                        </td>\n" +
            "                                                        <td colspan=\"1\">\n" +
            "                                                            <input class=\"multisteps-form__input form-control subtotal\"\n" +
            "                                                                   id=\"sub_mileage_unsaved_" + id_num + "\" name=\"sub_mileage\"\n" +
            "                                                                   type=\"text\" readonly/>\n" +
            "                                                        </td>";
        sub_cols = 2;
    }


    for (let i = 0; i < column_headers.length; i++) {
        column_headers_html += "<th>" + column_headers[i] + "</th>";
    }


    for (let i = 0; i < 7; i++) {
        normal_fields_html += "<tr>";
        for (let j = 0; j < column_field_names.length; j++) {
            if (column_field_names[j].includes('date')){
                normal_fields_html += "<td>\n" +
                    "<input class=\"form-control\" type=\"date\" id=\"" + column_field_names[j] + "_" + i.toString() +  "_unsaved_" + id_num + "\"\n" +
                    "name=\"" + column_field_names[j] + "\" readonly>\n" +
                    "</td>"
            }
            else{
                if (column_field_names[j] !== 'departure_from' && column_field_names[j] !== 'destination_to'){
                    normal_fields_html += "<td><input maxlength='6' type=\"text\" class=\"form-control numberinput\"\n" +
                                    "name=\"" + column_field_names[j] + "\" id=\"" + column_field_names[j] + "_" + i.toString() +  "_unsaved_" + id_num + "\"\n" +
                                    "></td>";
                }
                else{
                    normal_fields_html += "<td><input maxlength='6' type=\"text\" class=\"form-control\"\n" +
                                    "name=\"" + column_field_names[j] + "\" id=\"" + column_field_names[j] + "_" + i.toString() +  "_unsaved_" + id_num + "\"\n" +
                                    "></td>";
                }

            }
        }
        normal_fields_html += "</tr>";
    }


    if (there_is_perdiem){
        perdiem_html = "<tr>" +
            "<td colspan='3'>" +
            "<b>-OR-</b>" +
            "</td>" +
            "</tr>";

        for (let i = 0; i < 7; i++) {
            var day = i+1;
            perdiem_html +=
                "<tr>\n" +
            "<td>\n" +
            "<span class=\"input-group-text\"\n" +
            "id=\"basic-addon1\">Per Diem Day " + day.toString() + ":</span>\n" +
            "\n" +
            "</td>\n" +
            "<td colspan=\"2\">\n" +
            "<input maxlength='6' class=\"multisteps-form__input form-control numberinput\"\n" +
            "id=\"" + perdiem_base_name + "_" + i.toString() + "_unsaved_" + id_num +"\" name=\""+ perdiem_base_name +"\"\n" +
            "type=\"text\"/>\n" +
            "</td>\n" +
            "<td>\n" +
            "<input class=\"form-control\" type=\"date\" readonly id=\"" + perdiem_base_name + "_date_" + i.toString() + "_unsaved_" + id_num + "\"\n" +
            "name=\"" + perdiem_base_name + "_date\">\n" +
            "</td>\n" +
            "\n" +
            "</tr>";
        }
    }


    var new_popup = "<div class=\"modal fade\" id=\"" + modal_base_name + "_unsaved_" + id_num + "\" tabindex=\"-1\" role=\"dialog\"\n" +
        "                                     aria-labelledby=\"ModalCenterTitle\" aria-hidden=\"true\">\n" +
        "                                    <div class=\"modal-dialog modal-dialog-centered modal-lg\" role=\"document\">\n" +
        "                                        <div class=\"modal-content\">\n" +
        "                                            <div class=\"modal-header\">\n" +
        "                                                <h5 class=\"modal-title\" id=\"exampleModalLongTitle\">"+ overall_heading+"\n" +
        "                                                    </h5>\n" +
        "                                                <button type=\"button\" class=\"close\" data-dismiss=\"modal\"\n" +
        "                                                        aria-label=\"Close\">\n" +
        "                                                    <span aria-hidden=\"true\">&times;</span>\n" +
        "                                                </button>\n" +
        "                                            </div>\n" +
        "                                            <div class=\"modal-body\">\n" +
        "                                                <table class=\"table\" id=\"expense_meal_table\">\n" +
        "                                                    <thead>\n" +
        "                                                    <tr>\n" +
        "\n"                                            + column_headers_html +
        "                                                    </tr>\n" +
        "                                                    </thead>\n" +
        "                                                    <tbody id=\"tableadd\">\n" +
        "                                              "  + normal_fields_html +
        "<tr>\n" +
        "                                                        " + perdiem_html +
        "\n" +
        "                                                    </tbody>\n" +
        "                                                    <tfoot>\n" +
        "\n" +
        "                                                    <tr>\n" +
        "                                                        <td>\n" +
        "                                                            <span class=\"input-group-text\"\n" +
        "                                                                  id=\"basic-addon1\">Sub Total $:</span>\n" +
        "\n" +
        "                                                        </td>\n" +
        "                                                        <td colspan=\""+ sub_cols +"\">\n" +
        "                                                            <input class=\"multisteps-form__input form-control subtotal\"\n" +
        "                                                                   id=\"" + subtotal_name + "_unsaved_" + id_num + "\" name=\"" + subtotal_name + "\"\n" +
        "                                                                   type=\"text\" readonly/>\n" +
        "                                                        </td>\n" + mileage_sub_html +
        "\n" +
        "                                                    </tr>\n" + file_html +
        "\n" +
        "                                                    </tfoot>\n" +
        "                                                </table>\n" +
        "\n" +
        "                                            </div>\n" +
        "                                            <div class=\"modal-footer\">\n" +
        "                                                <button type=\"submit\" class=\"btn btn-success\" data-dismiss=\"modal\">Done\n" +
        "                                                </button>\n" +
        "                                            </div>\n" +
        "                                        </div>\n" +
        "                                    </div>\n" +
        "                                </div>";

    $('#re_form').append(new_popup);
    limitInput();
    set_up_sum_calculations();
}


function create_bee_popup(field_specifics) {
    var new_bee_popup = "<div class=\"modal fade\" id=\"Bee_Modal" + field_specifics + "\" tabindex=\"-1\" role=\"dialog\"\n" +
        "                                     aria-labelledby=\"ModalCenterTitle\" aria-hidden=\"true\">\n" +
        "                                    <div class=\"modal-dialog modal-dialog-centered modal-lg\" role=\"document\">\n" +
        "                                        <div class=\"modal-content\">\n" +
        "                                            <div class=\"modal-header\">\n" +
        "                                                <h5 class=\"modal-title\" id=\"exampleModalLongTitle\">Business Expense\n" +
        "                                                    Explaination </h5>\n" +
        "                                                <button type=\"button\" class=\"close\" data-dismiss=\"modal\"\n" +
        "                                                        aria-label=\"Close\">\n" +
        "                                                    <span aria-hidden=\"true\">&times;</span>\n" +
        "                                                </button>\n" +
        "                                            </div>\n" +
        "                                            <div class=\"modal-body\">\n" +
        "                                                <div class=\"card col-12\">\n" +
        "                                                    <h5 class=\"card-header\" style=\"background: #2b5797; color: #ffffff\">\n" +
        "                                                        Expense Explaination\n" +
        "                                                    </h5>\n" +
        "                                                    <div class=\"card-body \">\n" +
        "\n" +
        "                                                        <table class=\"table\" id=\"business_expense_explaination"+ field_specifics + "\">\n" +
        "\n" +
        "                                                            <tbody id=\"tableadd_business_expense_popup" + field_specifics + "\">\n" +
        "                                                            <tr>\n" +
        "                                                                <td>\n" +
        "                                                                <span class=\"input-group-text\"\n" +
        "                                                                      id=\"basic-addon1\">Amount:</span>\n" +
        "                                                                </td>\n" +
        "                                                                <td>\n" +
        "                                                                    <input type=\"text\" class=\"form-control numberinput\"\n" +
        "                                                                           name=\"business_expense_amount\"\n" +
        "                                                                           id=\"business_expense_amount" + field_specifics +"\"\n" +
        "                                                                           ></td>\n" +
        "                                                                </td>\n" +
        "                                                                <td>\n" +
        "                                                                <span class=\"input-group-text\"\n" +
        "                                                                      id=\"basic-addon1\">Place:</span>\n" +
        "                                                                </td>\n" +
        "\n" +
        "                                                                <td>\n" +
        "                                                                    <input type=\"text\" class=\"form-control\"\n" +
        "                                                                           id=\"business_expense_place" + field_specifics +"\"\n" +
        "                                                                           name=\"business_expense_place\"\n" +
        "                                                                           ></td>\n" +
        "                                                                </td>\n" +
        "                                                            </tr>\n" +
        "\n" +
        "\n" +
        "                                                            <tr>\n" +
        "                                                                <td>\n" +
        "                                                                    <span class=\"input-group-text\" id=\"basic-addon1\">Purpose:</span>\n" +
        "                                                                </td>\n" +
        "\n" +
        "\n" +
        "                                                                <td colspan=\"3\">\n" +
        "                                                                <textarea class=\"form-control subtotal\"\n" +
        "                                                                          id=\"business_expense_purpose" + field_specifics + "\"\n" +
        "                                                                          name=\"business_expense_purpose\"\n" +
        "                                                                         onchange=\"update_purpose('"+ field_specifics + "')\"></textarea>\n" +
        "\n" +
        "                                                                </td>\n" +
        "                                                            </tr>\n" +
        "\n" +
        "\n" +
        "                                                            <tr>\n" +
        "                                                                <td>\n" +
        "                                                                <span class=\"input-group-text\"\n" +
        "                                                                      id=\"basic-addon1\">Detail:</span>\n" +
        "                                                                </td>\n" +
        "\n" +
        "\n" +
        "                                                                <td colspan=\"3\">\n" +
        "                                                                <textarea class=\"form-control\"\n" +
        "                                                                          id=\"business_expense_detail"+ field_specifics +"\"\n" +
        "                                                                          name=\"business_expense_detail\"\n" +
        "                                                                         ></textarea>\n" +
        "\n" +
        "                                                                </td>\n" +
        "                                                            </tr>\n" +
        "\n" +
        "\n" +
        "                                                            </tbody>\n" +
        "                                                            <tfoot>\n" +
        "                                                            <tr>\n" +
        "                                                                <td>\n" +
        "                                                                    <span class=\"input-group-text\" id=\"basic-addon1\">Counter Party :</span>\n" +
        "                                                                </td>\n" +
        "                                                                <td colspan=\"4\">\n" +
        "                                                                    <input type=\"text\" class=\"form-control\"\n" +
        "                                                                           id=\"business_expense_counterparty" + field_specifics +"\"\n" +
        "                                                                           name=\"business_expense_counterparty\"\n" +
        "                                                                           ></td>\n" +
        "                                                            </tr>\n" +
        "\n" +
        "                                                            <tr>\n" +
        "                                                                <td>\n" +
        "                                                                <span class=\"input-group-text\"\n" +
        "                                                                      id=\"basic-addon1\">Name:</span>\n" +
        "                                                                </td>\n" +
        "                                                                <td>\n" +
        "                                                                    <input type=\"text\" class=\"form-control\" id=\"business_expense_name" + field_specifics + "\"\n" +
        "                                                                           name=\"business_expense_name\"\n" +
        "                                                                           >\n" +
        "                                                                </td>\n" +
        "                                                                </td>\n" +
        "                                                                <td>\n" +
        "                                                                <span class=\"input-group-text\"\n" +
        "                                                                      id=\"basic-addon1\">Title:</span>\n" +
        "                                                                </td>\n" +
        "\n" +
        "                                                                <td>\n" +
        "                                                                    <input type=\"text\" class=\"form-control\" id=\"bsiness_expense_title" + field_specifics + "\"\n" +
        "                                                                           name=\"business_expense_title\"\n" +
        "                                                                           ></td>\n" +
        "                                                                </td>\n" +
        "                                                            </tr>\n" +
        "\n" +
        "                                                            </tfoot>\n" +
        "                                                        </table>\n" +
        "                                                    </div>\n" +
        "                                                </div>\n" +
        "                                                <div class=\"modal-footer\">\n" +
        "                                                    <button type=\"button\" class=\"btn btn-secondary\"\n" +
        "                                                            data-dismiss=\"modal\">\n" +
        "                                                        Close\n" +
        "                                                    </button>\n" +
        "                                                </div>\n" +
        "                                            </div>\n" +
        "                                        </div>\n" +
        "                                    </div>\n" +
        "                                </div>";

    $('#re_form').append(new_bee_popup);
}