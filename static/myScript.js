function checkanswer(the_id, the_answer){
  var x = String(the_id);
  var y = String(the_answer);

  if (x == y){
    document.getElementById("correct_animation").style.display = "block";
    document.getElementById("worng_animation").style.display = "none";
  }
  else{
    document.getElementById("correct_animation").style.display = "none";
    document.getElementById("worng_animation").style.display = "block";
  }
}

function checkRegister(form){
  if (form.username.value = ""){
    alert("Missing email");
    form.username.focus();
    return Flase;
  }
  else if (form.password.value = ""){
    alert("Missing password");
    form.password.focus();
    return Flase;
  }
  else if (form.comfirmation.value = ""){
    alert("Missing comfirmation");
    form.confirmation.focus();
    return Flase;
  }

  return True;
}
