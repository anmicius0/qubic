function checkanswer(the_id, the_answer, solution){
  var x = String(the_id);
  var y = String(the_answer);

  if (x == y){
    swal("Correct!", solution, "success");
    document.getElementById("correct-record").submit();
  }
  else{
    swal("No no", solution, "error");
    document.getElementById("wrong-record").submit();
  }
}

function submit(the_id){
  document.getElementById(the_id).submit();
}
