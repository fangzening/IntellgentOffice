//Feel free to add extra helper functions here.


function ChangeToReadOnly(id)
{
    document.getElementById(id).readOnly = true;
}

function CheckComplete (count, defaultValue)
{
    let isComplete = false;
    count = defaultValue ? isComplete=true : isComplete;
    return isComplete;
}