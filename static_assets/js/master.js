
$(document).ready(function(){

  $('[data-toggle="tooltip"]').tooltip({
    "placement": "top",
    "html": true
  });
  
  $("#id_expense_search").autocomplete({
    source: "/autocomplete/get_remark/",
  });

  $.datepicker.setDefaults({
    showOn: "focus",
    buttonImage: "/static/images/calendar.gif",
    buttonImageOnly: true,
    dateFormat: "dd/mm/yy",
    changeMonth: true,
    changeYear: true,
    showAnim: "blind",
    showOptions: { direction: "up" },
    showOtherMonths: false,
    selectOtherMonths: true
  });

});


