const { app, BrowserWindow, dialog, ipcMain } = require("electron/main");
const path = require("node:path");
const { PythonShell } = require("python-shell");
let mainWindow;

function runProgram(filePath) {
  mainWindow.loadFile("loading.html");

  const command = "ecqm_dedupe.py";

  const poetryArgs = ["dedupe-data", "--fmt", "TEST", filePath, "./"];

  let options = {
    mode: "text",
    scriptPath: "../cli",
    pythonPath: "../.venv/bin/python",
    args: poetryArgs,
  };

  console.log("ABOUT TO RUN PYTHON SHELL PROGRAM");
  PythonShell.run(command, options).then((messages) => {
    console.log("SUCCESS");
    console.log("results: %j", messages);
    mainWindow.loadFile("success.html");
  });

  console.log("DONE EXECUTING PYTHON PROGRAM");
}

function createWindow() {
  mainWindow = new BrowserWindow({
    webPreferences: {
      preload: path.join(__dirname, "./preload.js"),
      contextIsolation: true,
    },
  });

  mainWindow.loadFile("index.html");
}

app.whenReady().then(() => {
  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (mainWindow == null) {
    createWindow();
  }
});

ipcMain.handle("runProgram", async (event, data) => {
  return await runProgram(data);
});
