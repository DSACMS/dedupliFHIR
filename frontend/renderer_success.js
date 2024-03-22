const downloadButton = document.getElementById("download");
downloadButton.addEventListener("click", () => {
  window.electronAPI.downloadFile("deduped_record_mapping.xlsx");
});

// Listen for response from main process
onDialogResponse((data) => {
  // Handle response data
  console.log("Received data from main process:", data);
});
