// This file has javascript by Corrina for the PR form


/************************************************************************************************************************************/
// START VALUE-CHANGING FUNCTIONS
/************************************************************************************************************************************/


function update_following_assets(prefix, elementName){
    var new_value = document.getElementById(prefix + "_1").value;
    var all_asset_values_with_same_name = document.getElementsByName(elementName);

    for (let i = 0; i < all_asset_values_with_same_name.length; i++) {
        if (all_asset_values_with_same_name[i].id.includes(prefix)){
            all_asset_values_with_same_name[i].value = new_value;
        }
    }
}

// This function helps post data know what checkboxes are checked
function update_checkbox(item_id){
    var is_on = document.getElementById("item_checkbox_"+item_id).checked;
    var input_to_update = document.getElementById("item_checkbox_value_"+item_id);
    if (is_on){
        input_to_update.value='on';
    }
    else{
        input_to_update.value='off';
    }
}

// This function changes the vendor code fields on the first page of the PR
function change_vendor(vendorCode, contact, address){
    console.log("setting vendor code: " + vendorCode);
    document.getElementById('vendor_code').value = vendorCode;

    console.log("setting contact: " + contact);
    document.getElementById('contact').value = contact;

    console.log("setting address: " + address);
    document.getElementById('address').value = address;
}


// This function updates the vendor information when a new vendor is selected on the PR
function update_vendor(){
    var select_box = document.getElementById('vendor_name');
    var selected_option = select_box.options[select_box.selectedIndex];
    console.log("selected option: " + selected_option.toString());
    console.log("option name: " + selected_option.id.toString());

    var broken_parameters = selected_option.id.split("/-/");
    console.log("Broken Parameters: " + broken_parameters.toString());

    change_vendor(broken_parameters[0], broken_parameters[1], broken_parameters[2]);
}

function update_plant_code(){
    var select_box = document.getElementById('business_unit');
    var selected_option = select_box.options[select_box.selectedIndex];
    var splitted_values = selected_option.id.toString().split("//");
    document.getElementById('plant_code').value = splitted_values[0];
    document.getElementById('business').value = splitted_values[1];
    document.getElementById('company').value = splitted_values[2];
}

function update_gl_descriptions(){
    var gl_accounts = document.getElementsByName('gl_account');
    for (let i = 0; i < gl_accounts.length; i++) {
        var desc_val = $('#' + gl_accounts[i].id.toString()).children("option:selected").val();

        var last_part_of_id = gl_accounts[i].id.toString().split('_')[gl_accounts[i].id.toString().split('_').length - 1 ];

        var desc_id = "gl_description_" + last_part_of_id;

        document.getElementById(desc_id).value = desc_val;

        widthauto(document.getElementById(desc_id));
        widthauto(gl_accounts[i]);
    }
}

function update_cost_center_code(){
    var cost_centers = document.getElementsByName('department');
    console.log("cost centers: " + cost_centers.toString());

    for (let i = 0; i < cost_centers.length; i++) {
        var chosen_option = $('#' + cost_centers[i].id.toString()).children("option:selected");
        var desc_val = chosen_option.attr("title");

        var last_part_of_id = cost_centers[i].id.toString().split('_')[cost_centers[i].id.toString().split('_').length - 1 ];

        var desc_id = "cost_center_" + last_part_of_id;

        document.getElementById(desc_id).value = desc_val;
        console.log("description id: " + desc_id.toString());
        console.log("new value: " + desc_val.toString());

        widthauto(document.getElementById(desc_id));
        widthauto(cost_centers[i]);
    }
}

// Gives all fields that currently have numberinput class when it is called forceNumeric
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



// This function makes it so the form can tell which submit button was chosen
function set_submit_button(button_chosen){
    document.getElementById('submit_button').value = button_chosen;
    return true
}

function make_fields_readonly(details_to_edit, rows_to_edit_pks, user_dept){
    // details_to_edit is an array pks of item details user can edit
    var editable_unit_price_ids = [];
    var editable_accountant_field_ids = [];

    if (details_to_edit !== null){
        //console.log("details to edit: " + details_to_edit.toString());
        for (let i = 0; i < details_to_edit.length; i++) {
            var unit_price_id = "unit_price_0" + details_to_edit[i];
            var material_id = "material_group_0" + details_to_edit[i];
            editable_unit_price_ids.push(unit_price_id);
            editable_unit_price_ids.push(material_id);
        }
    }
    //console.log("editable unit price ids: " + editable_unit_price_ids.toString());

    if (rows_to_edit_pks !== null && user_dept === "Supporting - Accounting"){
        for (let i = 0; i < rows_to_edit_pks.length; i++) {
            var asset_num_id = "asset_number_0" + rows_to_edit_pks[i].toString();
            editable_accountant_field_ids.push(asset_num_id);
            var gl_account_select = "gl_account_0" + rows_to_edit_pks[i].toString();
            editable_accountant_field_ids.push(gl_account_select);
            var gl_account_desc = "gl_description_0" + rows_to_edit_pks[i].toString();
            editable_accountant_field_ids.push(gl_account_desc);

            // Include asset class, tech categories 1-4
            var editable_accountant_asset_names = ['asset_class', 'tech_category1', 'tech_category2', 'tech_category3', 'tech_category4'];
            for (let j = 0; j < editable_accountant_asset_names.length; j++) {
                var elements_to_check = document.getElementsByName(editable_accountant_asset_names[j]);
                for (let k = 0; k < elements_to_check.length; k++) {
                    console.log('check if ' + elements_to_check[k].id + " includes 0" + rows_to_edit_pks[i]);
                    if (elements_to_check[k].id.toString().includes("0"+rows_to_edit_pks[i])){
                        if (editable_accountant_field_ids.includes(elements_to_check[k].id) === false){
                            console.log("ADDING " + elements_to_check[k].id + " to editable accountant field ids");
                            editable_accountant_field_ids.push(elements_to_check[k].id);
                        }
                    }
                }
            }
        }
    }

    var input_fields = document.getElementsByTagName("input");
    for (let i = 0; i < input_fields.length; i++) {
        if (input_fields[i].id !== 'email'){
            if (editable_unit_price_ids.includes(input_fields[i].id) === false && input_fields[i].name !== 'approver_check' && editable_accountant_field_ids.includes(input_fields[i].id) === false){
                input_fields[i].setAttribute("readonly", "true");
            }
        }
        else{
            if (details_to_edit === null){
                input_fields[i].setAttribute("readonly", "true");
            }
        }

    }

    var select_boxes = document.getElementsByTagName("select");
    for (let i = 0; i < select_boxes.length; i++) {
        if (select_boxes[i].id !== 'vendor_name'){

                if (editable_accountant_field_ids.includes(select_boxes[i].id) === false){
                    select_boxes[i].setAttribute("hidden", "true");
                    // Insert after each select box an input field holding the data of the select box
                    var select_id = select_boxes[i].id;
                    var select_value = $('#' + select_id).find(":selected").val();
                    var input_id = "input_" + select_id;
                    if (input_id.includes('department') === false) {
                        $("<input value='" + select_value + "' id='" + input_id + "' class='form-control' readonly>").insertAfter('#'+select_id.toString());
                    }
                    else{
                        var item_id = select_id.split("_")[1];
                         // find cost center code and see if it is hidden. if it is, make the dept input readonly too. else just leave it alone
                        if (document.getElementById('cost_center_' + item_id).getAttribute('hidden') !== null){
                            $("<input value='" + select_value + "' id='" + input_id + "' class='form-control' readonly hidden>").insertAfter('#'+select_id.toString());
                        }
                        else{
                            $("<input value='" + select_value + "' id='" + input_id + "' class='form-control' readonly>").insertAfter('#'+select_id.toString());
                        }
                    }
                }
            }
        else{
            if (details_to_edit === null){
                var select_id = select_boxes[i].id;
                var select_value = $('#' + select_id).find(":selected").text();
                var input_id = "input_" + select_id;
                console.log("showing input box");
                $("<input value='" + select_value + "' id='" + input_id + "' class='form-control' readonly>").insertAfter('#'+select_id.toString());
            }
        }

    }

    // var memo = document.getElementById("memo");
    // for (let i = 0; i < memo.length; i++) {
    //     if (memo[i].id.toString() !== 'chat-input'){
    //         memo[i].setAttribute("readonly", true);
    //     }
    // }
    // document.getElementById('upload_more_files_div').hidden = true;
}


// Calculates an item amount for the row number specified
function calculate_item_amount(row_num){
    console.log("checking id: " + "quantity_" + row_num);
    var quantity = document.getElementById("quantity_" + row_num).value;
    var unit_price = document.getElementById("unit_price_" + row_num).value;
    var item_amount = 0.00;
    if (quantity !== "" && unit_price !== ""){
        item_amount = (parseFloat(quantity) * parseFloat(unit_price)).toFixed(2);
    }
    document.getElementById("amount_" + row_num).value = item_amount;
    update_subtotal();
}

// updates subtotal
function update_subtotal(){
    var subtotal = 0.00;
    var item_amounts = document.getElementsByName('amount');
    for (let i = 0; i < item_amounts.length; i++) {
        try{
            subtotal += parseFloat(item_amounts[i].value);
        }
        catch (e) {
            subtotal += 0.00;
        }
    }
    document.getElementById('form_total').value = subtotal;
}

/************************************************************************************************************************************/
// END VALUE-CHANGING FUNCTIONS
/************************************************************************************************************************************/




//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




/************************************************************************************************************************************/
// START JQEURY AJAX SECTION
/************************************************************************************************************************************/
// corrina Validation function
function validate_pr(user_is_buyer){
    var error_message = [];

    if (user_is_buyer){
        var necesary_ids = ['vendor_name', 'email'];

        // Name in necesary names do not need to exist, but if they do they must be filled out
        var necesary_names = ['unit_price', 'quantity', 'amount'];
    }
    else{
        var necesary_ids = ['company', 'business', 'business_unit', 'plant_code', 'project', 'purpose',
        'shipping_name', 'shipping_address', 'currency'];

        // Name in necesary names do not need to exist, but if they do they must be filled out
        var necesary_names = ['unit_price', 'quantity', 'amount', 'item_description', 'department', 'cost_center', 'quantity',
                            'arrival_date', 'unit_of_measurement', 'material_group'];
    }


    for (let i = 0; i < necesary_ids.length; i++) {
        if (document.getElementById(necesary_ids[i]).value === "" || document.getElementById(necesary_ids[i]).value === null){
            error_message.push(necesary_ids[i].toString().replace("_", " ") + " must be filled out!");
        }
    }

    for (let i = 0; i < necesary_names.length; i++) {
        var names_of_this_name_are_all_filled = true;
        var current_names_list = document.getElementsByName(necesary_names[i]);
        for (let j = 0; j < current_names_list.length; j++) {
            if (current_names_list[j].value === "" || current_names_list[j].value === null){
                names_of_this_name_are_all_filled = false;
            }
            if (names_of_this_name_are_all_filled === false){
                error_message.push(necesary_names[i].toString().replace("_", " ") + " must be filled out!");
            }
        }
    }

    // Check if email has email value:
    if (user_is_buyer){
        var email_field_value = document.getElementById("email").value;
        if (email_field_value.includes(".") === false || email_field_value.includes("@") === false){
            error_message.push("Supplier email must be a valid email address!")
        }
    }


    return error_message
}

// What happens when form submits:
var frm = $('#msform');
    frm.submit(function () {

        var submit_action = document.getElementById('submit_button').value;
        var title = "";

        if (submit_action === 'Approve Selected Items'){
            // Check to see if any items are selected
            var selected_items = document.getElementsByName('item_checkbox');
            var any_items_selected = false;
            for (let i = 0; i < selected_items.length; i++) {
                if (selected_items[i].checked === true){
                    any_items_selected = true;
                    break;
                }
            }
            if (any_items_selected === false) {
                swal.fire({
                    title: "No Items Selected!",
                    icon: "warning",
                    text: "There are no items selected for approval! Please select the items you want to approve and then try again.",
                    buttons: {
                                cancel: "Ok"
                            }
                });
                    return false;
            }
            title="Saving Action Taken...";
        }
        else if (submit_action === 'Finish' || submit_action === 'Save and Submit form for approval'){
            if (submit_action === 'Finish'){
                title = "Form is Submitting...";
                var error_msg = validate_pr(false);
            }
            else{
                title="Saving Action Taken...";
                var error_msg = validate_pr(true);
            }

            if (error_msg.length > 0)
            {
                var error_message = "";
                for (let i = 0; i < error_msg.length; i++) {
                    error_message += "\n" + error_msg[i];
                }
                swal.fire({
                    title: "Please fix these issues before submitting",
                    icon: "warning",
                    text: error_message,
                    buttons: {
                                cancel: "Ok"
                            }
                });
                    return false;
            }



        }
        else if (submit_action === "Save" || submit_action.includes("Save Unit Price") || submit_action.includes('Accounting Save')) {
            title = "Form is Saving...";
        }
        else if (submit_action === "Upload Chosen File") {
            title = "Uploading File...";
        }
        else if (submit_action === "Generate PO Document"){
            title = "Generating PO Document...";
        }
        else if (submit_action === "Generate Asset"){
            title = "Generating Asset Numbers...";
        }
        else {
            title = "Saving Action Taken...";
        }

        // error with swal, happens before ajax so it causes form submission error
        swal.fire({
            title: title,
            text: "Please do not close the window or re-load the page",
            //icon: "warning",
            showCancelButton: false, // There won't be any cancel button
            showConfirmButton: false, // There won't be any confirm button
            closeOnBgClick: false,
            closeOnEscape: false,
        });

        // Adding files to request.FILES:
        var form = document.getElementById('msform');
        var formData = new FormData(form);

        var fileInput = document.getElementById("fileselect");
        var file = fileInput.files;
        if (fileInput.files !== undefined) {
            console.log('files: ' + file.toString());
            formData.append("fileselect", file);
        }


        // fileInput = document.getElementById("filedrag");
        // if (fileInput.files !== undefined){
        //     file = fileInput.files;
        //     console.log('files: ' + file.toString());
        //     formData.append("filedrag", file);
        // }


        var item_price_pks = [];
        var asset_nos = document.getElementsByName("asset_number");
        for (let i = 0; i < asset_nos.length; i++) {
            var item_price_pk = asset_nos[i].id.split("_")[asset_nos[i].id.split("_").length - 1];
            if (item_price_pk[0] === "0"){
                item_price_pks.push(item_price_pk.replace("0", ""));
            }
        }
        formData.append("item_price_pks", item_price_pks);


        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            success: function (data) {
                console.log(data);
                console.log("It worked!");
                // console.log("Form pk before: " + document.getElementById('form_pk').value);
                document.getElementById('form_pk').value = data['new_pk'];
                // console.log("Form pk after: " + document.getElementById('form_pk').value);
                try{
                    document.getElementById("reload_message").removeAttribute("hidden");
                }
                catch (e) {
                    console.log(e);
                }

                // If there are no errors do this:
                    if (data['result']['fatal_errors'] === ''){
                        // if there are no errors and the user clicked save, notify the user that the form was saved correctly. Do not redirect.
                        // if(submit_action === "Save") {
                        //     swal.fire({
                        //         title: "Form was saved!",
                        //         text: "The form was saved correctly.",
                        //         icon: "success",
                        //         showCancelButton: true,
                        //         cancelButtonText: 'Continue Working',
                        //         confirmButtonText: 'Go to Dashboard'
                        //         }).then((result) => {
                        //             console.log("result: " + result.value.toString());
                        //           if (result.value) {
                        //             window.location.href = data["dir_to_dash"];
                        //           }
                        //         })
                        //     }
                        if(submit_action === "Generate PO Document"){
                            window.open(data["file_link"], '_blank');
                            swal.fire({
                                title: "PO doc generated!",
                                text: "PO document should have opened in a new tab. If not, please try again.",
                                icon: "success",
                                showCancelButton: true,
                                cancelButtonText: 'Continue Working',
                                confirmButtonText: 'Go to Dashboard'
                                }).then((result) => {
                                    console.log("result: " + result.value.toString());
                                  if (result.value) {
                                    window.location.href = data["dir_to_dash"];
                                  }
                                });
                        }
                        else if(submit_action === "Upload Chosen File") {
                            // 1: add uploaded file to the list of uploaded files:
                            document.getElementById('uploaded_files_list').innerHTML = document.getElementById('uploaded_files_list').innerHTML +
                                "<br><a href=\""+ data["link_to_file"] +"\" target=\"_blank\">" + data["file_name"] + "</a>";
                            // 2: Clear the file field:
                            document.getElementById('uploaded_file').value = "";
                            document.getElementById('uploaded_file_name').innerHTML = "";
                            // 3: Make the button hidden again:
                            document.getElementById('upload_files_button').setAttribute("hidden", true);
                            swal.fire({
                                title: "File Uploaded!",
                                text: "The file was successfully uploaded.",
                                icon: "success",
                                buttons: {
                                    catch: {
                                        text: "Go to Dashboard",
                                        value: "catch",
                                    },
                                    cancel: "Continue Working"
                                }
                            })
                            .then((value) => {
                              switch (value) {
                                case "catch":
                                  window.location.href = data["dir_to_dash"];
                                  break;
                              }
                            });
                        }
                        else if (submit_action.includes("Save Unit Price")){
                            swal.fire({
                                title: "Changes were saved!",
                                text: "The form was saved correctly.",
                                icon: "success",
                                buttons: {
                                    catch: {
                                        text: "Go to Dashboard",
                                        value: "catch",
                                    },
                                    cancel: "Continue Working"
                                }
                            })
                            .then((value) => {
                              switch (value) {
                                case "catch":
                                  window.location.href = data["dir_to_dash"];
                                  break;
                              }
                            });
                        }
                        else if (submit_action.includes("Accounting Save")){
                            swal.fire({
                                title: "Changes were saved!",
                                text: "The form was saved correctly.",
                                icon: "success",
                                buttons: {
                                    catch: {
                                        text: "Go to Dashboard",
                                        value: "catch",
                                    },
                                    cancel: "Continue Working"
                                }
                            })
                            .then((value) => {
                              switch (value) {
                                case "catch":
                                  window.location.href = data["dir_to_dash"];
                                  break;
                              }
                            });
                        }
                         else if (submit_action.includes("Approve Item")){
                             // Hide Approve Item Button
                            document.getElementById(submit_action).setAttribute("hidden", true);
                            // Hide Decline Item
                            var approved_item_pk = submit_action.split(" ")[submit_action.split(" ").length - 1];
                            console.log("splitted: " + submit_action.split(" ").toString());
                            console.log("item pk: " + approved_item_pk.toString());
                            var decline_button_id = "Decline Item " + approved_item_pk.toString();
                            console.log("decline button id: " + decline_button_id);
                            document.getElementById(decline_button_id).setAttribute("hidden", true);

                            // If user is accountant:
                            if (data['updated_row_pk'] !== '' ){
                                //      Hide create asset button
                                document.getElementById('approver_check_' + data['updated_row_pk']).hidden = true;

                                //      Make Asset number readonly
                                document.getElementById('asset_number_' + data['updated_row_pk']).setAttribute("readonly", "true");

                                //      Turn GL Account into a readonly input field
                                document.getElementById('gl_account_' + data['updated_row_pk']).setAttribute("hidden", "true");
                                var select_value = $('#gl_account_' + data['updated_row_pk']).find(":selected").text();
                                var select_id = document.getElementById('gl_account_' + data['updated_row_pk']).id;
                                $("<input value='" + select_value + "' class='form-control' readonly>").insertAfter('#'+select_id.toString());

                                //      If there are any assets, make the last fields readonly
                                var asset_names = ["asset_class", "tech_category1", "tech_category2", "tech_category3", "tech_category4"];
                                for (let i = 0; i < asset_names.length; i++) {
                                    $('[id^="' + asset_names[i] + '_' + data['updated_row_pk'] +'"]').prop("readonly", true);
                                }

                            }

                            swal.fire({
                                title: "Item Approved!",
                                text: "You have successfully approved the item.",
                                icon: "success",
                                buttons: {
                                    catch: {
                                        text: "Go to Dashboard",
                                        value: "catch",
                                    },
                                    cancel: "Continue Working"
                                }
                            })
                            .then((value) => {
                              switch (value) {
                                case "catch":
                                  window.location.href = data["dir_to_dash"];
                                  break;
                              }
                            });
                        }
                         else if (submit_action.includes("Decline Item")){
                            // Get declined item pk
                            var declined_item_pk = submit_action.split(" ")[submit_action.split(" ").length - 1];

                            // hide the checkbox
                            document.getElementById("approver_check_0" + declined_item_pk).hidden = true;

                            // Replace Decline Item Button and Approve Item Button with Rescue Item Button (so that they can undo decline if they want)
                            document.getElementById("buttons_for_item_" + declined_item_pk).innerHTML = "<button type=\"submit\" class=\"btn btn-warning \" id=\"Undo Decline " + declined_item_pk + "\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Rescue Item (Undo Decline)\" onclick=\"return set_submit_button('Undo Decline " + declined_item_pk + "')\">\n" +
                                "                                                                  <i class=\"icon_lifesaver\"></i>\n" +
                                "                                                              </button>";

                            // Make row light coral
                            document.getElementById("purchase_item_row_" + declined_item_pk).style = "background-color: lightcoral";

                            // If the item has any assets make it light coral too
                            try{
                                var asset_rows = document.getElementsByName("item_asset_0" + declined_item_pk);
                            }
                            catch (e) {
                                console.log(e);
                                console.log("No assets associated with declined item");
                                var asset_rows = [];
                            }

                            for (let i = 0; i < asset_rows.length; i++) {
                                asset_rows[i].style = "background-color: lightcoral";
                            }

                            swal.fire({
                                title: "Item Declined!",
                                text: "You have successfully declined the item.",
                                icon: "success",
                                buttons: {
                                    catch: {
                                        text: "Go to Dashboard",
                                        value: "catch",
                                    },
                                    cancel: "Continue Working"
                                }
                            })
                            .then((value) => {
                              switch (value) {
                                case "catch":
                                  window.location.href = data["dir_to_dash"];
                                  break;
                              }
                            });
                        }
                         else if (submit_action.includes("Undo Decline")){
                            // Get declined item pk
                            var rescued_item_pk = submit_action.split(" ")[submit_action.split(" ").length - 1];

                            // if user is accountant, allow them to see the checkbox
                            if (data['user_department'] === 'Supporting - Accounting'){
                                document.getElementById("approver_check_0" + rescued_item_pk).removeAttribute("hidden");
                            }

                            // Replace Rescue Item Button with Decline Item Button and Approve Item Button
                            document.getElementById("buttons_for_item_" + rescued_item_pk).innerHTML = "<button type=\"submit\" class=\"btn btn-success\" id='Approve Item " + rescued_item_pk + "' data-toggle=\"tooltip\" data-placement=\"top\" title=\"Approve Item\" onclick=\"return set_submit_button('Approve Item " + rescued_item_pk + "')\">\n" +
                                "                                                                  <i class=\"icon_like_alt\"></i>\n" +
                                "                                                              </button>\n" +
                                "                                                              <button type=\"submit\" class=\"btn btn-danger \" id=\"Decline Item " + rescued_item_pk + "\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Decline Item\" onclick=\"return set_submit_button('Decline Item " + rescued_item_pk + "')\">\n" +
                                "                                                                  <i class=\"icon_dislike_alt\"></i>\n" +
                                "                                                              </button>";

                            // Make row normal color
                            document.getElementById("purchase_item_row_" + rescued_item_pk).removeAttribute("style");

                            // If the item has any assets make it normal color too
                            try{
                                var assets_to_normalify = document.getElementsByName("item_asset_0" + rescued_item_pk);
                            }
                            catch (e) {
                                console.log(e);
                                console.log("No assets associated with declined item");
                                var assets_to_normalify = [];
                            }

                            for (let i = 0; i < assets_to_normalify.length; i++) {
                                    assets_to_normalify[i].removeAttribute("style");
                                }



                            swal.fire({
                                title: "Item Rescued!",
                                text: "Item is no longer declined. You can now approve it.",
                                icon: "success",
                                buttons: {
                                    catch: {
                                        text: "Go to Dashboard",
                                        value: "catch",
                                    },
                                    cancel: "Continue Working"
                                }
                            })
                            .then((value) => {
                              switch (value) {
                                case "catch":
                                  window.location.href = data["dir_to_dash"];
                                  break;
                              }
                            });
                         }
                         else if (submit_action === "Accounting Approve"){
                             // Redirect
                            window.location.href = data["dir_to_dash"];
                        }
                        else if (submit_action === "Save and Submit form for approval"){
                            // Hide Save Unit Price buttons
                            // var save_buttons = document.getElementsByName('Save Unit Price');
                            // for (let i = 0; i < save_buttons.length; i++) {
                            //     save_buttons[i].setAttribute("hidden", true);
                            // }
                            // // Make unit price field readonly
                            // var unit_prices = document.getElementsByName("unit_price");
                            // for (let i = 0; i < unit_prices.length; i++) {
                            //     unit_prices[i].setAttribute("readonly", true);
                            // }
                            // Redirect
                            window.location.href = data["dir_to_dash"];
                        }
                        // if there are no errors and the user clicked Finish or Save and Submit form for approval, redirect them to the dashboard
                        else{
                            window.location.href = data["dir_to_dash"];
                        }
                    }

                    // If there are errors, notify the user
                    else{
                        swal.fire({
                        title: "Error updating the form!",
                        text: "What caused the error: \n" + data['result']['fatal_errors'],
                        icon: "warning",
                        buttons: {
                                    cancel: "Ok"
                                }
                         });
                    }


            },
            // If there was a ajax error do this
            error: function(data) {
                    console.log("Something went wrong!");
                    swal.fire({
                    title: "Something went wrong!",
                    text: "Form could not update! Please contact IT.",
                    icon: "warning",
                    buttons: {
                        cancel: "Ok"
                    }
                 });
                console.log(data);
            }
        });
        return false;
    });


// CSRF for Jquery Ajax form
$(function() {
    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    /*
    The functions below will create a header with csrftoken
    */
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url === origin || url.slice(0, origin.length + 1) === origin + '/') ||
            (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});
/************************************************************************************************************************************/
// END JQEURY AJAX SECTION
