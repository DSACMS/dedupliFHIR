const { ipcRenderer, contextBridge } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  runProgram: (filePath, fileFormat) =>
    ipcRenderer.invoke("runProgram", filePath, fileFormat),
  saveFile: () => ipcRenderer.invoke("dialog:saveFile"),
});
