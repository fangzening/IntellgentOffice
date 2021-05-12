<!-- Get and submit chat messages. - Written by Zaawar Ejaz -->

let lastMessageId = 0;
let newMessage = true;
let autoScroll = true;


$('#chat-input').mentionsInput({
    minChars: 0,
    onDataRequest: function (mode, query, callback) {
        $.getJSON(chat_approver_url, {'formType':form_type, 'formId':form_id},)
            .done(function (responseData) {
                responseData = _.filter(responseData['approvers'], function (item) {
                    return item.name.toLowerCase().indexOf(query.toLowerCase()) > -1
                });
                callback.call(this, responseData);
            })
            .fail(function( jqxhr, textStatus, error ) {
                var err = textStatus + ", " + error;
                console.log( "Request Failed: " + err );
            });
    }
});

$('#chat-input').on('keypress', function(event) {
    if(event.keyCode === 13) {
        event.preventDefault();
        send_chat_message();
    }
});

// $('#chat-input').emojioneArea({
//     filtersPosition: "bottom",
//     pickerPosition: "top",
//     search: false,
//     events: {
//         keypress: function (button, event) {
//             if(event.keyCode === 13) {
//                 event.preventDefault();
//                 send_chat_message();
//             }
//         },
//         emojibtn_click: function (button, event) {
//             $('#chat-input').data("emojioneArea").hidePicker()
//         }
//     }
// });


$('#chat-scroll').click(function (e) {
    $(this).toggleClass("btn fas fa-level-down-alt text-primary").toggleClass("btn fas fa-level-down-alt text-default");
    autoScroll = !autoScroll;
});

$('#toggle_icon').click(function () {
    if ($(this).hasClass("fa-arrow-up")) {
        $(this).removeClass("fa-arrow-up");
        $(this).addClass("fa-arrow-down");
    }
    else if ($(this).hasClass("fa-arrow-down")) {
        $(this).removeClass("fa-arrow-down");
        $(this).addClass("fa-arrow-up");
    }
});

$('#collapseOne').on('shown.bs.collapse', function () {
    $('#chat-body').scrollTop($('#chat-body')[0].scrollHeight);
    $('#chat-badge').html("");
});

$(function () {
    // initiate fetch messages function
    get_chat_messages();
});

// Get messages from server
const get_chat_messages = function (initialLoad = true) {

    // if(initialLoad) {
    //     $('#chat-input').prop('disabled', true);
    //     $('#chat-input').prop('placeholder', 'Please wait. Loading...');
    // }

    $.ajax({
        url: url + "?" + $.param({formId: form_id, formType: form_type, lastMessageId: lastMessageId }),
        type: "GET",
        success: function (result) {
            result['messages'].forEach(element => {
                if(element.sender_id === user_id) {
                    if(initialLoad) {
                        $('#chat_list').append(
                            '<li id="' + element.message_id + '" class="right clearfix">\n' +
                            '    <div class="chat-body clearfix">\n' +
                            '        <div>\n' +
                            '            <small class="text-muted time-text">\n' +
                            '                <span class="pr-1 far fa-clock text-success"></span>' + element.sent_on + '\n' +
                            '             </small>\n' +
                            '             <strong class="float-right font-weight-normal text-primary name-text">You</strong>\n' +
                            '        </div>\n' +
                            '        <p class="float-right">' + element.message + '</p>\n' +
                            '    </div>\n' +
                            '</li>'
                        )
                    }
                } else {
                    $('#chat_list').append(
                        '<li id="' + element.message_id +'" class="left clearfix">\n' +
                        '    <div class="chat-body clearfix">\n' +
                        '        <div>\n' +
                        '            <strong class="font-weight-normal text-primary name-text">' + element.sender_name + '</strong>\n' +
                        '            <small class="float-right text-muted time-text">\n' +
                        '                <span class="pr-1 far fa-clock text-success "></span>' + element.sent_on + '\n' +
                        '            </small>\n' +
                        '        </div>\n' +
                        '        <p>' + element.message + '</p>\n' +
                        '     </div>\n' +
                        '</li>'
                    );

                    newMessage = true;
                }
            });

            if (!initialLoad && newMessage && $('#collapseOne').is( ":hidden" ))
                $('#chat-badge').html('<span class="badge badge-chat">*</span>');

            if (autoScroll && newMessage)
                $('#chat-body').animate({ scrollTop : $('#chat-body')[0].scrollHeight}, "fast");

        },
        error: function (err) {
            console.log(err)
        },
        complete: function (data) {
            // if(initialLoad) {
            //     $('#chat-input').prop('disabled', false);
            //     $('#chat-input').prop('placeholder', 'Type your message here...');
            // }

            newMessage = false;

            let temp =  $('#chat_list li:last-child').prop('id');
            if (typeof temp !== 'undefined' && temp !== "") {
                lastMessageId = temp;
            }

            setTimeout(function () { get_chat_messages(false); }, 1000);
        }
    });
};

// {# Send message to server #}
const send_chat_message = function () {
    //.data("emojioneArea").getText().trim()
    if ($('#chat-input').val().trim() === "") {
        return;
    }

    let tempID = Math.round(Math.random()*1000000);
    let data = [];

    data['message'] = $('#chat-input').val();  //.data("emojioneArea").getText()

    $('#chat-input').mentionsInput('getMentions', function (mentions) {
        mentions.forEach(function (mention) {
            if (data['message'].search(mention.value) >= 0 ) {
                data['message'] = data['message'].replace(mention.value, "<b>" + mention.value + "</b>")
            }
        });

        data['mentions'] = mentions;

    });

    $.ajax({
        url: url,
        type: 'POST',
        data: {
            csrfmiddlewaretoken: csrf_token,
            formId: form_id,
            formType: form_type,
            message: data['message'],
            mentions: JSON.stringify(data['mentions'])
        },
        beforeSend: function () {
            $('#chat_list').append(
                '<li class="right clearfix">\n' +
                '    <div class="chat-body clearfix">\n' +
                '        <div>\n' +
                '            <small id="outgoing-' + tempID + '" class="text-muted time-text">\n' +
                '                <span class="pr-1 far fa-clock"></span>Sending\n' +
                '             </small>\n' +
                '             <strong class="float-right font-weight-normal text-primary name-text">You</strong>\n' +
                '        </div>\n' +
                '        <p class="float-right">' + data['message'] + '</p>\n' +
                '    </div>\n' +
                '</li>'
            );

            $('#chat-body').animate({ scrollTop : $('#chat-body')[0].scrollHeight}, "fast");
        },
        success: function (result) {
            $('#outgoing-'+tempID).html(
                '<span class="pr-1 far fa-clock text-success"></span>' + moment(new Date()).format("YYYY-MM-DD hh:mm A")
            );
        },
        error: function (err) {
            $('#outgoing-'+tempID).html(
                '<span class="pr-1 far fa-clock text-danger"></span>Sending failed'
            );
        }
    });

    // $('#chat-input').val(""); //.data("emojioneArea").setText("")
    $('#chat-input').mentionsInput('reset');
};
