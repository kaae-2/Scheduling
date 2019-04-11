// ARRAY FOR HEADER.
var headerArray = ["Actor", "Start shift", "End shift", ""]; // SIMPLY ADD OR REMOVE VALUES IN THE ARRAY FOR TABLE HEADERS.
var bookingArray = [
  "Restaurant",
  "Add Booking",
  "Current Bookings",
  "Remove Booking",
  ""
]; // SIMPLY ADD OR REMOVE VALUES IN THE ARRAY FOR TABLE HEADERS.

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

var bookingValues = {};
const restaurants = {
  1: "Varnæs",
  2: "Lauras Køkken",
  3: "Katrine",
  4: "Jernbanen",
  5: "Postgården",
  6: "Algade"
};

const times = [
  "12:00",
  "12:15",
  "12:30",
  "12:45",
  "13:00",
  "13:15",
  "13:30",
  "13:45",
  "14:00",
  "14:15",
  "14:30",
  "14:45",
  "15:00",
  "15:15",
  "15:30",
  "15:45",
  "16:00",
  "16:15",
  "16:30",
  "16:45",
  "17:00",
  "17:15",
  "17:30",
  "17:45",
  "18:00",
  "18:15",
  "18:30",
  "18:45",
  "19:00",
  "19:15",
  "19:30",
  "19:45",
  "20:00",
  "20:15",
  "20:30",
  "20:45",
  "21:00",
  "21:15",
  "21:30",
  "21:45"
];

function runEngine(args) {
  const { PythonShell } = require("python-shell");

  const path = require("path");

  var options = {
    scriptPath: path.join(__dirname, "/engine/"),
    //pythonPath: "/usr/local/bin/python3",
    //pythonPath:"C:/Users/fkir0011/AppData/Local/Programs/Python/Python36-32/python.exe",
    encoding: "utf8",
    //mode: "json",
    args: JSON.stringify(args)
  };
  var constraint = new PythonShell("app.py", options);
  console.log(constraint);

  constraint.on("message", message => {
    console.log(message);
    output = message;
  });
  constraint.end((err, code, message) => {
    console.log(output);
    localStorage.setItem("output", JSON.stringify(output));
    window.open("schedule.html");
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
  for (var i = 0; i < 4; i++) {
    addRow();
  }
}

// ADD A NEW ROW TO THE TABLE.
function addRow() {
  var empTab = document.getElementById("shiftTable");

  var rowCnt = empTab.rows.length; // GET TABLE ROW COUNT.
  var tr = empTab.insertRow(rowCnt); // TABLE ROW;

  for (var c = 0; c < headerArray.length; c++) {
    var td = document.createElement("td"); // TABLE DEFINITION.
    td = tr.insertCell(c);

    if (c == headerArray.length - 1) {
      // LAST COLUMN.
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
      ele.required = true;
      options = "<select>";
      options += "<option></option>";
      for (var key in actors) {
        options += '<option value="' + key + '">' + actors[key] + "</option>";
      }
      options += "</select>";
      ele.innerHTML = options;
      td.appendChild(ele);
      // SET INDEX FOR TESTING
      ele.selectedIndex = rowCnt;
    } else if (c == 1) {
      var ele = document.createElement("select");
      options = "<select>";
      for (var key in times) {
        options +=
          '<option value="' + times[key] + '">' + times[key] + "</option>";
      }
      options += "</select>";
      ele.innerHTML = options;
      ele.required = true;
      ele.selectedIndex = 1;
      td.appendChild(ele);
    } else if (c == 2) {
      var ele = document.createElement("select");
      options = "<select>";
      for (var key in times) {
        options +=
          '<option value="' + times[key] + '">' + times[key] + "</option>";
      }
      options += "</select>";
      ele.innerHTML = options;
      ele.required = true;
      // SET INDEX FOR TESTING
      ele.selectedIndex = 32;
      td.appendChild(ele);
    }
  }
}

// DELETE TABLE ROW.
function removeRow(oButton) {
  var empTab = document.getElementById("shiftTable");
  empTab.deleteRow(oButton.parentNode.parentNode.rowIndex); // BUTTON -> TD -> TR.
}

function createBookingTable() {
  var shiftTable = document.createElement("table");
  shiftTable.setAttribute("id", "bookingTable"); // SET THE TABLE ID.
  var tr = shiftTable.insertRow(-1);
  for (var h = 0; h < bookingArray.length; h++) {
    var th = document.createElement("th"); // TABLE HEADER.
    th.innerHTML = bookingArray[h];
    tr.appendChild(th);
  }

  var div = document.getElementById("booking");
  div.appendChild(shiftTable); // ADD THE TABLE TO YOUR WEB PAGE.
  for (var i = 0; i < 2; i++) {
    addBookingRow();
  }
}

function addBookingRow() {
  var empTab = document.getElementById("bookingTable");

  var rowCnt = empTab.rows.length; // GET TABLE ROW COUNT.
  var tr = empTab.insertRow(rowCnt); // TABLE ROW;
  bookingValues[rowCnt] = [];
  for (var c = 0; c < bookingArray.length; c++) {
    var td = document.createElement("td"); // TABLE DEFINITION.
    td = tr.insertCell(c);

    if (c == bookingArray.length - 2) {
      // LAST COLUMN.
      // ADD A BUTTON.
      var button = document.createElement("input");

      // SET INPUT ATTRIBUTE.
      button.setAttribute("type", "button");
      button.setAttribute("value", "X");
      button.setAttribute("class", "btn btn-danger");

      // ADD THE BUTTON's 'onclick' EVENT.
      button.setAttribute("onclick", "removeBooking(this)");
      td.appendChild(button);
    } else if (c == bookingArray.length - 1) {
      // LAST COLUMN.
      // ADD A BUTTON.
      var button = document.createElement("input");

      // SET INPUT ATTRIBUTE.
      button.setAttribute("type", "button");
      button.setAttribute("value", "Remove");
      button.setAttribute("class", "btn btn-danger");

      // ADD THE BUTTON's 'onclick' EVENT.
      button.setAttribute("onclick", "removeBookingRow(this)");
      td.appendChild(button);
    } else if (c == 0) {
      var ele = document.createElement("select");
      ele.required = true;
      options = "<select>";
      options += "<option></option>";
      for (var key in restaurants) {
        options +=
          '<option value="' + key + '">' + restaurants[key] + "</option>";
      }
      options += "</select>";
      ele.innerHTML = options;
      td.appendChild(ele);
      // SET INDEX FOR TESTING
      ele.selectedIndex = rowCnt;
    } else if (c == 1) {
      var ele = document.createElement("select");
      options = "<select>";
      for (var key in times) {
        options +=
          '<option value="' + times[key] + '">' + times[key] + "</option>";
      }
      options += "</select>";
      ele.innerHTML = options;
      ele.required = true;
      ele.setAttribute("onchange", "addToBooking(this)");
      //ele.setAttribute("multiple", true);
      ele.selectedIndex = 1;
      td.appendChild(ele);
    } else if (c == 2) {
      var ele = document.createElement("input");
      ele.setAttribute("type", "text");
      ele.setAttribute("disabled", true);
      ele.value = "";
      ele.required = true;
      // SET INDEX FOR TESTING
      td.appendChild(ele);
    }
  }
}

function addToBooking(change) {
  var empTab = document.getElementById("bookingTable");
  row = change.parentNode.parentNode.rowIndex; // BUTTON -> TD -> TR.
  bookingValues[row].push(change.value);
  empTab.rows[row].cells[2].getElementsByTagName(
    "input"
  )[0].value = bookingValues[row].join();
}

function removeBooking(change) {
  var empTab = document.getElementById("bookingTable");
  row = change.parentNode.parentNode.rowIndex; // BUTTON -> TD -> TR.
  bookingValues[row].pop();
  empTab.rows[row].cells[2].getElementsByTagName(
    "input"
  )[0].value = bookingValues[row].join();
}

function removeBookingRow(oButton) {
  var empTab = document.getElementById("bookingTable");
  empTab.deleteRow(oButton.parentNode.parentNode.rowIndex); // BUTTON -> TD -> TR.
}

// EXTRACT AND SUBMIT TABLE DATA.
function submit() {
  var myTab = document.getElementById("shiftTable");
  var myBooking = document.getElementById("bookingTable");
  var input = {};
  input["increment"] = document.getElementById("increment").value;
  // LOOP THROUGH EACH ROW OF THE TABLE.
  var act = new Object();
  var duplicates = [];
  for (row = 1; row < myTab.rows.length; row++) {
    // ERROR CHECKING
    if (duplicates.includes(myTab.rows[row].cells[0].childNodes[0].value)) {
      alert(
        "Please choose distinct actors. No 2 rows can contain the same actor."
      );
      return;
    } else {
      duplicates.push(myTab.rows[row].cells[0].childNodes[0].value);
    }
    for (cell = 0; cell < myTab.rows[row].cells.length - 1; cell++) {
      if (myTab.rows[row].cells[cell].childNodes[0].value == "") {
        console.log("lol");
        alert("Please fill out all rows to run the programme.");
        return;
      }
    }
    var actor = myTab.rows[row].cells[0].childNodes[0].value,
      startTime = myTab.rows[row].cells[1].childNodes[0].value,
      endTime = myTab.rows[row].cells[2].childNodes[0].value;
    act[actor] = { start: startTime, end: endTime };
  }

  input["shifts"] = act;
  res = {};
  for (row = 1; row < myBooking.rows.length; row++) {
    var restaurant = myBooking.rows[row].cells[0].childNodes[0].value,
      bookings = bookingValues[row];
    if (bookings.length > 0) {
      res[restaurant] = bookings;
    }
  }
  input["bookings"] = res;
  console.log(input);
  runEngine(input);
}
