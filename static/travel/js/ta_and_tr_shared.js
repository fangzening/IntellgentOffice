// These are functions that both TA and TR use

function change_approver_list_type(){
    var chosen_value = document.getElementById('add_approver_action').value;
    console.log("Chosen value: " + chosen_value.toString());
    if (chosen_value === "Add to approval list"){
        document.getElementById('approvers_options_label').innerHTML = "Approver: <br><i>use shift to select multiple people</i>";
        document.getElementById('add_approvers_options').setAttribute("multiple", "true");
    }
    else{
        document.getElementById('approvers_options_label').innerHTML = "Approver: ";
        document.getElementById('add_approvers_options').removeAttribute("multiple");
        document.getElementById('add_approvers_options').selectedIndex =0;
    }
}