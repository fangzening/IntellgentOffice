var frm = $('#request_password');
    frm.submit(function () {
        swal({
            title: "Sending Request..",
            text: "Please do not close the window or re-load the page",
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
                if (data['pass_fail_1'] === false && data['pass_fail_2'] === false && data['other_error'] === ""){
                    //console.log(data);
                    console.log("It worked!");
                    swal({
                            title: "Request was sent!",
                            text: "The form was saved correctly.",
                            icon: "success",
                             buttons: {
                                    catch: {
                                        text: "Ok",
                                        value: "catch",
                                    },
                                }
                        })
                }
                else{
                    var error_message = "";
                    if (data['pass_fail_1'] === true){
                        error_message += data['email_error'].toString() + '\n';
                    }
                    if (data['pass_fail_1'] === true){
                        error_message += data['password_error'].toString() + '\n';
                    }
                    if (data['other_error'] !== ""){
                        error_message += data['other_error'].toString() + '\n';
                    }
                    swal({
                    title: "Error sending request!",
                    text: error_message,
                    icon: "warning",
                    buttons: {
                                catch: {
                                    text: "Ok",
                                    value: "catch",
                                },
                            }
                     });
                }
            },
            error: function(data) {
                console.log("Something went wrong!");
                swal({
                title: "Form could not submit!",
                text: "What caused the form submission error: \n" + data['result'],
                icon: "warning",
                 buttons: {
                                catch: {
                                    text: "Ok",
                                    value: "catch",
                                },
                            }
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