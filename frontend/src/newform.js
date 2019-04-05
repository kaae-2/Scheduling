function addRow(e) {
  e.preventDefault();
  console.log("Hello World");
}

/* var table = document.getElementsByClassName(" table order-list");
  var newRow = "<tr>";
  var cols = "";

  cols +=
    '<td><input type="text" class="form-control" name="name' +
    counter +
    '"/></td>';
  cols +=
    '<td><input type="text" class="form-control" name="mail' +
    counter +
    '"/></td>';
  cols +=
    '<td><input type="text" class="form-control" name="phone' +
    counter +
    '"/></td>';

  cols +=
    '<td><input type="button" class="ibtnDel btn btn-md btn-danger "  value="Delete"></td>';
  newRow += cols;
  table.innerHTML += newRow;
  counter++;
} */

var counter = 0;

window.onload = () => {
  document
    .getElementById("addrow")
    .addEventListener("click", addRow(event), false);
};
