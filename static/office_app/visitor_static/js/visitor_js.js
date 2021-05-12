
// Mainly to add new Row
var therowIndex =1;

$("#add_schedule").on('click', function () {
    var newRow = '<tr>' +
        '<td rowspan="2"><input id="schedule_date_' + therowIndex + '" name="schedule_date" type="date"  class="input-text js-input date"/></td>"' +
        '<td><input id="schedule_time_' + therowIndex + '" name="schedule_time"  type="time"  class="input-text js-input time"/></td>"' +
        '<td>' +
        '<div class="form-field">' +
        '<input id="schedule_meeting_' + therowIndex + '" class="input-text js-input" type="text" placeholder="Ex' + therowIndex + '"> <label class="label2" for="schedule_meeting_1">Meeting <input id="schedule_tour_' + therowIndex + '" type="number" class="labelinput"> (Mins)</label>'+
        '</div>' +
        '<div class="form-field">' +
        '<input id="explain_meeting_' + therowIndex + '" class="input-text js-input" type="text" placeholder="Ex' + therowIndex + '">' +
        '</div>' +
        '<div class="form-field">' +
        '<input id="explain_meeting_' + therowIndex + '" class="input-text js-input" type="text" placeholder="Ex' + therowIndex + '">' +
        '</div>' +
        '<div class="form-field">' +
        '<input id="presenter_meeting_' + therowIndex + '" class="input-text js-input" type="text" placeholder="Presenter' + therowIndex + '">' +
        '</div>' +
        '<div class="form-field">' +
        '<input id="resource_meeting_' + therowIndex + '" class="input-text js-input" type="text" placeholder="Resources ' + therowIndex + '">' +
        '</div>' +
        '</td>"' +
        '<td>' +
        '<div class="form-field">' +
        '<input id="schedule_location_' + therowIndex + '" class="input-text js-input time" type="text" placeholder="Room No' + therowIndex + '">' +
        '</div>' +
        '</td>"' +
        '<td>' +
        '<div class="form-field">\n' +
        '<textarea id="fii_participants_' + therowIndex + '" name="fii_participants" rows="12"  placeholder="List participants' + therowIndex + '"></textarea>\n' +
        '</div>' +
        '</td>"' +
        '<td><input onfocusout="calculate_item_amount(\'' + therowIndex + '\')"' +
        '                                                       onkeyup="calculate_item_amount(\'' + therowIndex + '\'); widthauto(this)"\n' +
        '                                                       id="quantity_' + therowIndex + '" maxlength="12" name="quantity"\n' +
        '                                                       placeholder="Qty '+ therowIndex+' " type="text"\n' +
        '                                                       class="form-control numberinput"></td>\n' +
        '<td><input onkeyup="widthauto(this)" maxlength="12" id="amount_' + therowIndex + '" name="amount" placeholder = "Amount ' + therowIndex + ' " type="text" readonly class="form-control numberinput"/></td>"' +
        '<td><select onkeyup="widthauto(this)"  id="unit_of_measurement_' + therowIndex + '" name="unit_of_measurement" type="text" class="form-control mb-3 take_arrow"/> <option></option></select></td>"' +
        // '<td class="print"><input onkeyup="widthauto(this)" maxlength="25" id="material_group_' + therowIndex + '" name="material_group" placeholder = "Material Group ' + therowIndex + ' " type="text"  class="form-control"/></td>"' +
        '<td hidden><select hidden onkeyup="widthauto(this)" onchange="update_gl_descriptions();" id="gl_account_' + therowIndex + '" name="gl_account"' + therowIndex + ' " type="text" class="custom-select custom-select-md"><option></option></select></td>"' +
        '<td hidden><input hidden onkeyup="widthauto(this)" id="gl_description_' + therowIndex + '" name="gl_description" placeholder = "GL Description ' + therowIndex + ' " type="text" readonly class="form-control"/>' +
        '<input hidden readonly name="template_item_id" value="' + therowIndex + '"></td>"' +
        '<td class="print"><button type="button" class="btn btn-danger btn-group hide_btn delete" id="printing"  data-toggle="tooltip" data-placement="top" title="Delete Row">\n' +
        '                                                    <i class="icon_trash"></i>\n' +
        '                                                </button></td>"' +
        '</tr>';

    if ($("#item_detail > tbody > tr").is("*"))
        $("#item_detail > tbody > tr:last").after(newRow)
    else $("#item_detail > tbody").append(newRow)


    populate_gl_accounts('gl_account_' + therowIndex);
    populate_departments('department_' + therowIndex);
    populate_uom('unit_of_measurement_' + therowIndex);
    // widthauto(document.getElementById('department_' + therowIndex));

    update_gl_descriptions();
    update_cost_center_code();
    limitInput();

    therowIndex++;

});