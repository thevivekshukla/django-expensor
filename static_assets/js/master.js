
$(document).ready(function(){

  $('[data-toggle="tooltip"]').tooltip();
  
  $("#id_search").autocomplete({
    source: "/autocomplete/get_remark/",
  });

});


