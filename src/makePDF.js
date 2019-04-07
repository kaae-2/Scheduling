const jsPDF = require("jspdf");

var elementHandler = {
  "#ignorePDF": function(element, renderer) {
    return true;
  }
};

margins = {
  top: 80,
  bottom: 60,
  left: 40,
  width: 522
};

function makePDF() {
  var doc = new jsPDF();
  doc.setFontSize(9);
  doc.fromHTML(
    document.getElementById("outputRes"),
    margins.left,
    margins.top,
    {
      width: margins.width,
      elementHandlers: elementHandler,
      autoSize: true,
      fontSize: 9
    }
  );
  doc.output("dataurlnewwindow");

  //doc.save("output.pdf");
}
