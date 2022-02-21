function savepdf(data){
    console.log(data)
    let getData = [];
    getData = JSON.parse(data.replaceAll("'", "\""));
    console.log(getData)
    let table = document.createElement("TABLE");
        table.setAttribute('cellpadding', "2");
        table.setAttribute('cellspacing', "0")
        let thead = document.createElement("THEAD");
        let tbody = document.createElement("TBODY");
        console.log(thead,tbody)
        thead.innerHTML = "<tr><th align='center'>Question</th><th align='center'>Answer</th></tr>"
        getData.forEach(function(row) {
            tbody.innerHTML += "<tr><td>" + row[0] + "</td><td>" + row[1] + "</td></tr>"
        })
        console.log(table)
        table.appendChild(thead);
        table.appendChild(tbody);
        console.log(table)
        let doc = new jsPDF('p', 'pt', 'a4');
        let y = 20;
        doc.setLineWidth(2);
        doc.text(250, y + 30, "All Questions");
        doc.autoTable({
            html: table,
            startY: 70,
            theme: 'grid',
            columnStyles: {
                0: {
                    cellWidth: 255,
                },
                1: {
                    cellWidth: 260,
                }
            },
            styles: {
                minCellHeight: 40
            }
        })
        doc.save('QA-genrator.pdf');
        table.remove();

    }

  function savecsv(data){
    let getData=[]
    getData = JSON.parse(data.replaceAll("'", "\""));
    let csv = 'Question, Answer\n';
        getData.forEach(function(row) {
            csv += row[0].split(',').join(' ') + ',' + row[1].split(',').join(' ') + '\n';
        })
        let hiddenElement = document.createElement('a');
        hiddenElement.href = 'data:ion/vnd.ms-excel,' + encodeURIComponent(csv);
        hiddenElement.target = '_blank';
        //provide the name for the CSV file to be downloaded
        hiddenElement.download = 'QA-genrator.csv';
        hiddenElement.click();
  }
