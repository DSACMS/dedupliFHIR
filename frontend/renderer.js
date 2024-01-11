async function onOpenFileClick() {
  const filePath = await window.electronAPI.openFile()
  document.getElementById("file_path").innerHTML = "File Path: " + filePath
}

const setButton = document.getElementById("btn")
setButton.addEventListener("click", () => {
  const filePath = onOpenFileClick()
})

const submitButton = document.getElementById("submit")
submitButton.addEventListener("click", () => {
  console.log("submit has been pressed")
  // const filePath = runProgram()
})
