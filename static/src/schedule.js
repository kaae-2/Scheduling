function createOutputTable() {
  var output = JSON.parse(localStorage.getItem("output"));
  createResTable(output);
  createActTable(output);
}

function openTab(evt, tabName) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

function createActTable(output) {
  var outputActTable = document.createElement("table");
  outputActTable.setAttribute("id", "outputActTable"); // SET THE TABLE ID.
  outputActTable.setAttribute("border", "1");
  // console.log(output);

  var actArray = [""];
  for (var i in output) {
    //console.log(i, output[i]);
    for (var j in output[i]["role_actor"]) {
      if (!actArray.includes(output[i]["role_actor"][j]["actor"])) {
        actArray.push(output[i]["role_actor"][j]["actor"]);
      }
    }
  }
  actArray.sort();
  var tr = outputActTable.insertRow(-1);
  for (var h = 0; h < actArray.length; h++) {
    var th = document.createElement("th"); // TABLE HEADER.
    th.innerHTML = actArray[h];
    tr.appendChild(th);
  }
  var div = document.getElementById("outputAct");
  div.appendChild(outputActTable); // ADD THE TABLE TO YOUR WEB PAGE.

  for (var i in output) {
    var empTab = document.getElementById("outputActTable");

    var rowCnt = empTab.rows.length; // GET TABLE ROW COUNT.
    var tr = empTab.insertRow(rowCnt); // TABLE ROW;
    for (var c = 0; c < actArray.length; c++) {
      var td = document.createElement("td"); // TABLE DEFINITION.
      td = tr.insertCell(c);
      if (c == 0) {
        ele = document.createTextNode(String(i));
        console.log(i);
        //ele.setAttribute("value", String(i));

        td.appendChild(ele);
      } else
        for (var j in output[i]["role_actor"]) {
          if (output[i]["role_actor"][j]["actor"] == actArray[c]) {
            td.appendChild(
              document.createTextNode(
                "Role: " + output[i]["role_actor"][j]["role"]
              )
            );
            td.appendChild(document.createElement("br"));
            td.appendChild(
              document.createTextNode("Restaurant: " + output[i]["restaurant"])
            );
            td.appendChild(document.createElement("br"));
            td.appendChild(
              document.createTextNode("Scene: " + output[i]["scene"])
            );
          }
        }
    }
  }
}

function createResTable(output) {
  var outputResTable = document.createElement("table");
  outputResTable.setAttribute("id", "outputResTable"); // SET THE TABLE ID.
  outputResTable.setAttribute("border", "1");
  // console.log(output);

  var resArray = [""];
  for (var i in output) {
    //console.log(i, output[i]);
    if (!resArray.includes(output[i]["restaurant"])) {
      resArray.push(output[i]["restaurant"]);
      //console.log(output[i]["restaurant"]);
    }
  }
  resArray.sort();
  var tr = outputResTable.insertRow(-1);
  for (var h = 0; h < resArray.length; h++) {
    var th = document.createElement("th"); // TABLE HEADER.
    th.innerHTML = resArray[h];
    tr.appendChild(th);
  }
  var div = document.getElementById("outputRes");
  div.appendChild(outputResTable); // ADD THE TABLE TO YOUR WEB PAGE.

  for (var i in output) {
    var empTab = document.getElementById("outputResTable");

    var rowCnt = empTab.rows.length; // GET TABLE ROW COUNT.
    var tr = empTab.insertRow(rowCnt); // TABLE ROW;
    for (var c = 0; c < resArray.length; c++) {
      var td = document.createElement("td"); // TABLE DEFINITION.
      td = tr.insertCell(c);
      if (c == 0) {
        ele = document.createTextNode(String(i));
        console.log(i);
        //ele.setAttribute("value", String(i));

        td.appendChild(ele);
      } else if (output[i]["restaurant"] == resArray[c]) {
        td.appendChild(document.createTextNode("Scene: " + output[i]["scene"]));
        for (pair in output[i]["role_actor"]) {
          td.appendChild(document.createElement("br"));
          td.appendChild(
            document.createTextNode(
              output[i]["role_actor"][pair]["actor"] +
                ": " +
                output[i]["role_actor"][pair]["role"]
            )
          );
        }
      }
    }
  }
}
