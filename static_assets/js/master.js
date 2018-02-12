
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
  $("#dropdown").on('click', function(){
    $.get("/years/", function(data){
      $("#year-dropdown").html("");

      for (i=0; i<data.length; i++){
        $("#year-dropdown").append('<li><a href="/'+data[i]+'/">'+ data[i] +'</a></li>');
      }

    });
  });

}
