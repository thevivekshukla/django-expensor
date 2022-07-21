function showSnackbar(text, timeout) {
    // Get the snackbar DIV
    var x = document.getElementById("snackbar");
    x.innerHTML = text;
    // Add the "show" class to DIV
    x.className = "show";
  
    // After 2 seconds, remove the show class from DIV
    setTimeout(function(){ x.className = x.className.replace("show", ""); }, timeout);
  }