// This file has javascript by Corrina for the PR form


/************************************************************************************************************************************/
// START VALUE-CHANGING FUNCTIONS
/************************************************************************************************************************************/
var deleted_rows = [];

function calculate_balance(){
    //Tax amount + GR amount + Ship amount
    try{
        var tax_amount = parseFloat(document.getElementById('tax_amount').value);
    }
    catch (e) {
        var tax_amount = 0;
    }
    try{
         var gr_amount = parseFloat(document.getElementById('total_gr_amount').value);
    }
    catch (e) {
         var gr_amount = 0;
    }
   try{
        var ship_amount = parseFloat(document.getElementById('shipping_fee').value);
   }
    catch (e) {
        var ship_amount = 0;
    }
    document.getElementById('balance').value = (tax_amount+gr_amount + ship_amount).toString();
}


function calculate_tax_rate(){
    //Tax amount/(GR amount + Ship amount)
    try{
        var tax_amount = parseFloat(document.getElementById('tax_amount').value);
    }
    catch (e) {
        var tax_amount = 0;
    }
    try{
         var gr_amount = parseFloat(document.getElementById('total_gr_amount').value);
    }
    catch (e) {
         var gr_amount = 0;
    }
   try{
        var ship_amount = parseFloat(document.getElementById('shipping_fee').value);
   }
    catch (e) {
        var ship_amount = 0;
    }
    try{
        document.getElementById('tax_rate').value = (tax_amount/(gr_amount + ship_amount)).toString();
    }
    catch (e) {
        document.getElementById('tax_rate').value = '0.00';
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

// This function deletes a gr list item
function delete_gr_item(pk) {
    // have some way to make sure they don't delete ALL of the items.
    var amount_of_deleted_rows = deleted_rows.length;
    var amount_of_rows = document.getElementsByName('item_row').length;
    if (amount_of_deleted_rows < amount_of_rows - 1){
        document.getElementById('item_' + pk).innerHTML = "<td colspan='11' style='color: red'><b>Save changes to confirm deletion of this row</b><input hidden name='deleted_row' value='"+ pk +"'></td>";
        deleted_rows.push(pk.toString())
    }
    else{
        swal.fire({
                    title: "Cannot remove all rows",
                    icon: "warning",
                    text: "You must have at least one item on the invoice form",
                    buttons: {
                                cancel: "Ok"
                            }
                });
    }
}


// This function will initialize if the user is unable to edit the form (all stages are claimed, their stage declined the form, their stage approved the form
function user_cannot_edit_form(){
    // ids
    var elements_to_make_readonly = ['memo', 'invoice_date', 'invoice_date', 'invoice_text', 'tax_amount',
                                        'shipping_fee', 'tax_rate', 'invoice_amount'];

    // names
    var multiple_elements_to_make_readonly = [];

    // ids
    var elements_to_hide = ['yes', 'no'];

    for (let i = 0; i < elements_to_make_readonly.length; i++) {
        //console.log("checking element: " + elements_to_hide[i].toString());
        try{
            document.getElementById(elements_to_make_readonly[i]).setAttribute("readonly", true);
        }
        catch (e) {
            console.log("element " + elements_to_make_readonly[i].toString() + " does not exist")
        }

    }

    for (let i = 0; i < multiple_elements_to_make_readonly.length; i++) {
        var element_list = document.getElementsByName(multiple_elements_to_make_readonly[i]);
        for (let j = 0; j < element_list.length; j++) {
            try{
                element_list[j].setAttribute("readonly", "true");
            }
            catch (e) {
                console.log("element " + element_list[j].toString() + " does not exist")
            }
        }
    }

    document.getElementById('use_tax').removeAttribute('hidden');

    for (let i = 0; i < elements_to_hide.length; i++) {
        try{
            document.getElementById(elements_to_hide[i]).setAttribute("hidden", "true");
        }
        catch (e) {
            console.log("element " + elements_to_hide[i].toString() + " does not exist")
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

/************************************************************************************************************************************/
// END VALUE-CHANGING FUNCTIONS
/************************************************************************************************************************************/




//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




/************************************************************************************************************************************/
// START JQEURY AJAX SECTION
/************************************************************************************************************************************/
// corrina Validation function
function validate_invoice(){
    var error_message = [];

    // for fields that have only once version of themselves
    var necesary_ids = ['memo', 'invoice_date', 'tax_amount', 'invoice_amount',
        'shipping_fee', 'tax_rate', 'invoice_text', 'use_tax'];

    // For fields that have multiple versions of themselves
    var necesary_names = ['gl_account', 'quantity', 'amount'];

    for (let i = 0; i < necesary_ids.length; i++) {
        console.log('checkin for id: ' + necesary_ids[i]);
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

        if (submit_action.includes('Submit')){
            title = "Saving Action Taken...";

            var error_msg = validate_invoice();

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
        else if (submit_action.includes("Save")) {
            title = "Form is Saving...";
        }
        else if (submit_action.includes('upload')) {
            title = "Uploading File...";
        }
        else if (submit_action === 'generate_po_doc'){
            title = "Generating Document..."
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
        var file_field_ids = ['pr_file', 'po_file', 'gr_file', 'invoice_file', 'ar_file', 'ps_file'];

        for (let i = 0; i < file_field_ids.length; i++) {
            //var data = [];
            var fileInput = document.getElementById(file_field_ids[i]);
            if (fileInput !== null){
                var file = fileInput.files;
                formData.append(file_field_ids[i], file);
            }
        }

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
                    if(submit_action === "Save" || submit_action === "upload files" || submit_action==="generate_po_doc" ) {
                        // reset file upload fields where files were uploaded so files dont rist being uploaded twice
                        for (let i = 0; i < file_field_ids.length; i++) {
                            //var data = [];
                            var fileInputs = document.getElementsByName(file_field_ids[i]);
                            for (let j = 0; j < fileInputs.length; j++) {
                                if (fileInputs[j] !== null){
                                    fileInputs[j].value = null;
                                }
                            }
                        }


                        // Show packaging slip:
                        // check if data contains ['slip']
                        if ('slip' in data){
                            document.getElementById('slip').innerHTML = '<a href="' + data['slip']['link_to_file'] + '" target="_blank">"' + data['slip']['file_name'] + '</a>';
                        }

                        // Show attachments:
                        var keys = Object.keys(data['result']);
                        console.log("keys: " + keys.toString());
                        for (let i = 0; i < keys.length; i++) {
                            if (keys[i].includes('attachment')){
                                console.log('attachment object: ' + keys[i]);
                                var lineBreak = document.createElement("br");
                                var anchor = document.createElement("a");
                                anchor.href = data['result'][keys[i]]['link_to_file'];
                                anchor.innerHTML= data['result'][keys[i]]['file_name'];
                                anchor.target="_blank";
                                try{
                                    if (keys[i].includes('attachment')){
                                        document.getElementById(keys[i].replace('attachment', '')+'_list').appendChild(lineBreak);
                                        document.getElementById(keys[i].replace('attachment', '')+'_list').appendChild(anchor);
                                    }
                                }
                                catch (e) {
                                    console.log(e);
                                }
                            }
                        }
                        var text = "";
                        if (submit_action === 'Save'){
                            title = "Form was saved!";
                            text = 'The form was saved correctly and any files you added were uploaded.'
                        }
                        else if(submit_action === 'generate_po_doc'){
                            title = "Document Generated!";
                            text = 'Download link to the document should now appear on the page. If it does not, please contact IT.'
                        }
                        else{
                            title = "Files Uploaded!";
                            text = 'Files were successfully uploaded.'
                        }
                        // remove any rows that were deleted
                        console.log("deleted rows: " + deleted_rows.toString());
                        console.log("deleted rows length: " + deleted_rows.length.toString());
                        for (let i = 0; i < deleted_rows.length; i++) {
                            console.log("i: " + i.toString());
                            var row_to_delete = document.getElementById("item_" + deleted_rows[i]);
                            console.log('row to delete: ' + "item_" + deleted_rows[i]);
                            if (row_to_delete !== null){
                                console.log("removing row");
                                row_to_delete.remove();
                            }
                        }
                        deleted_rows = [];
                        swal.fire({
                            title: title,
                            text: text,
                            icon: "success",
                            showCancelButton: true,
                            cancelButtonText: 'Continue Working',
                            confirmButtonText: 'Go to Dashboard'
                            }).then((result) => {
                              if (result.value) {
                                  window.location.href = data["dir_to_dash"];
                              }
                            });

                        if(submit_action === 'generate_po_doc'){
                            document.getElementById('po_doc_link').innerHTML = "<a href=\"" + data['result']['pdf_link'] + "\" target=\"_blank\">Download PO printable Version</a>\n";
                            window.open(data['result']["pdf_link"], '_blank')
                        }

                    }
                    // if there are no errors and the user clicked Submit or Approve or Decline, redirect them to the dashboard
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
