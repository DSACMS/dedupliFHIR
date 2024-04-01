const successAlert = document.getElementById("download-success-alert");
const failAlert = document.getElementById("download-fail-alert");

const downloadButton = document.getElementById("download");
downloadButton.addEventListener("click", async () => {
  const filePath = await window.electronAPI.saveFile();
  if (filePath) {
    successAlert.style.display = "block";
    failAlert.style.display = "none";
  } else {
    successAlert.style.display = "none";
    failAlert.style.display = "block";
  }
});
