const resultsText = document.getElementById("results-ready-text");
const successAlert = document.getElementById("save-file-success-alert");
const failAlert = document.getElementById("save-file-fail-alert");
const instructions = document.getElementById(
  "results-spreadsheet-instructions",
);
const homeButton = document.getElementById("return-to-home");

const saveButton = document.getElementById("save-file");
saveButton.addEventListener("click", async () => {
  const filePath = await window.electronAPI.saveFile();
  if (filePath) {
    resultsText.style.display = "none";
    successAlert.style.display = "block";
    instructions.style.display = "block";
    failAlert.style.display = "none";
    saveButton.style.display = "none";
    homeButton.innerText = "Load another file into DedupliFHIR";
  } else {
    resultsText.style.display = "none";
    successAlert.style.display = "none";
    instructions.style.display = "none";
    failAlert.style.display = "block";
  }
});
