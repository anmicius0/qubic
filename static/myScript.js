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
