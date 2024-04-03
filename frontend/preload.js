const { ipcRenderer, contextBridge } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  runProgram: (filePath) => ipcRenderer.invoke("runProgram", filePath),
  saveFile: () => ipcRenderer.invoke("dialog:saveFile"),
});
