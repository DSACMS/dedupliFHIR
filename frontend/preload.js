const { ipcRenderer, contextBridge } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  runProgram: () => ipcRenderer.invoke("dialog:runProgram"),
});
