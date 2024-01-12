const { ipcRenderer, contextBridge } = require("electron")

contextBridge.exposeInMainWorld("electronAPI", {
  openFile: () => ipcRenderer.invoke("dialog:openFile"),
})
