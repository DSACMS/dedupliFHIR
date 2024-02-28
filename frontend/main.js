const { app, BrowserWindow, dialog, ipcMain } = require("electron/main")
const path = require("node:path")

let mainWindow

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
