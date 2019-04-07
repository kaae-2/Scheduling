/* var resArray = new Array();
resArray = [
  "",
  "Varnæs",
  "Lauras køkken",
  "Katrine",
  "Jernbanen",
  "Postgården",
  "Algade"
];  */ // SIMPLY ADD OR REMOVE VALUES IN THE ARRAY FOR TABLE resS.

function createOutputTable() {
  var outputResTable = document.createElement("table");
  var output = JSON.parse(localStorage.getItem("output"));
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
        ele = document.createTextNode(String(output[i]["scene"]));
        td.appendChild(ele);
      }
    }
  }
}
