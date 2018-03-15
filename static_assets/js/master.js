
$(document).ready(function(){
  $("#id_search").autocomplete({
    source: "{% url 'expense:get_remark' %}",
  });

  years();
});



function update(){
  $(".edit").on("click", function(e){
    e.preventDefault();
    id = $(this).data("id");

    $.ajax({
      url: "/update/"+ id,
      success: function(){
        $("#smsg-"+id).text("Taking you there!");
        window.location.href = "/update/"+ id +"/";
      },
      error: function(){
        $("#emsg-"+id).text("Too late!");

      },
    });
  });
}


function years(){
  $("#year-dropdown").on('click mouseenter', function(){
    $.get("/years/", function(data){
      $("#year-content-dropdown").html("");

      for (i=0; i<data.length; i++){
        $("#year-content-dropdown").append('<li><a href="/'+data[i]+'/">'+ data[i] +'</a></li>');
      }

    });
  });

}
