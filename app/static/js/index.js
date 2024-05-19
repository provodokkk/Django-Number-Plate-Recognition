Dropzone.options.myGreatDropzone = {
  autoProcessQueue: false,
  paramName: "file",
  maxFilesize: 2,
  clickable: "#dropZone"
};

function updateFileName(input) {
    var fileName = input.files[0].name;
    var fileNameElement = document.getElementById("file-name");
    fileNameElement.textContent = fileName;
}