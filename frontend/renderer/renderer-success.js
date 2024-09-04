const successAlert = document.getElementById("download-success-alert");
const instructions = document.getElementById(
  "results-spreadsheet-instructions",
);
const failAlert = document.getElementById("download-fail-alert");

const downloadButton = document.getElementById("download");
downloadButton.addEventListener("click", async () => {
  const filePath = await window.electronAPI.saveFile();
  if (filePath) {
    successAlert.style.display = "block";
    instructions.style.display = "block";
    failAlert.style.display = "none";
  } else {
    successAlert.style.display = "none";
    instructions.style.display = "none";
    failAlert.style.display = "block";
  }
});
