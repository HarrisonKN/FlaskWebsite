function openTab(tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }
    document.getElementById(tabName).style.display = "block";
    event.currentTarget.classList.add("active");
}

function addNote(color,fontSize) {
    // Create a new textarea element
    var newTextArea = document.createElement("textarea");
    newTextArea.classList.add("NotePadArea");
    newTextArea.placeholder = "Enter your note here";
    newTextArea.style = "margin: 5px; margin-top:20px; font-size:"+fontSize+";";
    // Append the new textarea to the note pad
    document.getElementById("NotePad").appendChild(newTextArea);
}