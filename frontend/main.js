const { app, BrowserWindow, dialog, ipcMain } = require("electron/main")
const path = require("node:path")

let mainWindow

async function handleFileOpen() {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    title: "Select file to be uploaded",
    properties: ["openFile"],
    filters: [{ name: "FHIR & QRDA files", extensions: ["json"] }],
  })
  if (!canceled && filePaths.length > 0) {
    return filePaths[0]
  }
  // TODO: Consider displaying data on UI before submission
}

function createWindow() {
  mainWindow = new BrowserWindow({
    webPreferences: {
      preload: path.join(__dirname, "./preload.js"),
      contextIsolation: true,
    },
  })

  mainWindow.loadFile("index.html")
}

app.whenReady().then(() => {
  ipcMain.handle("dialog:openFile", handleFileOpen)
  createWindow()
})

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit()
  }
})

app.on("activate", () => {
  if (mainWindow == null) {
    createWindow()
  }
})
