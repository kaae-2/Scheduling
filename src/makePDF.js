const jsPDF = require("jspdf");
const html2canvas = require("html2canvas");

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
  html2canvas(document.getElementById("outputRes")).then(canvas => {
    var contentWidth = canvas.width;
    var contentHeight = canvas.height;

    //The height of the canvas which one pdf page can show;
    var pageHeight = (contentWidth / 592.28) * 841.89;
    //the height of canvas that haven't render to pdf
    var leftHeight = contentHeight;
    //addImage y-axial offset
    var position = 15;
    //a4 format [595.28,841.89]
    var imgWidth = 595.28;
    var imgHeight = (592.28 / contentWidth) * contentHeight;

    var pageData = canvas.toDataURL("image/jpeg", 1.0);

    var pdf = new jsPDF("", "pt", "a4");

    if (leftHeight < pageHeight) {
      pdf.addImage(pageData, "JPEG", 0, 0, imgWidth, imgHeight);
    } else {
      while (leftHeight > 25) {
        pdf.addImage(pageData, "JPEG", 0, position, imgWidth, imgHeight);
        leftHeight -= pageHeight;
        position -= 841.89;
        //avoid blank page
        if (leftHeight > 25) {
          pdf.addPage();
        }
      }
    }
    /*  doc.fromHTML(
    document.getElementById("outputRes"),
    margins.left,
    margins.top,
    {
      width: margins.width,
      elementHandlers: elementHandler,
      autoSize: true,
      fontSize: 9
    }
  ); */
    pdf.save("output.pdf");
    //pdf.output("dataurlnewwindow");
    //doc.save("output.pdf");
  });
}
