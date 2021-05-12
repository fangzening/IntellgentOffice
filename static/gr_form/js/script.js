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
                        'position': 'absolute'
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


// Delete row on delete button click
// $(document).on("click", ".delete", function() {
//
//   bootbox.confirm({
//     message: "Are you sure you want to clear all information? Note: Information deleted cannot be retrieved. Click OK to proceed.",
//     title: "Do you want to delete Row?",
//     size:"small",
//     show:true,
//     backdrop: true,
//     closeButton:true,
//     animate:true,
//     buttons :
//      {
//         confirm:
//         {
//           label : 'Yes',
//           className: 'btn-success',
//         },
//         cancel: {
//           label:'No',
//           className: 'btn-danger'
//         },
//     },
//     callback: function (result)
//     {
//       if (result === true)
//       $(document).on("click", ".delete", function()
//       {
//         {
//           if ($(this).parents('table').find('tr').length > 1)
//           {
//             $(this).parents("tr").remove();
//           }
//         }
//           return false;
//         })
//     }
//
//   })
// });

// Delete row on delete button click
// $(document).on("click", ".delete", function() {
//   if (confirm("Are you sure you want to clear all information?\n\nNote: Information deleted cannot be retrieved.\n\n\t\t\tOK to proceed.")) {
//     if ($(this).parents('table').find('tr').length > 3) {
//       $(this).parents("tr").remove();
//     }
//
//   }
//   return false;
//
// });

// Mainly to add new Row
var therowIndex = 0;

$("#addnew_item").on('click', function () {

    var checkbox = "";

    var newRow = '<tr>' + checkbox +
        '<td hidden><input hidden onkeyup="widthauto(this)" id="asset_number_' + therowIndex + '"  name="asset_number" placeholder = "Asset Number ' + therowIndex + ' " type="text"  class="form-control numberinput"/></td>"' +
        '<td><input onkeyup="widthauto(this)" maxlength="25" id="supplier_pn_' + therowIndex + '" name="supplier_pn" placeholder = "Supplier ' + therowIndex + ' " type="text"  class="form-control"/></td>"' +
        '<td><input onkeyup="widthauto(this)" maxlength="25" id="item_description_' + therowIndex + '" name="item_description" placeholder = "Description ' + therowIndex + ' " type="text"  class="form-control"/></td>"' +
        '<td><select onkeyup="widthauto(this)" onchange="update_cost_center_code();" id="department_' + therowIndex + '" name="department" type="text" class="custom-select custom-select-lg mb-3"><option></option></select></td>"' +
        '<td><input onkeyup="widthauto(this)" id="cost_center_' + therowIndex + '" name="cost_center" placeholder = "C.Center ' + therowIndex + ' " type="text" readonly class="form-control"/></td>"' +
        '<td><input onkeyup="widthauto(this)" maxlength="12" id="unit_price_' + therowIndex + '" name="unit_price" placeholder = "Unit Price ' + therowIndex + ' " type="text"  class="form-control numberinput"/></td>"' +
        '<td><input onkeyup="widthauto(this)" maxlength="12" id="quantity_' + therowIndex + '" name="quantity" placeholder = "Qty ' + therowIndex + ' " type="text"  class="form-control numberinput"/></td>"' +
        '<td><input onkeyup="widthauto(this)" maxlength="12" id="amount_' + therowIndex + '" name="amount" placeholder = "Amount ' + therowIndex + ' " type="text"  class="form-control numberinput"/></td>"' +
        '<td><input onkeyup="widthauto(this)" id="subtotal' + therowIndex + '" name="subtotal" type="number" class="form-control"   placeholder="$0.00 ' + therowIndex + '" readonly></td>"' +
        '<td><input onkeyup="widthauto(this)" maxlength="25" id="material_group_' + therowIndex + '" name="material_group" placeholder = "Material Group ' + therowIndex + ' " type="text"  class="form-control"/></td>"' +
        '<td hidden><select hidden onkeyup="widthauto(this)" onchange="update_gl_descriptions();" id="gl_account_' + therowIndex + '" name="gl_account"' + therowIndex + ' " type="text" class="custom-select custom-select-lg mb-3"><option></option></select></td>"' +
        '<td hidden><input hidden onkeyup="widthauto(this)" id="gl_description_' + therowIndex + '" name="gl_description" placeholder = "GL Description ' + therowIndex + ' " type="text" readonly class="form-control"/>' +
        '<input hidden readonly name="template_item_id" value="' + therowIndex + '"></td>"' +
        '<td><button type="button" class="btn btn-danger btn-group delete" data-toggle="tooltip" data-placement="top" title="Delete Row">\n' +
        '                                                    <i class="icon_trash"></i>\n' +
        '                                                </button></td>"' +
        '</tr>';

    if ($("#item_detail > tbody > tr").is("*"))
        $("#item_detail > tbody > tr:last").after(newRow)
    else $("#item_detail > tbody").append(newRow)

    populate_gl_accounts('gl_account_' + therowIndex);
    populate_departments('department_' + therowIndex);
    widthauto(document.getElementById('department_' + therowIndex));
    update_gl_descriptions();
    update_cost_center_code();
    limitInput();

    therowIndex++;

});


function generatepr() {
    var seq = 0;
    seq = seq + 1;
    var number = '0000'.substr(String(seq).length) + seq;
    var todaydate = new Date();
    var day = todaydate.getDate();
    var month = todaydate.getMonth() + 1;
    var year = todaydate.getFullYear();
    if (month < 10) month = '0' + month;
    if (day < 10) day = '0' + day;
    var comp = document.getElementById('company').value;
    var datestring = comp + year + "" + month + "" + day + "" + number;


    document.getElementById("pr_number").value = datestring;
}

function itemDetail() {
    var rows = document.getElementsByName("asset_number");

    for (let i = 0; i < rows.length; i++) {

        var id_split = rows[i].id.toString().split("_");

        var id_number = id_split[id_split.length - 1];

        //console.log("id checking: " + id_number);
        //console.log("asset id checking: " + "asset_number_" + id_number);
        var assetNumber = document.getElementById("asset_number_" + id_number).value;
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
        $("input[id^=" + asset_num + "]").val(assetNumber);
        $("input[id^=" + supplier_pn + "]").val(assetSupplierPN);
        $("input[id^=" + item_desc + "]").val(assetItemDescription);
        $("input[id^=" + department_disp + "]").val(assetDepartment);
        $("input[id^=" + ccd + "]").val(assetCostCenter);
        $("input[id^=" + upd + "]").val(assetUnitPrice);
        $("input[id^=" + qd + "]").val("1");
        $("input[id^=" + ad + "]").val(assetAmount);
        $("input[id^=" + mgd + "]").val(assetMaterialGroup);
        $("input[id^=" + glad + "]").val(assetGLAccount);
        $("input[id^=" + gldd + "]").val(assetGLDescription);
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
                            var gl_stuff = "";
                            rows = "<tr id=\"displaymodalheader\"><th>Supplier PN</th><th>Item Description</th><th>Department</th><th>Cost Center</th><th>Unit Price</th><th>Quantity</th><th>Item Amount</th><th>Material Group</th>" + gl_stuff + "<th>Asset Class</th><th>Tech Category 1</th><th>Tech Category 2</th><th>Tech Category 3</th><th>Tech Category 4</th></tr>";
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
                                rows += "<tr name='item_asset_" + id_number + "'><td><input type='number' readonly class='form-control' name='asset_numberdisplay' placeholder='Asset Number'  id='" + "asset_numberdisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' readonly class='form-control' name='supplier_pndisplay' placeholder='Suppllier' id='" + "supplier_pndisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' readonly class='form-control' name='item_descriptiondisplay' placeholder='Description' id='" + "item_descriptiondisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' readonly class='form-control' name='departmentdisplay' placeholder='Department' id='" + "departmentdisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' readonly class='form-control' name='cost_centerdisplay' placeholder='C. Center' id='" + "cost_centerdisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='number' readonly class='form-control' name='unit_pricedisplay' placeholder='Unit Price' id='" + "unit_pricedisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='number' readonly class='form-control' name='quantitydisplay' placeholder='QTY' id='" + "quantitydisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='number' readonly class='form-control' name='amountdisplay' placeholder='Amount' id='" + "amountdisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' readonly class='form-control' name='material_groupdisplay' placeholder='Material Group' id='" + "material_groupdisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' readonly class='form-control' name='gl_accountdisplay' placeholder='GL Account' id='" + "gl_accountdisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' readonly class='form-control' name='gl_descriptiondisplay' placeholder='GL Description' id='" + "gl_descriptiondisplay_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' class='form-control' name='asset_class' placeholder='Asset Class' id='" + "asset_class_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td> <input type='text' class='form-control' maxlength=\"50\" name='tech_category1' placeholder='Tech Category 1' id='" + "tech_category1_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td><input type='text' class='form-control' maxlength=\"50\" name='tech_category2' placeholder='Tech Category 2' id='" + "tech_category2_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td> <input type='text' class='form-control' maxlength=\"50\" name='tech_category3' placeholder='Tech Category 3' id='" + "tech_category3_" + id_number + "_".concat(i + 1) + "'></td>" +
                                    "<td> <input type='text' class='form-control' maxlength=\"50\" name='tech_category4' placeholder='Tech Category 4' id='" + "tech_category4_" + id_number + "_".concat(i + 1) + "'>" +
                                    "<input name='template_asset_id' value='" + id_number + "' readonly hidden></td></tr>";
                            }
                        }
                        //}

                        document.getElementById("displaymodalbody").insertAdjacentHTML("beforeend", rows);
                        itemDetail();
                    }
                }

            }
        })
    } else {
        console.log("begin unchecked function");
        // If user unchecked the check box
        var a;
        var master_quantity = document.getElementById("quantity_" + checked_id);

        //for (let j = 0; j < master_quantities.length; j++) {
        var quantity_id_num = master_quantity.id.split("_")[master_quantity.id.split("_").length - 1];

        //console.log("id checked: " + "approver_check_" + quantity_id_num.toString());

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

        var assets_to_delete = document.getElementsByName("item_asset_" + id_number);
        console.log("removing assets with name : " + "item_asset_" + id_number);
        console.log("assets to remove: " + assets_to_delete.toString());

        console.log("assets to delete length: " + assets_to_delete.length); // Length is correct here, but once i start the loop
        for (let i = 0; i !== assets_to_delete.length; i) {                 // It goes down each time an asset is removed, so wait until length gets to 0
            console.log("assets to delete length inside: " + assets_to_delete.length);
            console.log('removing asset: ' + assets_to_delete[i].toString());
            assets_to_delete[i].parentNode.removeChild(assets_to_delete[i]);
        }

        console.log("end unByIdchecked function");
    }
    //}
}

//
// $(document).ready(function () {
//   $("#moreInfo").click(function () {
//     $("#more_info").toggle();
//   });
// });

   $(document).on("click", ".delete", function () {
        $(this).parent('div','div').remove();
        return false;

    })


function widthauto(textbox) {
    $(textbox).parent().css("width", (textbox.value.length + 2) + "em");
}


document.getElementById("show_table").addEventListener("click", function (button) {
    if (document.getElementById("item_detail").style.display === "none")
        document.getElementById("item_detail").style.display = "block";
    else document.getElementById("item_detail").style.display = "none";
});


document.getElementById("show_table").addEventListener("click", function (button) {
    if (document.getElementById("addnew_item").style.display === "none")
        document.getElementById("addnew_item").style.display = "block";
    else document.getElementById("addnew_item").style.display = "none";
});

document.getElementById('show_table').addEventListener("click", function (mouseEvent) {
    document.getElementById("show_table").style.display = "none";
});


function add_attachment() {
        dynamic_attachment = '<div><div class="form-group col-md-5"> <input type="file" class="form-control" id="attachment" name="attachment"></div><div class="form-group col-md-6"><textarea class="form-control" id="attachment_description" name="attachment_description" placeholder="File Description"></textarea></div><button type="button"  href="#" data-toggle="tooltip" data-placement="top" title="Delete" class="btn btn-danger delete  col-md-1"><i class="icon_trash"></i></button></div>';
        $('#attachments').append(dynamic_attachment);
    }


   // $(document).on("click", ".delete", function () {
   //     alert("Test");
   //
   //      $(this).parents('div').remove();
   //      return false;
   //
   //  })


// $(document).on("click", ".delete", function() {
//   if (confirm("Are you sure you want to clear all information?\n\nNote: Information deleted cannot be retrieved.\n\n\t\t\tOK to proceed.")) {
//     if ($(this).parents('table').find('tr').length > 3) {
//       $(this).parents("tr").remove();
//     }
//
//   }
//   return false;
//
// });


//Delete row on delete button click
$('#attachments').on("click", ".delete", function () {

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

            $(this).parent('div').remove();{
            // if ($(this).parents('table').find('tr').length > 3) {
            //     $(this).parents("tr").remove();
                swalWithBootstrapButtons.fire(
                    'Deleted!',
                    'Your item has been deleted.',
                    'success'
                )
            // } else {
                swalWithBootstrapButtons.fire(
                    'Noooooo!',
                    'Please note you cannot delete all items!!!',
                    'Error'
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

