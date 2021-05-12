;
(function ($) {
    "use strict";

    //* Form js
    function verificationForm() {
        //jQuery time
        var current_fs, next_fs, previous_fs; //fieldsets
        var left, opacity, scale; //fieldset properties which we will animate
        var animating; //flag to prevent quick multi-click glitches

        $(".next").click(function () {
            if (animating) return false;
            animating = true;

            current_fs = $(this).parent();
            next_fs = $(this).parent().next();

            //activate next step on progressbar using the index of next_fs
            $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

            //show the next fieldset
            next_fs.show();
            //hide the current fieldset with style
            current_fs.animate({
                opacity: 0
            }, {
                step: function (now, mx) {
                    //as the opacity of current_fs reduces to 0 - stored in "now"
                    //1. scale current_fs down to 80%
                    scale = 1 - (1 - now) * 0.2;
                    //2. bring next_fs from the right(50%)
                    left = (now * 50) + "%";
                    //3. increase opacity of next_fs to 1 as it moves in
                    opacity = 1 - now;
                    current_fs.css({
                        'transform': 'scale(' + scale + ')',
                        'position': 'inherit'
                    });
                    next_fs.css({
                        'left': left,
                        'opacity': opacity
                    });
                },
                duration: 800,
                complete: function () {
                    current_fs.hide();
                    animating = false;
                },
                //this comes from the custom easing plugin
                easing: 'easeInOutBack'
            });
        });

        $(".previous").click(function () {
            if (animating) return false;
            animating = true;

            current_fs = $(this).parent();
            previous_fs = $(this).parent().prev();

            //de-activate current step on progressbar
            $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

            //show the previous fieldset
            previous_fs.show();
            //hide the current fieldset with style
            current_fs.animate({
                opacity: 0
            }, {
                step: function (now, mx) {
                    //as the opacity of current_fs reduces to 0 - stored in "now"
                    //1. scale previous_fs from 80% to 100%
                    scale = 0.8 + (1 - now) * 0.2;
                    //2. take current_fs to the right(50%) - from 0%
                    left = ((1 - now) * 50) + "%";
                    //3. increase opacity of previous_fs to 1 as it moves in
                    opacity = 1 - now;
                    current_fs.css({
                        'left': left
                    });
                    previous_fs.css({
                        'transform': 'scale(' + scale + ')',
                        'opacity': opacity
                    });
                },
                duration: 800,
                complete: function () {
                    current_fs.hide();
                    animating = false;
                },
                //this comes from the custom easing plugin
                easing: 'easeInOutBack'
            });
        });

        $(".submit").click(function () {
            return false;
        })
    };

    //* Add Phone no select
    function phoneNoselect() {
        if ($('#msform').length) {
            $("#phone").intlTelInput();
            $("#phone").intlTelInput("setNumber", "+1");
        }
        ;
    };

    //* Select js
    function nice_Select() {
        if ($('.product_select').length) {
            $('select').niceSelect();
        }
        ;
    };
    /*Function Calls*/
    verificationForm();
    phoneNoselect();
    nice_Select();


    // var counter = 1;
    //
    // var limit = 100;
    //
    // function addInput(divName){
    //
    //      if (counter == limit)  {
    //
    //           alert("You have reached the limit of adding " + counter + " inputs");
    //
    //      }
    //
    //      else {
    //
    //           var newdiv = document.createElement('div');
    //
    //           newdiv.innerHTML = "Entry " + (counter + 1) + " <br><input type='text' name='myInputs[]'>";
    //
    //           document.getElementById(divName).appendChild(newdiv);
    //
    //           counter++;
    //
    //      }
    //
    // }

    $(document).ready(function () {
        $("#search_input").on("keyup", function () {
            var value = $(this).val().toLowerCase();
            $("#displaymodal td").filter(function () {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });

        });
    });
//   var $rows = $('#displaymodal tr');
// $('#search_input').keyup(function() {
//     var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
//
//     $rows.show().filter(function() {
//         var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
//         return !~text.indexOf(val);
//     }).hide();
// });

// $("#search_input").keyup(function () {
//     var value = this.value.toLowerCase().trim();
//     $("#displaymodal tr").each(function (index)
//     {
//         if (!index) return;
//         alert("Found")
//         $(this).find("td").each(function () {
//           if ("td")
//           {
//             if (value.toUpperCase().indexOf(filter) > -1)
//             {
//               ("tr")[i].style.display = "";
//             } else
//               {
//               ("tr")[i].style.display = "none";
//              }
//           }
//         });
//     });
// });

})(jQuery);


//
// function myFunction() {
//   var input, filter, table, tr, td, i, txtValue;
//   input = document.getElementById("search_input");
//   filter = input.value.toUpperCase();
//   table = document.getElementById("displaymodal");
//   tr = table.getElementsByTagName("tr");
//   for (i = 0; i < tr.length; i++) {
//     td = tr[i].getElementsByTagName("td")[4];
//     if (td) {
//       txtValue = td.textContent || td.innerText;
//       if (txtValue.toUpperCase().indexOf(filter) > -1) {
//         tr[i].style.display = "";
//       } else {
//         tr[i].style.display = "none";
//       }
//     }
//   }
// }


$('#item_detail').on('click', 'input[type="button"]', function () {
    $(this).closest('tr').remove();
})
$('p input[type="button"]').click(function () {
    $('#myTable').append('<tr><td><input type="text" class="fname" /></td><td><input type="button" value="Delete" /></td></tr>')
});


var selDiv = "";

document.addEventListener("DOMContentLoaded", init, false);

function init() {
    document.querySelector('#files').addEventListener('change', handleFileSelect, false);
    selDiv = document.querySelector("#selectedFiles");
}

function handleFileSelect(e) {

    if (!e.target.files || !window.FileReader) return;

    selDiv.innerHTML = "";

    var files = e.target.files;
    var filesArr = Array.prototype.slice.call(files);
    filesArr.forEach(function (f) {
        var f = files[i];
        if (!f.type.match("image.*")) {
            return;
        }

        var reader = new FileReader();
        reader.onload = function (e) {
            var html = "<img src=\"" + e.target.result + "\">" + f.name + "<br clear=\"left\"/>";
            selDiv.innerHTML += html;
        }
        reader.readAsDataURL(f);
    });

}



//Delete row on delete button click
$(document).on("click", ".delete", function () {

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
            if ($(this).parents('table').find('tr').length >= 4) {
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


// Mainly to add new Row
var therowIndex =1;

$("#addnew_item").on('click', function () {

    var checkbox = "";

    var newRow = '<tr>' + checkbox +
        //'<td hidden><input hidden onkeyup="widthauto(this)" id="asset_number_' + therowIndex + '"  name="asset_number" placeholder = "Asset Number ' + therowIndex + ' " type="text"  class="form-control numberinput"/></td>"' +
        '<td><input onkeyup="widthauto(this)" maxlength="25" id="supplier_pn_' + therowIndex + '" name="supplier_pn" placeholder = "Supplier ' + therowIndex + ' " type="text"  class="form-control"/></td>"' +
        // '<td><input onkeyup="widthauto(this)" id="arrival_date_' + therowIndex + '"\n' +
        // '                                                       name="arrival_date"\n' +
        // '                                                       type="date" class="form-control">\n' +
        // '                                            </td>' +
        '<td><input onkeyup="widthauto(this)" maxlength="25" id="item_description_' + therowIndex + '" name="item_description" placeholder = "Description ' + therowIndex + ' " type="text"  class="form-control"/></td>"' +
        '<td class="print"><select onkeyup="widthauto(this)" onchange="update_cost_center_code();" id="department_' + therowIndex + '" name="department" type="text" class="custom-select custom-select-md "><option></option></select></td>"' +
        '<td class="print"><input onkeyup="widthauto(this)" id="cost_center_' + therowIndex + '" name="cost_center" placeholder = "C.Center ' + therowIndex + ' " type="text" readonly class="form-control"/></td>"' +
        '<td><input onfocusout="calculate_item_amount(' + (therowIndex).toString() + ')" onkeyup="calculate_item_amount(' + (therowIndex).toString() + ');" maxlength="12" id="unit_price_' + therowIndex + '" name="unit_price" placeholder = " 0.00 " step="0.01" max="9999999999999.99" min="0.00" type="number"  class="form-control numberinput two-decimals"/></td>"' +
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

// var display_unit = []
//     $(document).ready(function dropdown_uom(){
//     display_unit = []
//     $.getJSON("{% url 'units_of_measure_api/'%}",function (data) {
//         var options = '<option disabled selected value>-- select a unit --</option>';
//              for (var i = 0; i < data.length; i++) {
//                         display_unit.push(data[i])
//                  options += '<option value "' + data[i].pk + '">' + data[i].fields['the_unit'] + '</option>';
//         }
//
//             $("select[name='unit_of_measurement']").html(options);
//              $("select[name='unit_of_measurement']").selectpicker('refresh');
// });
// });
//
// let dropdown = $('#unit_of_measurement_0');
//
// dropdown.empty();
//
// dropdown.append('<option selected="true" disabled>Choose Unit</option>');
// dropdown.prop('selectedIndex', 0);
//
// const url = "{% url 'units_of_measure_api' %}";
//
// // Populate dropdown with list of provinces
// $.getJSON(url, function (data) {
//   $.each(data, function (key, entry) {
//     dropdown.append($('<option></option>').attr('value', entry.the_unit).text(entry.the_desc));
//   })
// });

 // $(document).ready(function () {
 //        var url = "../units_of_measure_api/";
 //
 //                $.getJSON(url, function (data) {
 //                   alert("data",data)
 //                $.each(data, function (index, value) {
 //                    // APPEND OR INSERT DATA TO SELECT ELEMENT.
 //                    $('#unit_of_measurement_0').append('<option value="' + value.the_unit + '">' + value.the_desc + '</option>');
 //                });
 //            });
 //        });







function itemDetail() {
    var rows = document.getElementsByName("quantity");

    for (let i = 0; i < rows.length; i++) {

        var id_split = rows[i].id.toString().split("_");

        var id_number = id_split[id_split.length - 1];

        //console.log("id checking: " + id_number);
        //console.log("asset id checking: " + "asset_number_" + id_number);
        //var assetNumber = document.getElementById("asset_number_" + id_number).value;
        var assetSupplierPN = document.getElementById("supplier_pn_" + id_number).value;
        var assetItemDescription = document.getElementById("item_description_" + id_number).value;
        var assetDepartment = document.getElementById("department_" + id_number).value;
        var assetCostCenter = document.getElementById("cost_center_" + id_number).value;
        var assetUnitPrice = document.getElementById("unit_price_" + id_number).value;
        var assetQuantity = document.getElementById("quantity_" + id_number).value;
        var assetAmount = document.getElementById("amount_" + id_number).value;
        var assetMaterialGroup = document.getElementById("material_group_" + id_number).value;
        var e = document.getElementById("gl_account_" + id_number);
        var assetGLAccount = e.options[e.selectedIndex].text;
        var assetGLDescription = document.getElementById("gl_description_" + id_number).value;


        // Get these where ids start with name_id_number
        var asset_num = "asset_numberdisplay_" + id_number + "_";
        var supplier_pn = "supplier_pndisplay_" + id_number + "_";
        var item_desc = "item_descriptiondisplay_" + id_number + "_";
        var department_disp = "departmentdisplay_" + id_number + "_";
        var ccd = "cost_centerdisplay_" + id_number + "_";
        var upd = "unit_pricedisplay_" + id_number + "_";
        var qd = "quantitydisplay_" + id_number + "_";
        var ad = "amountdisplay_" + id_number + "_";
        var mgd = "material_groupdisplay_" + id_number + "_";
        var glad = "gl_accountdisplay_" + id_number + "_";
        var gldd = "gl_descriptiondisplay_" + id_number + "_";

        // document.getElementById(asset_num).value = assetNumber;
        // document.getElementById(supplier_pn).value = assetSupplierPN;
        // document.getElementById(item_desc).value = assetItemDescription;
        // document.getElementById(department_disp).value = assetDepartment;
        // document.getElementById(ccd).value = assetCostCenter;
        // document.getElementById(upd).value = assetUnitPrice;
        // document.getElementById(qd).value = assetQuantity;
        // document.getElementById(ad).value = assetAmount;
        // document.getElementById(mgd).value = assetMaterialGroup;
        // document.getElementById(department_disp).value = assetDepartment;
        // document.getElementById(glad).value = assetGLAccount;
        // document.getElementById(gldd).value = assetGLDescription;

        //console.log("editing assets that start with: " + asset_num);
        $("input[id^=" + item_desc + "]").val(assetItemDescription);
        // $("input[id^=" + supplier_pn + "]").val(assetSupplierPN);
        // $("input[id^=" + department_disp + "]").val(assetDepartment);
        // $("input[id^=" + ccd + "]").val(assetCostCenter);
        // $("input[id^=" + upd + "]").val(assetUnitPrice);
        // $("input[id^=" + qd + "]").val("1");
        // $("input[id^=" + ad + "]").val(assetAmount);
        // $("input[id^=" + mgd + "]").val(assetMaterialGroup);
        // $("input[id^=" + glad + "]").val(assetGLAccount);
        // $("input[id^=" + gldd + "]").val(assetGLDescription);
    }
}

$('.modal').click(function (event) {
    $(event.target).modal('hide');
});


function modalpop(checked, checked_id) {
    $('#approver_check_' + checked_id.toString()).prop("checked", false);
    if (checked) {
        bootbox.dialog({
            title: 'Choose an Action',
            message: "<p>Hi, Kindly Choose an Action.</p>",
            size: 'medium',
            centerVertical: true,
            // Make it so that if user presses 'x' the checkbox is unchecked
            // onEscape: {
            //   function () {
            //     $('#approver_check_' + checked_id.toString()).prop("checked", false);
            //   }
            // },

            buttons: {
                // cancel: {
                //   label: "Decline",
                //   className: 'btn-danger',
                //   callback: function () {
                //     console.log('Custom cancel clicked');
                //   }
                // },
                noclose: {
                    label: "Need more information ?",
                    className: 'btn-info',
                    callback: function () {
                        bootbox.prompt()({
                            title: "This is a prompt with a number input!",
                            inputType: 'number',
                            callback: function (result) {
                                console.log(result);
                            }

                        })


                        // function moreInfo (){
                        //           var togglethetexarea = document.getElementById("more_info");
                        //           togglethetexarea.toggle();
                        //   return false;
                    }
                },
                ok: {
                    label: "Create an Asset",
                    className: 'btn-primary',
                    backdrop: true,
                    callback: function createTable() {
                        $('#approver_check_' + checked_id.toString()).prop("checked", true);
                        var a;
                        //var master_quantities = document.getElementsByName("quantity");
                        var master_quantity = document.getElementById("quantity_" + checked_id);
                        var rows = "";
                        var table_has_been_created_already = true;
                        // If there are no rows, add header row to the table
                        try {
                            document.getElementById("displaymodalheader").id;
                        } catch (e) {
                            //console.log("table has not been created yet");
                            table_has_been_created_already = false;
                            //var gl_stuff = "";
                            rows = "<tr>\n" +
                                "                                                <input type=\"submit\" name=\"generate_asset_button\"\n" +
                                "                                                           class=\"btn btn-success ml-auto\" id=\"generate_asset_button\" value=\"Generate Asset Number\" onclick=\"return set_submit_button('Generate Asset');\"/>\n" +
                                "                                            </tr><br>" +
                                "<tr id=\"displaymodalheader\">" +
                                "<th>Asset Number</th>" +
                                "<th>Item Description</th>" +
                                "<th>Asset Class</th>" +
                                "<th>Tech Category 1</th>" +
                                "<th>Tech Category 2</th>" +
                                "<th>Tech Category 3</th>" +
                                "<th>Tech Category 4</th></tr>";
                        }

                        // Only add the assets that the user checked the checkbox of


                        //for (let j = 0; j < master_quantities.length; j++) {

                        var quantity_id_num = master_quantity.id.split("_")[master_quantity.id.split("_").length - 1];

                        //console.log("id checked: " + "approver_check_ " + quantity_id_num.toString());

                        // if (!document.getElementById("approver_check_" + quantity_id_num).checked)
                        //   continue;

                        a = master_quantity.value;
                        var the_id = master_quantity.id.toString();
                        //console.log("id: " + the_id);

                        var splitted = the_id.split("_");
                        //console.log("splitted: " + splitted.toString());

                        var id_number = splitted[splitted.length - 1];
                        //console.log("ID Num: " + id_number.toString());
                        var length = document.getElementById('itemDisplay').rows.length;
                        if (a === "") {
                            bootbox.alert("Please enter some numeric value");
                        } else {
                            for (var i = 0; i < a; i++) {
                                if (i===0){
                                    rows += "<tr name='item_asset_" + id_number + "'><td><input type='number' readonly class='form-control' name='asset_numberdisplay' placeholder='Asset Number'  id='" + "asset_numberdisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' readonly class='form-control' name='item_descriptiondisplay' placeholder='Description' id='" + "item_descriptiondisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' class='form-control' name='asset_class' placeholder='Asset Class' id='" + "asset_class_" + id_number + "_".concat(i + 1) + "' onkeyup='update_following_assets(\"asset_class_" + id_number + "\", \"asset_class\");'></td>" +
                                    "<td><input type='text' class='form-control' maxlength=\"50\" name='tech_category1' placeholder='Tech Category 1' id='" + "tech_category1_" + id_number + "_".concat(i + 1) + "' onkeyup='update_following_assets(\"tech_category1_" + id_number + "\", \"tech_category1\");'></td>" +
                                    "<td><input type='text' class='form-control' maxlength=\"50\" name='tech_category2' placeholder='Tech Category 2' id='" + "tech_category2_" + id_number + "_".concat(i + 1) + "' onkeyup='update_following_assets(\"tech_category2_" + id_number + "\", \"tech_category2\");'></td>" +
                                    "<td><input type='text' class='form-control' maxlength=\"50\" name='tech_category3' placeholder='Tech Category 3' id='" + "tech_category3_" + id_number + "_".concat(i + 1) + "' onkeyup='update_following_assets(\"tech_category3_" + id_number + "\", \"tech_category3\");'></td>" +
                                    "<td><input type='text' class='form-control' maxlength=\"50\" name='tech_category4' placeholder='Tech Category 4' id='" + "tech_category4_" + id_number + "_".concat(i + 1) + "' onkeyup='update_following_assets(\"tech_category4_" + id_number + "\", \"tech_category4\");'>" +
                                    "<input name='template_asset_id' value='" + id_number + "' readonly hidden></td></tr>";
                                }
                                else{
                                    rows += "<tr name='item_asset_" + id_number + "'><td><input type='number' readonly class='form-control' name='asset_numberdisplay' placeholder='Asset Number'  id='" + "asset_numberdisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' readonly class='form-control' name='item_descriptiondisplay' placeholder='Description' id='" + "item_descriptiondisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' class='form-control' name='asset_class' placeholder='Asset Class' id='" + "asset_class_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' class='form-control' maxlength=\"50\" name='tech_category1' placeholder='Tech Category 1' id='" + "tech_category1_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' class='form-control' maxlength=\"50\" name='tech_category2' placeholder='Tech Category 2' id='" + "tech_category2_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' class='form-control' maxlength=\"50\" name='tech_category3' placeholder='Tech Category 3' id='" + "tech_category3_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' class='form-control' maxlength=\"50\" name='tech_category4' placeholder='Tech Category 4' id='" + "tech_category4_" + id_number + "_".concat(i + 1) + "'>" +
                                    "<input name='template_asset_id' value='" + id_number + "' readonly hidden></td></tr>";
                                }
                            }
                        }

                        //

                        document.getElementById("displaymodalbody").insertAdjacentHTML("beforeend", rows);
                        itemDetail();

                        // make dept, cost center code, gl account, and gl description hidden for this particular item
                        var items_to_hide = ['gl_account', 'gl_description'];
                        for (let i = 0; i < items_to_hide.length; i++) {
                            console.log("looking for: " + items_to_hide[i] + "_" + id_number);
                            document.getElementById(items_to_hide[i] + "_" + id_number).setAttribute("hidden", "true");
                        }
                        // make asset number not hidden for this particular item
                         //document.getElementById('asset_number_' + id_number).removeAttribute("hidden");
                    }
                }

            }
        })
    } else {
        console.log("begin unchecked function");
        // If user unchecked the check box
        var a;
        var master_quantity = document.getElementById("quantity_" + checked_id);

        var quantity_id_num = master_quantity.id.split("_")[master_quantity.id.split("_").length - 1];

        a = master_quantity.value;
        var the_id = master_quantity.id.toString();

        var splitted = the_id.split("_");

        var id_number = splitted[splitted.length - 1];
        var length = document.getElementById('itemDisplay').rows.length;

        var assets_to_delete = document.getElementsByName("item_asset_" + id_number);

        for (let i = 0; i !== assets_to_delete.length; i) {                 // It goes down each time an asset is removed, so wait until length gets to 0
            assets_to_delete[i].parentNode.removeChild(assets_to_delete[i]);
        }
        // make dept, cost center code, gl account, and gl description not hidden for this particular item
        var items_to_show = ['input_department', 'cost_center', 'gl_account', 'gl_description'];
        for (let i = 0; i < items_to_show.length; i++) {
            document.getElementById(items_to_show[i] + "_" + id_number).removeAttribute("hidden");
        }
        // make asset number not hidden for this particular item
        //document.getElementById('asset_number_' + id_number).setAttribute("hidden", "true");
        console.log("end unByIdchecked function");
    }
}

//
//
function widthauto(textbox) {
    $(textbox).parent().css("width", ((textbox.value.length + 1) * 9)+ "px");
}

$(".two-decimals").change(function(){
  this.value = parseFloat(this.value).toFixed(2);
});


//
// document.getElementById("show_table").addEventListener("click", function (button) {
//     if (document.getElementById("item_detail").style.display === "none")
//         document.getElementById("item_detail").style.display = "block";
//     else document.getElementById("item_detail").style.display = "none";
// });
//
//
// document.getElementById("show_table").addEventListener("click", function (button) {
//     if (document.getElementById("addnew_item").style.display === "none")
//         document.getElementById("addnew_item").style.display = "block";
//     else document.getElementById("addnew_item").style.display = "none";
// });
//
// document.getElementById('show_table').addEventListener("click", function (mouseEvent) {
//     document.getElementById("show_table").style.display = "none";
// });


<!--Auto-Complete Function. Author:Josh-->
function autocomplete(inp, arr) {
    var currentFocus;
    inp.addEventListener("input", function (e) {
        var a, b, i, val = this.value;
        closeAllLists();
        if (!val) {
            return false;
        }
        currentFocus = -1;
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(a);
        for (i = 0; i < arr.length; i++) {
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                b = document.createElement("DIV");
                b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                b.innerHTML += arr[i].substr(val.length);
                b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                b.addEventListener("click", function (e) {
                    inp.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
        update_vendor();
    });

    inp.addEventListener("keydown", function (e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            currentFocus++;
            addActive(x);
        } else if (e.keyCode == 38) {
            currentFocus--;
            addActive(x);
        } else if (e.keyCode == 13) {
            e.preventDefault();
            if (currentFocus > -1) {
                if (x) x[currentFocus].click();
            }
        }
        update_vendor();
    });

    function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add("autocomplete-active");
        update_vendor();
    }

    function removeActive(x) {
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
        update_vendor();
    }

    function closeAllLists(elmnt) {
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
        update_vendor();
    }

    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
        update_vendor();
    });
}


//
// function displayFunction() {
//      $(".show_summary").click(function () {
//     Swal.fire({
//         title: 'Do you want to view your Form Summary?',
//         icon: 'info',
//         showCancelButton: true,
//         confirmButtonColor: '#3085d6',
//         cancelButtonColor: '#d33',
//         confirmButtonText: 'Yes, show  summary!'
//     }).then((result) => {
//         if (result.value) {
//             Swal.fire(
//                 'Generated!',
//                 'Your summary has been generated.',
//                 'success'
//             )
//
//                $("fieldset").css({"display": "block", "opacity" : "1", "transform": "none"});
//                $(".action-button, .btn, #progressbar").hide();
//                // $("#summary").addClass('newClassWithYourStyles').removeClass('show_summary').val('Go to Form');
//                 $("#summary").toggleClass("show_summary show_form");
//
//
//         }
//
//
//
//     })
//
// })
// }
//
//  displayFunction();
//
// $(document).ready(function(){
//           $('#myLink').click();
//     Swal.fire({
//         title: 'Do you want to view your Form Summary?',
//         icon: 'info',
//         showCancelButton: true,
//         confirmButtonColor: '#3085d6',
//         cancelButtonColor: '#d33',
//         confirmButtonText: 'Yes, show  summary!'
//     }).then((result) => {
//         if (result.value) {
//             Swal.fire(
//                 'Generated!',
//                 'Your summary has been generated.',
//                 'success'
//             )
//
//                $("fieldset").css({"display": "block", "opacity" : "1", "transform": "none", "button" : "none" });
//                $(".action-button, .btn, #progressbar").hide();
//                $("#summary").val('Go to Form').href("google.com").button('refresh');
//
//
//
//         }
//
//
//
//     })
//
//  });
// function change() {
//     $("#summary").val('Go to Form')
//
// }


function toggle() {
    let timerInterval
    Swal.fire({
        title: 'Sure! We are working on it!',
        html: 'Generating in <b></b> milliseconds.',
        timer: 1500,
        timerProgressBar: true,
        onBeforeOpen: () => {
            Swal.showLoading()
            timerInterval = setInterval(() => {
                const content = Swal.getContent()
                if (content) {
                    const b = content.querySelector('b')
                    if (b) {
                        b.textContent = Swal.getTimerLeft()
                    }
                }
            }, 100)
        },
        onClose: () => {
            clearInterval(timerInterval)
        }
    }).then((result) => {

        if (result.dismiss === Swal.DismissReason.timer) {
            console.log('Generated')


        }
    })


    var el1 = document.getElementById("main"),
        el2 = document.getElementById("summary_style");
    var sum_button = document.getElementById("summary")
    if (el1.disabled) {
        el1.disabled = false;
        el2.disabled = true;


    } else {
        el1.disabled = true;
        el2.disabled = false;

    }


}

$('#summary').click(function() {
    var change_text = $(this);
        change_text.html(change_text.text() === 'Page Summary' ? 'Go Back to Form' : 'Page Summary');
    return false;
});



    $("#summary").click(function(){
        


});



//
// $(document).ready(function() {
//    $('.selectpicker').selectpicker();
// });

 // $('.selectpicker').selectpicker({
 //      });

//* Form js
// function summarypage() {
//   //jQuery time
//   var current_fs, next_fs, previous_fs; //fieldsets
//   var left, opacity, scale; //fieldset properties which we will animate
//   var animating; //flag to prevent quick multi-click glitches
//
//   $("#summary").click(function () {
//     if (animating) return false;
//     animating = true;
//
//     current_fs = $(this).parent();
//     next_fs = $(this).parent().next();
//
//     //activate next step on progressbar using the index of next_fs
//     $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");
//
//     //show the next fieldset
//     next_fs.show();
//     //hide the current fieldset with style
//     current_fs.animate({
//       opacity: 1
//     }, {
//       step: function (now, mx) {
//         //as the opacity of current_fs reduces to 0 - stored in "now"
//         //1. scale current_fs down to 80%
//         scale = 1 - (1 - now) * 0.2;
//         //2. bring next_fs from the right(50%)
//         left = (now * 50) + "%";
//         //3. increase opacity of next_fs to 1 as it moves in
//         opacity = 1 - now;
//         current_fs.css({
//           'transform': 'scale(' + scale + ')',
//           'position': 'inherit'
//         });
//         next_fs.css({
//           'left': left,
//           'opacity': opacity
//         });
//       },
//       duration: 800,
//       complete: function () {
//         current_fs.hide();
//         animating = false;
//       },
//       //this comes from the custom easing plugin
//       easing: 'easeInOutBack'
//     });
//   });
//
//   $(".previous").click(function () {
//     if (animating) return false;
//     animating = true;
//
//     current_fs = $(this).parent();
//     previous_fs = $(this).parent().prev();
//
//     //de-activate current step on progressbar
//     $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");
//
//     //show the previous fieldset
//     previous_fs.show();
//     //hide the current fieldset with style
//     current_fs.animate({
//       opacity: 0
//     }, {
//       step: function (now, mx) {
//         //as the opacity of current_fs reduces to 0 - stored in "now"
//         //1. scale previous_fs from 80% to 100%
//         scale = 0.8 + (1 - now) * 0.2;
//         //2. take current_fs to the right(50%) - from 0%
//         left = ((1 - now) * 50) + "%";
//         //3. increase opacity of previous_fs to 1 as it moves in
//         opacity = 1 - now;
//         current_fs.css({
//           'left': left
//         });
//         previous_fs.css({
//           'transform': 'scale(' + scale + ')',
//           'opacity': opacity
//         });
//       },
//       duration: 800,
//       complete: function () {
//         current_fs.hide();
//         animating = false;
//       },
//       //this comes from the custom easing plugin
//       easing: 'easeInOutBack'
//     });
//   });
//
//   $("").click(function () {
//     return false;
//   })
// };

$(document).ready(function() {
	$('[data-toggle="toggle"]').change(function(){
		$(this).parents().next('.hide').toggle();
	});
});




// this is for the upload
(function() {

	// getElementById
	function $id(id) {
		return document.getElementById(id);
	}


	// output information
	function Output(msg) {
		var m = $id("messages");
		m.innerHTML = msg + m.innerHTML;
	}


	// file drag hover
	function FileDragHover(e) {
		e.stopPropagation();
		e.preventDefault();
		e.target.className = (e.type == "dragover" ? "hover" : "");
	}


	// file selection
	function FileSelectHandler(e) {

		// cancel event and hover styling
		FileDragHover(e);

		// fetch FileList object
		var files = e.target.files || e.dataTransfer.files;

		// process all File objects
		for (var i = 0, f; f = files[i]; i++) {
			ParseFile(f);
			console.log(f.name);
		}
		// console.log("the files dragged :" +file[i])


	}
	// this is just to test the AJAX function







    // End AJAX


	// output file information
	function ParseFile(file) {

		Output(
			"<p>Name of File: <strong>" + file.name +
			"</strong> File Type: <strong>" + file.type +
			"</strong> Size of File: <strong>" + file.size +
			"</strong> bytes</p>"

		);

	}


	// initialize
	function Init() {

		var fileselect = $id("fileselect"),
			filedrag = $id("filedrag"),
			submitbutton = $id("Save");
		    fileList =[];

		// file select
		fileselect.addEventListener("change", FileSelectHandler, false);


        filedrag.addEventListener('change', function (evnt){
            fileList = [];
            for(var i = 0; i < filedrag.files.length; i++){

                fileList.push(filedrag.files[i]);

            }
            console.log("dragged: "+ FileList)
        })
        // filedrag.addEventListener('change', function (evnt){
        //     fileList = [];
        //     for(var i = 0; i < filedrag.files.length; i++){
        //         fileList.push(filedrag.files[i]);
        //     }
        //     console.log("file drag: "+fileList)
        // })



		// is XHR2 available?
		var xhr = new XMLHttpRequest();
		if (xhr.upload) {

			// file drop
			filedrag.addEventListener("dragover", FileDragHover, false);
			filedrag.addEventListener("dragleave", FileDragHover, false);
			filedrag.addEventListener("drop", FileSelectHandler, false);
			filedrag.style.display = "block";

			// remove submit button
			submitbutton.style.display = "none";
		}

	}

	// call initialization file
	if (window.File && window.FileList && window.FileReader) {
		Init();
	}


})();
