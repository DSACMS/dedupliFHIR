async function onOpenFileClick() {
  const filePath = await window.electronAPI.openFile()
  console.log(filePath, "filePath!")
  return filePath
}

const setButton = document.getElementById("btn")
setButton.addEventListener("click", () => {
  console.log("is this being clicked?")
  const filePath = onOpenFileClick()
})
