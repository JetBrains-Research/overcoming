function processCode(editor){

    // const user_id = document.getElementById("task").value
    // const theme = document.getElementById("theme").value
    const code = editor.getValue()
    var resultsContainer = document.getElementById("results");
    var codeResult = document.getElementById("coderesult");
    var codeUpoload = document.getElementById("codeupoload");
    resultsContainer.style.display = "block";

    const server_data = [
      // {"task": formatedQTc},
      // {"theme": heartRate},
      {"code": code},];

    $.ajax({type: "POST",
          url: "/process_code",
          data: JSON.stringify(server_data),
          contentType: "application/json",
          dataType: 'json',
          success: function(result) {
            console.log("Result:");
            console.log(result);
            codeUpoload.innerHTML = result.code_uploaded
          }
});
}

