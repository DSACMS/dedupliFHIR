const { ipcRenderer, contextBridge, webUtils } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  pathForFile: (file) => webUtils.getPathForFile(file),
  runProgram: (filePath, fileFormat) =>
    ipcRenderer.invoke("runProgram", filePath, fileFormat),
  saveFile: () => ipcRenderer.invoke("dialog:saveFile"),
});
