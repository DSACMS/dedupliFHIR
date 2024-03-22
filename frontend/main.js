const { app, BrowserWindow, dialog, ipcMain } = require("electron/main");
const path = require("node:path");
const fs = require("fs-extra");
const { PythonShell } = require("python-shell");
const constants = require("./constants/constants.js");
let mainWindow;

function runProgram(filePath) {
  mainWindow.loadFile("loading.html");

  const script = constants.SCRIPT;

  const poetryArgs = [
    constants.COMMANDS.DEDUPE_DATA,
    constants.OPTIONS.FORMAT,
    constants.FORMAT.TEST,
    filePath,
    "./",
  ];

  let options = {
    mode: "text",
    scriptPath: "../cli",
    pythonPath: "../.venv/bin/python",
    args: poetryArgs,
  };

  PythonShell.run(script, options)
    .then((messages) => {
      console.log("SUCCESS");
      console.log("results: %j", messages);
      mainWindow.loadFile("success.html");
    })
    .catch((err) => {
      console.log(err);
      mainWindow.loadFile("error.html");
    });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    webPreferences: {
      preload: path.join(__dirname, "./preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false,
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

ipcMain.on("download", (event, info) => {
  dialog
    .showSaveDialog({
      title: "Select Directory to Save Results",
      defaultPath: "deduped_record_mapping.xlsx",
      properties: ["openDirectory"],
    })
    .then((result) => {
      if (!result.canceled && result.filePath) {
        const sourceFile = "deduped_record_mapping.xlsx";
        const destinationFile = result.filePath; // Path to the new file

        console.log(destinationFile, "hi");

        fs.copy(sourceFile, destinationFile)
          .then(() => {
            console.log("File saved successfully.");
            mainWindow.webContents.send("dialog-response", destinationFile);
          })
          .catch((err) => {
            console.error("Error saving file:", err);
          });
      }
    })
    .catch((err) => {
      console.log(err);
    });
});
