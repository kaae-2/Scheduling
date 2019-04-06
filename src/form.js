// ARRAY FOR HEADER.
var headerArray = new Array();
headerArray = ["Actor", "Start shift", "End shift", ""]; // SIMPLY ADD OR REMOVE VALUES IN THE ARRAY FOR TABLE HEADERS.

const actors = {
  PA: "Pernille A",
  PP: "Pernille P",
  LE: "Le",
  AH: "Ann Hjort",
  TD: "Terese",
  TK: "Thomas",
  AU: "Peter",
  AA: "Asbjørn",
  SS: "Sune"
};

function runEngine() {
  var python = require("python-shell");
  var path = require("path");

  var options = {
    scriptPath: path.join(__dirname, "/../../engine/"),
    pythonPath: "/usr/local/bin/python3"
  };

  var face = new python("app.py", options);

  face.end((err, code, message) => {
    console.log(code);
  });
}

// FIRST CREATE A TABLE STRUCTURE BY ADDING A FEW HEADERS AND
// ADD THE TABLE TO YOUR WEB PAGE.
function createTable() {
  var shiftTable = document.createElement("table");
  shiftTable.setAttribute("id", "shiftTable"); // SET THE TABLE ID.

  var tr = shiftTable.insertRow(-1);

  for (var h = 0; h < headerArray.length; h++) {
    var th = document.createElement("th"); // TABLE HEADER.
    th.innerHTML = headerArray[h];
    tr.appendChild(th);
  }

  var div = document.getElementById("cont");
  div.appendChild(shiftTable); // ADD THE TABLE TO YOUR WEB PAGE.
  for (var i = 0; i < 3; i++) {
    addRow();
  }
}

// ADD A NEW ROW TO THE TABLE.s
function addRow() {
  var empTab = document.getElementById("shiftTable");

  var rowCnt = empTab.rows.length; // GET TABLE ROW COUNT.
  var tr = empTab.insertRow(rowCnt); // TABLE ROW;

  for (var c = 0; c < headerArray.length; c++) {
    var td = document.createElement("td"); // TABLE DEFINITION.
    td = tr.insertCell(c);

    if (c == headerArray.length - 1) {
      // FIRST COLUMN.
      // ADD A BUTTON.
      var button = document.createElement("input");

      // SET INPUT ATTRIBUTE.
      button.setAttribute("type", "button");
      button.setAttribute("value", "Remove");
      button.setAttribute("class", "btn btn-danger");

      // ADD THE BUTTON's 'onclick' EVENT.
      button.setAttribute("onclick", "removeRow(this)");

      td.appendChild(button);
    } else if (c == 0) {
      var ele = document.createElement("select");
      options = "<select>";
      options += "<option></option>";
      for (var key in actors) {
        options += '<option value="' + key + '">' + actors[key] + "</option>";
      }
      options += "</select>";
      ele.innerHTML = options;

      td.appendChild(ele);
    } else {
      // CREATE AND ADD TEXTBOX IN EACH CELL.
      var ele = document.createElement("input");
      ele.setAttribute("type", "time");
      ele.setAttribute("value", "");
      ele.setAttribute("step", "900");
      //ele.setAttribute("placeholder", "12:00 PM");
      td.appendChild(ele);
    }
  }
}

// DELETE TABLE ROW.
function removeRow(oButton) {
  var empTab = document.getElementById("shiftTable");
  empTab.deleteRow(oButton.parentNode.parentNode.rowIndex); // BUTTON -> TD -> TR.
}

// EXTRACT AND SUBMIT TABLE DATA.
function submit() {
  var myTab = document.getElementById("shiftTable");
  var input = {};
  input["increments"] = document.getElementById("increments").value;
  // LOOP THROUGH EACH ROW OF THE TABLE.
  var act = new Object();
  for (row = 1; row < myTab.rows.length; row++) {
    var actor = myTab.rows[row].cells[0].childNodes[0].value,
      startTime = myTab.rows[row].cells[1].childNodes[0].value,
      endTime = myTab.rows[row].cells[2].childNodes[0].value;
    /*  for (c = 0; c < myTab.rows[row].cells.length; c++) {
      // EACH CELL IN A ROW.

      var element = myTab.rows.item(row).cells[c];

      if (element.childNodes[0].getAttribute("type") != "button") {
        act.push(element.childNodes[0].value);
      }
    } 
    if (act.length > 0) {
      input[shifts] = act;
    }*/
    act[actor] = { start: startTime, end: endTime };
  }

  input["shifts"] = act;
  //input["shifts"][String(actor)] = { start: startTime, end: endTime };

  console.log(input);
  runEngine(input);
}
