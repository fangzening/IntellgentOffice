
//table function
function myFunction() {
  var checkBox = document.getElementById("check1");
  var text = document.getElementById("entertainment");
  if (checkBox.checked == true){
    text.style.display = "block";
  } else {
    text.style.display = "none";
  }
}



//add new table
function addRw(tableID)
{

  var table = document.getElementById(tableID);

  var rowCount = table.rows.length;
  var row = table.insertRow(rowCount);

  var colCount = table.rows[0].cells.length;
  for(var i=0; i<colCount; i++)
  {
    var newcell	= row.insertCell(i);

    newcell.innerHTML = table.rows[0].cells[i].innerHTML;
    //alert(newcell.childNodes);
    switch(newcell.childNodes[0].type)
    {
      case "text":
      newcell.childNodes[0].value = "";
      break;
      case "checkbox":
      newcell.childNodes[0].checked = false;
      break;
      case "select-one":
      newcell.childNodes[0].selectedIndex = 0;
      break;
    }
  }
}

//delete the added table using a checkbox
function deleteRow(tableID) {
  try {
    var table = document.getElementById(tableID);
    var rowCount = table.rows.length;

    for(var i=0; i<rowCount; i++) {
      var row = table.rows[i];
      var chkbox = row.cells[0].childNodes[0];
      if(null != chkbox && true == chkbox.checked) {
        if(rowCount <= 1) {
          alert("Cannot delete all the rows.");
          break;
        }
        table.deleteRow(i);
        rowCount--;
        i--;
      }


    }
  }catch(e) {
    alert(e);
  }
}

function submit (){
  var table = document.getElementById(tableID);
  var rowCount = table.rows.length;
}








//DOM elements
const DOMstrings = {
  stepsBtnClass: 'multisteps-form__progress-btn',
  stepsBtns: document.querySelectorAll(`.multisteps-form__progress-btn`),
  stepsBar: document.querySelector('.multisteps-form__progress'),
  stepsForm: document.querySelector('.multisteps-form__form'),
  stepsFormTextareas: document.querySelectorAll('.multisteps-form__textarea'),
  stepFormPanelClass: 'multisteps-form__panel',
  stepFormPanels: document.querySelectorAll('.multisteps-form__panel'),
  stepPrevBtnClass: 'js-btn-prev',
  stepNextBtnClass: 'js-btn-next' };


  //remove class from a set of items
  const removeClasses = (elemSet, className) => {

    elemSet.forEach(elem => {

      elem.classList.remove(className);

    });

  };

  //return exact parent node of the element
  const findParent = (elem, parentClass) => {

    let currentNode = elem;

    while (!currentNode.classList.contains(parentClass)) {
      currentNode = currentNode.parentNode;
    }

    return currentNode;

  };

  //get active button step number
  const getActiveStep = elem => {
    return Array.from(DOMstrings.stepsBtns).indexOf(elem);
  };

  //set all steps before clicked (and clicked too) to active
  const setActiveStep = activeStepNum => {

    //remove active state from all the state
    removeClasses(DOMstrings.stepsBtns, 'js-active');

    //set picked items to active
    DOMstrings.stepsBtns.forEach((elem, index) => {

      if (index <= activeStepNum) {
        elem.classList.add('js-active');
      }

    });
  };

  //get active panel
  // const getActivePanel = () => {
  //
  //   let activePanel;
  //
  //   DOMstrings.stepFormPanels.forEach(elem => {
  //
  //     if (elem.classList.contains('js-active')) {
  //
  //       activePanel = elem;
  //
  //     }
  //
  //   });
  //
  //   return activePanel;
  //
  // };

  // //open active panel (and close unactive panels)
  // const setActivePanel = activePanelNum => {
  //
  //   //remove active class from all the panels
  //   removeClasses(DOMstrings.stepFormPanels, 'js-active');
  //
  //   //show active panel
  //   DOMstrings.stepFormPanels.forEach((elem, index) => {
  //     if (index === activePanelNum) {
  //
  //       elem.classList.add('js-active');
  //
  //       setFormHeight(elem);
  //
  //     }
  //   });
  //
  // };

  //set form height equal to current panel height
  // const formHeight = activePanel => {
  //
  //   const activePanelHeight = activePanel.offsetHeight;
  //
  //   DOMstrings.stepsForm.style.height = `${activePanelHeight}px`;
  //
  // };
  //
  // const setFormHeight = () => {
  //   const activePanel = getActivePanel();
  //
  //   formHeight(activePanel);
  // };

  //STEPS BAR CLICK FUNCTION
  DOMstrings.stepsBar.addEventListener('click', e => {

    //check if click target is a step button
    const eventTarget = e.target;

    if (!eventTarget.classList.contains(`${DOMstrings.stepsBtnClass}`)) {
      return;
    }

    //get active button step number
    const activeStep = getActiveStep(eventTarget);

    //set all steps before clicked (and clicked too) to active
    setActiveStep(activeStep);

    //open active panel
    setActivePanel(activeStep);
  });

  //PREV/NEXT BTNS CLICK
  DOMstrings.stepsForm.addEventListener('click', e => {

    const eventTarget = e.target;

    //check if we clicked on `PREV` or NEXT` buttons
    if (!(eventTarget.classList.contains(`${DOMstrings.stepPrevBtnClass}`) || eventTarget.classList.contains(`${DOMstrings.stepNextBtnClass}`)))
    {
      return;
    }

    //find active panel
    const activePanel = findParent(eventTarget, `${DOMstrings.stepFormPanelClass}`);

    let activePanelNum = Array.from(DOMstrings.stepFormPanels).indexOf(activePanel);

    //set active step and active panel onclick
    if (eventTarget.classList.contains(`${DOMstrings.stepPrevBtnClass}`)) {
      activePanelNum--;

    } else {

      activePanelNum++;

    }

    setActiveStep(activePanelNum);
    setActivePanel(activePanelNum);

  });
  //
  // //SETTING PROPER FORM HEIGHT ONLOAD
  // window.addEventListener('load', setFormHeight, false);

  //SETTING PROPER FORM HEIGHT ONRESIZE
  window.addEventListener('resize', setFormHeight, false);


  const setAnimationType = newType => {
    DOMstrings.stepFormPanels.forEach(elem => {
      elem.dataset.animation = newType;
    });
  };

  //selector onchange - changing animation
  const animationSelect = document.querySelector('.pick-animation__select');

  animationSelect.addEventListener('change', () => {
    const newAnimationType = animationSelect.value;

    setAnimationType(newAnimationType);
  });
focusScrollMethod = function getFocus() {
  document.getElementById("travel_datefrom").focus({preventScroll:false});
}
