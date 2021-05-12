var frm = $('#re_form');
    frm.submit(function () {
        var submit_action = document.getElementById('submit_button').value;
        var title = "";

        if (submit_action === 'Submit'){
            title = "Form is Submitting...";
        }
        else if (submit_action === "Save and Return to Home") {
            title = "Form is Saving...";
        }
        else{
            title = "Saving Action Taken..."
        }

        swal({
            title: title,
            text: "Please do not close the window or re-load the page",
            icon: "success",
            showCancelButton: false,
            showConfirmButton: false,
            closeOnConfirm: false,
            closeOnBgClick: false,
            closeOnEscape: false,
             });

        if (submit_action === "Send Modified"){
            create_fields_associated_with_ids();
        }

        // Adding files to request.FILES:
        var form = document.getElementById('re_form');
        var formData = new FormData(form);
        var file_field_names = ["uploaded_file"];
        for (let i = 0; i < file_field_names.length; i++) {
            for (let j = 0; j < document.getElementsByName(file_field_names[i]).length; j++) {
                var fileInput = document.getElementsByName(file_field_names[i])[j];
                var file = fileInput.files;

                formData.append(file_field_names[i], file);
            }
        }
        // When I send data like this and with frm.serialize, it gets parking data. otherwise, it doesn't
        // var xhr = new XMLHttpRequest();
        // xhr.open('POST', '', true);
        // xhr.send(formData);


        // After adding files it doesn't redirect like it was supposed too..
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            //data: frm.serialize(),
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            success: function (data) {
                if (data['result']['fatal_errors'] === ''){
                    //console.log(data);
                    console.log("It worked!");
                    window.location.href = data["dir_to_dash"];
                    //window.location.reload(); // To refresh page
                }
                else if(data['result'] === 'undefined'){
                    swal({
                    title: "Form could not submit!",
                    text: "There was an unknown error that stopped the form submission. Please contact IT for help.",
                    type: "warning",
                    showCancelButton: false,
                    showConfirmButton: true,
                    closeOnConfirm: true,
                     });
                }
                else{
                    swal({
                    title: "Form could not submit!",
                    text: "What caused the form submission error: \n" + data['result']['fatal_errors'],
                    type: "warning",
                    showCancelButton: false,
                    showConfirmButton: true,
                    closeOnConfirm: true,
                     });
                }
            },
            error: function(data) {
                console.log("Something went wrong!");
                try{
                    swal({
                    title: "Form could not submit!",
                    text: "What caused the form submission error: \n" + data['result']['fatal_errors'],
                    type: "warning",
                    showCancelButton: false,
                    showConfirmButton: true,
                    closeOnConfirm: true,
                     });
                }
                catch (e) {
                    swal({
                    title: "Form could not submit!",
                    text: "An unknown error occurred. Please contact IT.",
                    type: "warning",
                    showCancelButton: false,
                    showConfirmButton: true,
                    closeOnConfirm: true,
                     });
                }

                console.log(data);
            }
        });
        return false;
    });


    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CSRF for Jquery Ajax form
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
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