const fileInputAlert = document.getElementById("file-input-alert");
fileInputAlert.style.display = "none";

const submitButton = document.getElementById("submit");
submitButton.addEventListener("click", () => {
  var fileInput = document.getElementById("file-input-specific");

  // Check if files are selected
  if (fileInput.files.length > 0) {
    // Access the selected file
    var selectedFile = fileInput.files[0];

    if (selectedFile) {
      console.log("File Name:", selectedFile.name);
      console.log("File Path:", selectedFile.path);
      console.log("File Size:", selectedFile.size, "bytes");
      console.log("File Type:", selectedFile.type);

      fileInputAlert.style.display = "none";
    }
  } else {
    // Displays error if no file selected
    fileInputAlert.style.display = "block";
  }
});
