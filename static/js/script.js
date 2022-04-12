function openFile(event1) {
    let input = event.target.files;
    var files = new FormData();
    file = input[0]
    files.append('file', file);
    console.log(files)
    axios({
        type: 'POST',
        url: '/upload_file',
        data: files,
        contentType: false,
        cache: false,
        processData: false,
        success: function (data) {
            if (data.status != 401) {
                upload_file_loader.style.display = 'none';
                let node = document.getElementById('doc-fetched-data');
                node.value = data.file_data;
                $scope.set_document_word_count(data.file_data);
                document.getElementById('doc-fetched-data').style.display = 'block';
                console.log('Success!');
                document.getElementById("upload-file-label").innerHTML = file.name;
                document.getElementById("customFile").title = file.name;
            }
            else {
                upload_file_loader.style.display = 'none';
                $scope.show_snackbar(data['message'], "#F23852");
            }
        },
    });
}

function EnableDisableTextBox() {
    var chkNo = document.getElementById("chkNo");
    var chkYes = document.getElementById("chkYes");
    var link = document.getElementById("link");
    var test = document.getElementById("test");
    var pdf12 = document.getElementById("pdf12");
    var fileUpload = document.getElementById("fileuplode");
    var px = document.getElementById("fileUpload").disabled = true;
    test.disabled = chkYes.checked ? false : true;
    link.disabled = chkNo.checked ? false : true;
    if (!test.disabled) {
        test.focus();
    }
    else if (!link.disabled) {
        link.focus();
    }
    else if (!px.disabled) {
        document.getElementById("fileUpload").disabled = false;
    }
}
function ValidateExtension() {
    var allowedFiles = [".pdf"];
    var fileUpload = document.getElementById("fileUpload");
    var lblError = document.getElementById("lblError");
    var regex = new RegExp("([a-zA-Z0-9\s_\\.\-:])+(" + allowedFiles.join('|') + ")$");
    if (!regex.test(fileUpload.value.toLowerCase())) {
        lblError.innerHTML = "Please upload files having extensions: <b>" + allowedFiles.join(', ') + "</b> only.";
        return false;
    }
    lblError.innerHTML = "";
    return true;
}

function save_pdf(data) {
    console.log(data)
    console.log(typeof (data))
    let getData = [];
    if (data) {
        getData = JSON.parse(data.replaceAll("'", "\""));
    }

    console.log(getData)
    let table = document.createElement("TABLE");
    table.setAttribute('cellpadding', "2");
    table.setAttribute('cellspacing', "0")
    let thead = document.createElement("THEAD");
    let tbody = document.createElement("TBODY");
    console.log(thead, tbody)
    thead.innerHTML = "<tr><th align='center'>Question</th><th align='center'>Answer</th></tr>"
    getData.forEach(function (row) {
        tbody.innerHTML += "<tr><td>" + row['Question'] + row['Paraphrased_Question'] + "</td><td>" + row['Answer'] + "</td></tr>"
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
    doc.save('Generated_QA.pdf');
    table.remove();

}

function save_csv(data) {
    let getData = []
    getData = JSON.parse(data.replaceAll("'", "\""));
    let csv = 'Question,Paraphrased_Question(1),Paraphrased_Question(2),Paraphrased_Question(3), Answer\n';
    getData.forEach(function (row) {
        csv += row['Question'] + ',' +
            row['Paraphrased_Question'][0] + ',' + row['Paraphrased_Question'][1] + ',' +
            row['Paraphrased_Question'][2] + ',' + row['Answer'] + '\n';
    })
    let hiddenElement = document.createElement('a');
    hiddenElement.href = 'data:ion/vnd.ms-excel,' + encodeURIComponent(csv);
    hiddenElement.target = '_blank';
    //provide the name for the CSV file to be downloaded
    hiddenElement.download = 'Generated_QA.csv';
    hiddenElement.click();
}

//check the password or confirm_password is metch or not check validation

function onChange() {
    const password = document.querySelector('input[name=password]');
    const confirm = document.querySelector('input[name=conpassword]');
    if (confirm.value === password.value) {
        confirm.setCustomValidity('');
    } else {
        confirm.setCustomValidity('Passwords do not match');
    }
}
var check = function () {
    if (document.getElementById('password').value ==
        document.getElementById('confirm_password').value) {
        document.getElementById('message').style.color = 'green';
        document.getElementById('message').innerHTML = 'matching';
    } else {
        document.getElementById('message').style.color = 'red';
        document.getElementById('message').innerHTML = 'not matching';
    }
}

function handleFormSubmit(event) {
    event.preventDefault();
    const collection = document.getElementsByClassName("radio-input");
    let anyOneSelected = false;
    for (let i = 0; i < collection.length; i++) {
       if(collection[i].checked) {
           anyOneSelected = true;
           if(!document.getElementById(collection[i].value).value) {
               window.alert("Please provide valid " + collection[i].value);
           }
       }
    }
    if(!anyOneSelected) {
        window.alert("Please select atleast 1 radio button");
    }
    // document.getElementById("my-form").submit();
    document.getElementById("loader").classList.add("loader");
    fetch(event.target.action, {
        method: 'POST',
        body: new URLSearchParams(new FormData(event.target)) // event.target is the form
    }).then((resp) => {
        // or resp.text() or whatever the server sends
    }).then((body) => {
        // TODO handle body
    }).catch((error) => {
        // TODO handle error
    }).finally(() => {
        document.getElementById("loader").classList.remove("loader");
    })
}

