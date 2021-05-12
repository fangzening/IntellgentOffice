var frm = $('#travel_form');
    frm.submit(function () {
        var submit_action = document.getElementById('submit_button').value;
        var title = "";

        if (submit_action === 'Send'){
            title = "Form is Submitting...";
        }
        else if (submit_action === "Save and Return to Home") {
            title = "Form is Saving...";
        }
        else{
            title = "Saving Action Taken..."
        }

        swal.fire({
            title: title,
            text: "Please do not close the window or re-load the page",
            icon: "success",
            showCancelButton: false,
            showConfirmButton: false,
            closeOnConfirm: false,
            closeOnBgClick: false,
            closeOnEscape: false,
             });

        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
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
                swal({
                title: "Form could not submit!",
                text: "What caused the form submission error: \n" + data['result']['fatal_errors'],
                type: "warning",
                showCancelButton: false,
                showConfirmButton: true,
                closeOnConfirm: true,
                 });
                //console.log(data);
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
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
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