
$('#item_detail').on('click', 'input[type="button"]', function() {
  $(this).closest('tr').remove();
})
$('p input[type="button"]').click(function() {
  $('#myTable').append('<tr><td><input type="text" class="fname" /></td><td><input type="button" value="Delete" /></td></tr>')
});




// Delete row on delete button click
$(document).on("click", ".delete", function() {
  if (confirm("Are you sure you want to clear all information?\n\nNote: Information deleted cannot be retrieved.\n\n\t\t\tOK to proceed.")) {
    if ($(this).parents('table').find('tr').length > 2) {
      $(this).parents("tr").remove();CheckBU();
    }

  }
  return false;

});

function Notify() {
  alert("Sorry, I cannot delete all Rows!");
}



//Mainly to add new Row

//Add multiple attachment function

  var maximum=10;
  var current=1;
  function add_new_attachment(){
  if(current<maximum){
  current++;
  attachmentinputstring='<div class="form-row"> <div class="form-group col-md-5"> <input type="file" class="form-control" id="attachment" name="attachment" required></div><div class="form-group col-md-6"> <textarea class="form-control" id="attachment_description" name="attachment_description" placeholder="File Description" required></textarea></div> <div class="form-group col-md-1"> <button type="button" class="btn btn-danger btn-group deletethat" data-toggle="tooltip" data-placement="top" title="Delete Row"><i class="icon_trash"></i></button> </div></div>'

      $('#attachments').append(attachmentinputstring);}
       else
{
alert('You Reached the limits')
}

  }

   $('#attachments').on("click",".deletethat", function(e)
   {
       e.preventDefault();
       $(this).parent('div').parent('div').remove();
       current--;
  })



//Check BU
function CheckBU() {
cccodes=[]
 $("select[name='selected_cc_expense_item']").each(function() {
    cccodes.push($(this).val())
 });

$.getJSON('../checkBU/', {"cccode": cccodes},
    function(data){

    var options = ' <option disabled selected value>-- select a BU according to cost center(s) above --</option>';

for (var i = 0; i < data.length; i++) {
options += '<option value="' + data[i].pk + '">' + data[i].pk+ '</option>';
}
$("select#BU").html(options);
});
}

//function to add new use tax

function add_new_use_tax(){
     assetinputstring='<div><label>GL account:</label><select class="form-control" name="selected_GL_account" required>{% for gl in GL_accounts %}<option value="gl">{{gl.glCode}}</option>{% endfor %}</select><label>card type:</label><select class="form-control" name="selected_card_type" required><option value="C">credit</option><option value="D">debit</option></select><label>amount:</label><input  name="item_amount" type="number" step="0.01" max="9999999999999.99" min="0.00"placeholder="0.00" required><label>Cost center:</label><select class="form-control" name="selected_cc_use_tax" required>{% for cc in cost_centers %}<option value="{{cc.costCenterCode}}">{{ cc.costCenterName }}</option>{% endfor %}</select><label>text:</label><input  name="item_text" type="text" required><label>assignment:</label><input  name="item_assignment" type="text" required><a href="#" class="delete">Delete</a><br/></div>'
        $('#use_tax').append(assetinputstring);
    }
     $('#use_tax').on("click",".delete", function(e){
        e.preventDefault(); $(this).parent('div').remove();
    })




//function to add new item
// function add_new_item(){
//  iteminputstring=' <div><label>name:</label><input  name="item_name" type="text" required><label>description:</label><input  name="item_description" type="textarea" required><label>amount:</label><input  name="item_amount" type="number" step="0.01" max="9999999999999.99" min="0.00"placeholder="0.00" required> <label>Cost center:</label><select class="form-control" name="selected_cc_expense_item" onchange="CheckBU()" required> <option disabled selected value>-- select a cost center --</option>{% for cc in cost_centers %}<option value="{{cc.costCenterCode}}">{{ cc.costCenterName }}</option>{% endfor %}</select><a href="#" class="delete">Delete</a><br/></div>'
//     $('#expense_item').append(iteminputstring);
// }
// $('#expense_item').on("click",".delete", function(e){
//     e.preventDefault(); $(this).parent('div').remove();CheckBU();
// })
//


//date function
var today = new Date();
var dd = today.getDate();
var mm = today.getMonth()+1; //January is 0!
var yyyy = today.getFullYear();
 if(dd<10){
        dd='0'+dd
    }
    if(mm<10){
        mm='0'+mm
    }

today = yyyy+'-'+mm+'-'+dd;
document.getElementById("payment_date").setAttribute("min", today);
