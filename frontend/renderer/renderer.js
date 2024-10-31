const fileInputAlert = document.getElementById("file-input-alert");
const fileFormatSelect = document.getElementById("options");

const submitButton = document.getElementById("submit");
submitButton.addEventListener("click", () => {
  var selectedFormat = fileFormatSelect.value;
  var fileInput = document.getElementById("file-input-specific");

  // Check if files are selected
  if (fileInput.files.length > 0) {
    // Access the selected file
    var selectedFile = fileInput.files[0];

    if (selectedFile) {
      const filePath = window.electronAPI.pathForFile(selectedFile);

      console.log("File Name:", selectedFile.name);
      console.log("File Path:", filePath);
      console.log("File Size:", selectedFile.size, "bytes");
      console.log("File Type:", selectedFile.type);

      fileInputAlert.style.display = "none";

      window.electronAPI.runProgram(filePath, selectedFormat);
    }
  } else {
    // Displays error if no file selected
    fileInputAlert.style.display = "block";
  }
});
