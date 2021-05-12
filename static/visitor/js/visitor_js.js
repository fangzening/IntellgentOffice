// To add Multiple Rows to Schedule Table
var therowIndex = 1;

$("#add_schedule").on('click', function () {
    var newRow =
        '<table class="table table-bordered" id="mainParent' + therowIndex + '">' +
        '<thead class="thead-dark">' +
        '<tr>' +
        '<th scope="col">Date</th>' +
        '<th scope="col">Time</th>' +
        '<th scope="col" style="width: 500px"> Agenda</th>' +
        '<th scope="col" style="width: 200px">Location</th>' +
        '<th scope="col">Fii Participants</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody>' +
        '<tr id="schedule_' + therowIndex + '">' +
        '<td rowspan="2"><input id="schedule_date_' + therowIndex + '" name="schedule_date" type="date"  class="input-text js-input date"/></td>' +
        '<td>' +
        '<div class="form-field">' +
        '<input id="schedule_time_from_' + therowIndex + '" name="meeting_time_from" class="input-text js-input time" type="time">' +
        '<label class="label2" for="schedule_meeting_1">Time (From) </label>' +
        '</div>' +
        '<div class="form-field">' +
        '<input id="schedule_time_to_' + therowIndex + '" name="meeting_time_to" class="input-text js-input time" type="time">' +
        '<label class="label2" for="schedule_meeting_1">Time (To) </label>' +
        '</div>' +
        '</td>' +
        '<td>' +
        '<div class="form-field">' +
        '<input id="schedule_meeting_' + therowIndex + '" name="meeting_explain_' + therowIndex + '" class="input-text js-input" type="text" placeholder="Explain' + therowIndex + '"> <label class="label2" for="schedule_meeting_1">Meeting <input id="schedule_tour_' + therowIndex + '" type="number" class="labelinput"> (Mins)</label>'+
        '</div>' +
        '<div class="form-field">' +
        '<input id="explain_meeting_' + therowIndex + '" name="meeting_explain_' + therowIndex + '" class="input-text js-input" type="text" placeholder="Explain' + therowIndex + '">' +
        '</div>' +
        '<div class="form-field">' +
        '<input id="explain_meeting_' + therowIndex + '" name="meeting_explain_' + therowIndex + '" class="input-text js-input" type="text" placeholder="Explain' + therowIndex + '">' +
        '</div>' +
        '<div class="form-field">' +
        '<input id="presenter_meeting_' + therowIndex + '" name="meeting_presenter" class="input-text js-input" type="text" placeholder="Presenter' + therowIndex + '">' +
        '</div>' +
        '<div class="form-field">' +
        '<input id="resource_meeting_' + therowIndex + '" name="meeting_resources" class="input-text js-input" type="text" placeholder="Resources ' + therowIndex + '">' +
        '</div>' +
        '</td>' +
        '<td>' +
        '<div class="form-field">' +
        '<input id="schedule_location_' + therowIndex + '" name="meeting_location" class="input-text js-input time" type="text" placeholder="Room No' + therowIndex + '">' +
        '</div>' +
        '</td>' +
        '<td>' +
        '<div class="form-field">' +
        '<textarea name="meeting_participants" rows="12"  placeholder="List participants ' + therowIndex + '"></textarea>' +
        '</div>' +
        '</td>' +
        '</tr>' +
        '<tr id="tour_' + therowIndex + '">' +
        '<td>' +
        '<div class="form-field  ">' +
        '<input id="tour_time_from_' + therowIndex + '" name="tour_time_from" class="input-text js-input time" type="time">' +
        '<label class="label2" for="schedule_meeting_1">Time (From) </label>' +
        '</div>' +
        '<div class="form-field  ">' +
        '<input id="tour_time_to_' + therowIndex + '" name="tour_time_to" class="input-text js-input time" type="time">' +
        ' <label class="label2" for="schedule_meeting_1">Time (To)</label>' +
        ' </div>' +
        '</td>' +
        '<td>' +
        '<div class="form-field">' +
        '                  <input id="schedule_tour_' + therowIndex + '" name="tour_explain_0' + therowIndex + '" class="input-text js-input" type="text" placeholder="Explain' + therowIndex + '">' +
        '                  <label class="label2" for="schedule_meeting_' + therowIndex + '">Tour <input id="schedule_tour_' + therowIndex + '" type="number" class="labelinput"> (Mins)</label>' +
        '                </div>' +
        '<div class="form-field">' +
        '                  <input id="explain_tour_' + therowIndex + '" name="tour_explain_0' + therowIndex + '" class="input-text js-input" type="text" placeholder="Explain ' + therowIndex + '">' +
        '                </div>' +
        '<div class="form-field">' +
        '                  <input id="explain_tour_' + therowIndex + '" name="tour_explain_0' + therowIndex + '" class="input-text js-input" type="text" placeholder="Explain ' + therowIndex + '">' +
        '                </div>' +
        '<div class="form-field">' +
        '                  <input id="presenter_tour_' + therowIndex + '" name="tour_presenter" class="input-text js-input" type="text" placeholder="Presenter ' + therowIndex + '">' +
        '                </div>' +
        '<div class="form-field">' +
        '                  <input id="resource_tour_' + therowIndex + '" name="tour_resources" class="input-text js-input" type="text" placeholder="Resources ' + therowIndex + '">' +
        '                </div>' +
        '</td>' +
        '<td>' +
        '<div class="form-field">' +
        '                  <input id="tour_location_' + therowIndex + '" name="tour_location" class="input-text js-input time" type="text" placeholder=" Eg. MPB">' +
        '                </div>' +
        '</td>' +
        '<td>' +
        '<div class="form-field">' +
        '                    <textarea name="fii_participants_tour' + therowIndex + '" rows="12"  name="tour_participants" placeholder="List participants ' + therowIndex + '"></textarea>' +
        '                    </div>' +
        '<button type="button" class="btn btn-outline-danger delete_schedule float-right" name="button"><svg width="1.5em" height="1.5em" viewBox="0 0 16 16" class="bi bi-person-x-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg">' +
        '<path fill-rule="evenodd" d="M1 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm6.146-2.854a.5.5 0 0 1 .708 0L14 6.293l1.146-1.147a.5.5 0 0 1 .708.708L14.707 7l1.147 1.146a.5.5 0 0 1-.708.708L14 7.707l-1.146 1.147a.5.5 0 0 1-.708-.708L13.293 7l-1.147-1.146a.5.5 0 0 1 0-.708z" />' +
        '</svg> </button>' +
        '</td>' +
        '</tr>' +
        '</tbody>' +
        '</table>';

    $("#visitor_schedule").append(newRow);


    therowIndex++;

});







// To add Multiple Rows to Visitor's Table
var theIndex = 4;

$("#add_visitor").on('click', function () {
    // var newVisitor = '<tr>' +
    //     '<th scope="row">' + theIndex + '</th>' +
    //     '<td><input id="visitor_name_' + theIndex + '" class="input-text js-input" type="text" placeholder="Visitor Name ' + theIndex + '"></td>"' +
    //     '<td><input id="job_title_' + theIndex + '" class="input-text js-input" type="text" placeholder="Job Title ' + theIndex + '"></td>"' +
    //     '<td><input id="sex_' + theIndex + '" class="input-text js-input" type="text" placeholder="M/F ' + theIndex + '"></td>"' +
    //     '<td><input id="job_role_' + theIndex + '" class="input-text js-input" type="text" placeholder="Job Role ' + theIndex + '"></td>"' +
    //     '<td><input id="visiting_history_' + theIndex + '" class="input-text js-input" type="text" placeholder="Y/N ' + theIndex + '"></td>"' +
    //     '<td><button type="button" class="btn btn-outline-danger delete_visitor" name="button"><svg width="1.5em" height="1.5em" viewBox="0 0 16 16" class="bi bi-person-x-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n' +
    //     '                    <path fill-rule="evenodd"\n' +
    //     '                      d="M1 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm6.146-2.854a.5.5 0 0 1 .708 0L14 6.293l1.146-1.147a.5.5 0 0 1 .708.708L14.707 7l1.147 1.146a.5.5 0 0 1-.708.708L14 7.707l-1.146 1.147a.5.5 0 0 1-.708-.708L13.293 7l-1.147-1.146a.5.5 0 0 1 0-.708z" />\n' +
    //     '                  </svg></button></td>' +
    //     '</tr>';
    var newVisitor = '<tr>' +
        '<th scope="row" style="visibility:hidden;">' + theIndex + '</th>' +
        '<td><input id="visitor_name" class="input-text js-input" type="text" placeholder="Visitor Name "></td>"' +
        '<td><input id="job_title" class="input-text js-input" type="text" placeholder="Job Title"></td>"' +
        '<td><input id="sex" class="input-text js-input" type="text" placeholder="M/F"></td>"' +
        '<td><input id="job_role" class="input-text js-input" type="text" placeholder="Job Role"></td>"' +
        '<td><input id="visiting_history" class="input-text js-input" type="text" placeholder="Y/N"></td>"' +
        '<td><button type="button" class="btn btn-outline-danger delete_visitor" name="button"><svg width="1.5em" height="1.5em" viewBox="0 0 16 16" class="bi bi-person-x-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n' +
        '                    <path fill-rule="evenodd"\n' +
        '                      d="M1 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm6.146-2.854a.5.5 0 0 1 .708 0L14 6.293l1.146-1.147a.5.5 0 0 1 .708.708L14.707 7l1.147 1.146a.5.5 0 0 1-.708.708L14 7.707l-1.146 1.147a.5.5 0 0 1-.708-.708L13.293 7l-1.147-1.146a.5.5 0 0 1 0-.708z" />\n' +
        '                  </svg></button></td>' +
        '</tr>';

    // if ($("#visitor > tbody > tr").is("*"))
    //     $("#visitor > tbody > tr:last").after(newVisitor)
    // else
    $("#visitor > tbody").append(newVisitor)


    theIndex++;

});



//Adding new Objectives

var objIndex = 4;
$("#add_obj").on('click', function () {
    var newObj =
        '<div class="form-field col-lg-12">' +
        '<input id="objectives_' + objIndex + '" class="input-text js-input" type="text" placeholder="' + objIndex + ' .">' +
        '</div>'
    $("#objectives").append(newObj)

    objIndex++;
});



$(document).on("click", ".delete_visitor", function () {

    const swalWithBootstrapButtons = Swal.mixin(
        {
            customClass: {
                confirmButton: 'btn btn-success',
                cancelButton: 'btn btn-danger'
            },
            width: 600,
            padding: '3em',
            buttonsStyling: true
        })

    swalWithBootstrapButtons.fire({
        title: 'Are you sure you want to delete this row??',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel!',
        reverseButtons: true,
        showClass: {
            popup: 'animate__animated animate__fadeInDown'
        },
        hideClass: {
            popup: 'animate__animated animate__fadeOutUp'
        }
    }).then((result) => {
        if (result.value) {
            if ($(this).parents('table').find('tr').length >= 3) {
                $(this).parents("tr").remove();
                swalWithBootstrapButtons.fire(
                    'Deleted!',
                    'Your item has been deleted.',
                    'success'
                )
            } else {
                swalWithBootstrapButtons.fire(
                    'Noooooo!',
                    'Please note you cannot delete all items!!!',
                    'error'
                )
            }


        } else if (

            result.dismiss === Swal.DismissReason.cancel
        ) {
            swalWithBootstrapButtons.fire(
                'Cancelled',
                'Your item was not deleted',
                'error'
            )
        }

    })
});



//Delete Schedule
$(document).on("click", ".delete_schedule", function () {

    const swalWithBootstrapButtons = Swal.mixin(
        {
            customClass: {
                confirmButton: 'btn btn-success',
                cancelButton: 'btn btn-danger'
            },
            width: 600,
            padding: '3em',
            buttonsStyling: true
        })

    swalWithBootstrapButtons.fire({
        title: 'Are you sure you want to delete this row??',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel!',
        reverseButtons: true,
        showClass: {
            popup: 'animate__animated animate__fadeInDown'
        },
        hideClass: {
            popup: 'animate__animated animate__fadeOutUp'
        }
    }).then((result) => {
        if (result.value) {
            // alert("Working")
            $(this)[0].parentNode.parentNode.parentNode.parentNode.remove()
            swalWithBootstrapButtons.fire(
                'Deleted!',
                'Your item has been deleted.',
                'success'
            )

        }


    })
});
var number = document.getElementById('numberof_people');

// Listen for input event on numInput.
number.onkeydown = function(e) {
    if(!((e.keyCode > 95 && e.keyCode < 106)
      || (e.keyCode > 47 && e.keyCode < 58)
      || e.keyCode === 8)) {
        return false;
    }
}



