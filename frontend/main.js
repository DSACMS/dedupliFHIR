const { app, BrowserWindow, dialog, ipcMain } = require("electron/main")
const path = require("node:path")

let mainWindow

async function handleFileOpen() {
  const { canceled, filePaths } = await dialog.showOpenDialog({})
  if (!canceled) {
    return filePaths[0]
  }
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
