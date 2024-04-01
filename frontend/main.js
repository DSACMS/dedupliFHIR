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
      console.log("results: %j", messages);
      mainWindow.loadFile("success.html");
    })
    .catch((error) => {
      console.log("Error running dedupe-data command: ", err);
      mainWindow.loadFile("error.html");
    });
}

async function handleSaveFile() {
  try {
    const result = await dialog.showSaveDialog({
      title: "Select Directory to Save Results",
      defaultPath: "deduped_record_mapping.xlsx",
      properties: ["openDirectory"],
    });

    if (result.canceled || !result.filePath) return null;

    const sourceFile = "deduped_record_mapping.xlsx";
    const destinationFile = result.filePath; // Selected path of new file location

    try {
      await fs.copy(sourceFile, destinationFile);
      return destinationFile;
    } catch (error) {
      console.error("Error copying file:", error);
      return null;
    }
  } catch (error) {
    console.error("Error showing save dialog:", error);
    return null;
  }
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

ipcMain.handle("dialog:saveFile", handleSaveFile);
