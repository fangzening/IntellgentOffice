// This file has javascript by Corrina for the PR form


/************************************************************************************************************************************/
// START VALUE-CHANGING FUNCTIONS
/************************************************************************************************************************************/
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

// This function will initialize if the user is unable to edit the form (all stages are claimed, their stage declined the form, their stage approved the form
function user_cannot_edit_form(){
    // ids
    var elements_to_make_readonly = ['header_text', 'memo', 'attachment_description'];

    // names
    var multiple_elements_to_make_readonly = ['gr_quantity'];

    // ids
    var elements_to_hide = ['packaging_slip', 'attachments', 'addnew_attchment'];

    for (let i = 0; i < elements_to_make_readonly.length; i++) {
        //console.log("checking element: " + elements_to_hide[i].toString());
        if (document.getElementById(elements_to_make_readonly[i]).toString() !== 'chat-input') {
            try {
                document.getElementById(elements_to_make_readonly[i]).setAttribute("readonly", true);
            } catch (e) {
                console.log("element " + elements_to_make_readonly[i].toString() + " does not exist")
            }
        }

    }

    for (let i = 0; i < multiple_elements_to_make_readonly.length; i++) {
        var element_list = document.getElementsByName(multiple_elements_to_make_readonly[i]);
        for (let j = 0; j < element_list.length; j++) {
            //console.log("checking element: " + elements_to_hide[i].toString());
            if (element_list[i].id.toString() !== 'chat-input'){
                try{
                element_list[j].setAttribute("readonly", "true");
                }
                catch (e) {
                    console.log("element " + element_list[j].toString() + " does not exist")
                }
            }
        }
    }

    for (let i = 0; i < elements_to_hide.length; i++) {
        //console.log("checking element: " + elements_to_hide[i].toString());
        if (elements_to_hide[i].id.toString() !== 'chat-input') {
            try {
                document.getElementById(elements_to_hide[i]).setAttribute("hidden", "true");
            } catch (e) {
                console.log("element " + elements_to_hide[i].toString() + " does not exist")
            }
        }
    }
}


function user_can_edit_form(){
    // ids
    var elements_to_make_readonly = ['header_text', 'memo', 'attachment_description'];

    // names
    var multiple_elements_to_make_readonly = ['gr_quantity'];

    // ids
    var elements_to_hide = ['packaging_slip', 'attachments', 'addnew_attchment'];

    for (let i = 0; i < elements_to_make_readonly.length; i++) {
        try{
            document.getElementById(elements_to_make_readonly[i]).removeAttribute("readonly");
        }
        catch (e) {
            console.log("element " + elements_to_make_readonly[i].toString() + " does not exist")
        }
    }

    for (let i = 0; i < multiple_elements_to_make_readonly.length; i++) {
        try{
            var element_list = document.getElementsByName(multiple_elements_to_make_readonly[i]);
        }
        catch (e) {
            console.log("element " + element_list[i].toString() + " does not exist");
            continue;
        }

        for (let j = 0; j < element_list.length; j++) {
            try{
                element_list[j].removeAttribute("readonly");
            }
            catch (e) {
                console.log("element " + element_list[j] + " does not exist");
            }
        }
    }

    for (let i = 0; i < elements_to_hide.length; i++) {
        try{
            document.getElementById(elements_to_hide[i]).removeAttribute("hidden");
        }
        catch (e) {
            console.log("element " + elements_to_hide[i] + " does not exist");
        }

    }
}

function hide_selects(){
        // selects
    var select_boxes = document.getElementsByTagName("select");
    for (let i = 0; i < select_boxes.length; i++) {
        console.log("select box: " + select_boxes[i].id.toString());
        select_boxes[i].setAttribute("hidden", "true");
        // Insert after each select box an input field holding the data of the select box
        var select_id = select_boxes[i].id;
        var select_value = $('#' + select_id).find(":selected").text();
        $("<input value='" + select_value + "' class='form-control' readonly>").insertAfter('#'+select_id.toString());
    }
}

function update_cost_center_codes(){
    var cc_descs = document.getElementsByName('cc_description');
    var cc_codes = document.getElementsByName('cost_center');
    for (let i = 0; i < cc_descs.length; i++) {
        cc_codes[i].value = cc_descs[i].value;
    }
}

/************************************************************************************************************************************/
// END VALUE-CHANGING FUNCTIONS
/************************************************************************************************************************************/




//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




/************************************************************************************************************************************/
// START JQEURY AJAX SECTION
/************************************************************************************************************************************/
// corrina Validation function
function validate_gr(){
    var error_message = [];

    // for fields that have only once version of themselves
    var necesary_ids = ['memo',
                        //'sap_gr_postdate', 'sap_acc_doc',
                        ];

    // For fields that have multiple versions of themselves
    var necesary_names = [//'attachment_description',
    //                        'po_item', 'po_number', 'part_number', 'description', 'gr_quantity', 'po_quantity',
    //                        'cost_center', 'cc_description'
                        ];

    // Not sure on rules about packaging slip and MRO GR Attachment


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
    return error_message
}

// What happens when form submits:
var frm = $('#msform');
    frm.submit(function () {

        var submit_action = document.getElementById('submit_button').value;
        var title = "";

        if (submit_action.includes('Finish')){
            title = "Saving Action Taken...";

            // var error_msg = validate_gr();
            //
            // if (error_msg.length > 0)
            // {
            //     var error_message = "";
            //     for (let i = 0; i < error_msg.length; i++) {
            //         error_message += "\n" + error_msg[i];
            //     }
            //     swal.fire({
            //         title: "Please fix these issues before submitting",
            //         icon: "warning",
            //         text: error_message,
            //         buttons: {
            //                     cancel: "Ok"
            //                 }
            //     });
            //         return false;
            // }
        }
        else if (submit_action.includes("Save") || submit_action.includes("Save Unit Price")) {
            title = "Form is Saving...";
        }
        else if (submit_action === "Upload Chosen File") {
            title = "Uploading File...";
        }

        else{
            title = "Saving Action Taken..."
        }


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
        var file_field_names = ["company_amount_due_file", "business_file", "personal_file", "supporting_document"];
        for (let i = 0; i < file_field_names.length; i++) {
            //var data = [];
            for (let j = 0; j < document.getElementsByName(file_field_names[i]).length; j++) {
                var fileInput = document.getElementsByName(file_field_names[i])[j];
                var file = fileInput.files;

                formData.append(file_field_names[i], file);
            }
        }

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
            html:true,
            success: function (data) {
                console.log(data);
                console.log("It worked!");

                // If there are no errors do this:
                if (data['result']['fatal_errors'] === ''){
                    // if there are no errors and the user clicked save, notify the user that the form was saved correctly. Do not redirect.
                    if(submit_action.includes("Save")) {
                        document.getElementById('attachments').innerHTML = "<div class=\"form-group col-md-5\">\n" +
                            "                                        <input type=\"file\" class=\"form-control\" id=\"attachment\"\n" +
                            "                                               name=\"attachment\">\n" +
                            "                                    </div>\n" +
                            "                                    <div class=\"form-group col-md-6\">\n" +
                            "                                                        <textarea class=\"form-control\" id=\"attachment_description\"\n" +
                            "                                                                  name=\"attachment_description\"\n" +
                            "                                                                  placeholder=\"File Description\"></textarea>\n" +
                            "                                    </div>";

                        // Show packaging slip:
                        // check if data contains ['slip']
                        if ('slip' in data){
                            document.getElementById('slip').innerHTML = '<a href="' + data['slip']['link_to_file'] + '" target="_blank">"' + data['slip']['file_name'] + '</a>';
                        }

                        // Show attachments:
                        // check if data contains ['attachment#']
                        var keys = Object.keys(data);
                        console.log("keys: " + keys.toString());
                        for (let i = 0; i < keys.length; i++) {
                            var lineBreak = document.createElement("br");
                            var anchor = document.createElement("a");
                            anchor.href = data[keys[i]]['link_to_file'];
                            // anchor.name = data[keys[i]]['file_name']
                            anchor.innerHTML= data[keys[i]]['file_name'];
                            anchor.target="_blank";

                            try{
                                if (keys[i].includes('attachment')){
                                    document.getElementById('uploaded_attachments').appendChild(lineBreak);
                                     document.getElementById('uploaded_attachments').appendChild(anchor);
                                    // document.getElementById('uploaded_attachments').append('<br><a href="' + data[keys[i]]['link_to_file'] + '" target="_blank">' + data[keys[i]]['file_name'] + '</a>');
                                    document.getElementById('uploaded_attachments').removeAttribute('hidden');
                                }
                            }
                            catch (e) {
                                console.log(e);
                            }
                        }


                        // Get which one was clicked:
                        if (submit_action.includes("warehouse")){
                            // Update approver name field:
                            document.getElementById("warehouse_manager").value = document.getElementById("employee_name").value;
                            document.getElementById("warehouse_buttons").innerHtml = "<button type=\"submit\" class=\"btn btn-primary\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Save Changes\" onclick=\"return set_submit_button('Save warehouse')\">Save Changes</button>\n" +
                                "                                      <button type=\"submit\" class=\"btn btn-success\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Approve\" onclick=\"return set_submit_button('Finish warehouse')\">Approve</button>\n" +
                                "                                       <button type=\"submit\" class=\"btn btn-danger\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Decline\" onclick=\"return set_submit_button('Decline warehouse')\">Decline</button>";
                             // Hide buttons approver can no longer click and make other's comment field readonly:
                            document.getElementById('buyer_buttons').innerHTML = "";
                            document.getElementById('comment_buyer').setAttribute("readonly", true);
                        }
                        else{
                            // Update approver name field:
                            document.getElementById("buyer").value = document.getElementById("employee_name").value;
                            document.getElementById('buyer_buttons').innerHTML = "<button type=\"submit\" class=\"btn btn-primary\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Save Changes\" onclick=\"return set_submit_button('Save buyer')\">Save Changes</button>\n" +
                                "                                                    <button type=\"submit\" class=\"btn btn-success\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Approve\" onclick=\"return set_submit_button('Finish buyer')\">Approve</button>\n" +
                                "                                                    <button type=\"submit\" class=\"btn btn-danger\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Decline\" onclick=\"return set_submit_button('Decline buyer')\">Decline</button>";
                            // Hide buttons approver can no longer click and make other's comment field readonly:
                            document.getElementById('warehouse_buttons').innerHTML = "";
                            document.getElementById('comment_warehouse_manager').setAttribute("readonly", true);
                        }

                        // Update form Declined Messages
                        document.getElementById('declined_message').setAttribute("hidden", true);
                        document.getElementById('status').setAttribute("value", "Pending Approval");
                        document.getElementById('status').setAttribute("style", "");

                        swal.fire({
                            title: "Form was saved!",
                            text: "The form was saved correctly.",
                            icon: "success",
                            showCancelButton: true,
                            cancelButtonText: 'Continue Working',
                            confirmButtonText: 'Go to Dashboard'
                            }).then((result) => {
                              if (result.value) {
                                  window.location.href = data["dir_to_dash"];
                              }
                            })
                    }
                    else if(submit_action.includes("Un-")) {
                        user_can_edit_form();

                        // Hide declined or approved messages
                        document.getElementById('declined_message').setAttribute("hidden", true);
                        document.getElementById('approved_message').setAttribute("hidden", true);

                        // Show buttons that they can use now
                        if (submit_action.includes("warehouse")){
                            document.getElementById("warehouse_buttons").innerHTML = "<button type=\"submit\" class=\"btn btn-primary\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Save Changes\" onclick=\"return set_submit_button('Save warehouse')\">Save Changes</button>\n" +
                                "                                                    <button type=\"submit\" class=\"btn btn-success\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Approve\" onclick=\"return set_submit_button('Finish warehouse')\">Approve</button>\n" +
                                "                                                    <button type=\"submit\" class=\"btn btn-danger\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Decline\" onclick=\"return set_submit_button('Decline warehouse')\">Decline</button>";
                        }
                        else{
                            document.getElementById("buyer_buttons").innerHTML = "<button type=\"submit\" class=\"btn btn-primary\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Save Changes\" onclick=\"return set_submit_button('Save buyer')\">Save Changes</button>\n" +
                                "                                                    <button type=\"submit\" class=\"btn btn-success\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Approve\" onclick=\"return set_submit_button('Finish buyer')\">Approve</button>\n" +
                                "                                                    <button type=\"submit\" class=\"btn btn-danger\" data-toggle=\"tooltip\" data-placement=\"top\" title=\"Decline\" onclick=\"return set_submit_button('Decline buyer')\">Decline</button>";
                        }

                        swal.fire({
                            title: "Successful Action Undone!",
                            text: "You have successfully undone your action to the form.",
                            icon: "success",
                            showCancelButton: true,
                            cancelButtonText: 'Continue Working',
                            confirmButtonText: 'Go to Dashboard'
                            }).then((result) => {
                              if (result.value) {
                                window.location.href = data["dir_to_dash"];
                              }
                            })
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
                    // if there are no errors and the user clicked Finish, redirect them to the dashboard
                    else{
                        window.location.href = data["dir_to_dash"];
                    }
                }

                // If there are errors, notify the user
                else{
                    swal.fire({
                    title: "Error updating the form!",
                    text: "What caused the error: \n" + data['result'],
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
