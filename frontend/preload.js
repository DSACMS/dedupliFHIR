const { ipcRenderer, contextBridge } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  runProgram: (filePath) => ipcRenderer.invoke("runProgram", filePath),
  downloadFile: (url) => ipcRenderer.send("download"),
  onDialogResponse: (callback) => {
    ipcRenderer.invoke("dialog-response", (event, data) => {
      callback(data);
    });
  },
});
