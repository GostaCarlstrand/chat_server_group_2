<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> gosta
function verifyPassword() {
  var pw_repeated = document.getElementById("pswd_repeat").value;
  var pw = document.getElementById("pswd").value;
  //check empty password field
  if(pw == "") {
     document.getElementById("pswd_notification").innerHTML = "Fill the password please!";
     return false;
  }

 //minimum password length validation
  if(pw.length < 8) {
     document.getElementById("pswd_notification").innerHTML = "Password length must be at least 8 characters";
     return false;
  }
  if(pw.length > 15) {
      document.getElementById("pswd_notification").innerHTML = "Password length must not exceed 15 characters";
      return false;
  }


  if (pw == pw_repeated) {
      window.location.replace()
  } else {
      document.getElementById("pswd_notification").innerHTML = "Password does not match";
      return false;
  }


}

function reload_page() {
    window.location.reload();
}
<<<<<<< HEAD
>>>>>>> 4ef7b52e7c724dadf8c5e86ebdee4aff50d13b26
=======
>>>>>>> gosta
