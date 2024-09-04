const { app, BrowserWindow, dialog, ipcMain } = require("electron/main");
const path = require("node:path");
const fs = require("fs-extra");
const { PythonShell } = require("python-shell");
const {
  SCRIPT,
  COMMANDS,
  OPTIONS,
  FORMAT,
  RESULTS_FILE_NAME,
} = require("./constants.js");
let mainWindow;
var resultsFile;

function findPython() {
  const possibilities = [
    // In packaged app
    path.join(process.resourcesPath, "python", "bin", "python3.11"),
    path.join(process.resourcesPath, "python", "bin", "python3.12"),
    // In development
    path.join("..", ".venv", "bin", "python"),
  ];
  for (const path of possibilities) {
    if (fs.existsSync(path)) {
      return path;
    }
  }
  console.log("Could not find python3, checked", possibilities);
  app.quit();
}

function identifyFormat(fileName) {
  const extension = path.extname(fileName).slice(1);

  switch (extension) {
    case "csv":
      return FORMAT.CSV;
    case "xml":
      return FORMAT.FHIR;
    default:
      return FORMAT.TEST;
  }
}

function runProgram(filePath, fileFormat) {
  mainWindow.loadFile("pages/loading.html");
  resultsFile = RESULTS_FILE_NAME + fileFormat;

  const fileName = path.basename(filePath);
  const currentDirectory = path.dirname(__filename);
  let scriptPath;
  let outputPath;

  if (app.isPackaged) {
    scriptPath = path.join(process.resourcesPath, "cli");
    outputPath = path.join(app.getPath("userData"), resultsFile);
  } else {
    scriptPath = path.join(currentDirectory, "..", "cli");
    outputPath = path.join(currentDirectory, resultsFile);
  }

  const script = SCRIPT;

  const poetryArgs = [
    COMMANDS.DEDUPE_DATA,
    OPTIONS.FORMAT,
    identifyFormat(fileName),
    filePath,
    outputPath,
  ];

  let options = {
    mode: "text",
    scriptPath: scriptPath,
    pythonPath: findPython(),
    args: poetryArgs,
  };

  PythonShell.run(script, options)
    .then((messages) => {
      console.log("results: %j", messages);
      mainWindow.loadFile("pages/success.html");
    })
    .catch((err) => {
      console.log("Error running dedupe-data command: ", err);
      mainWindow.loadFile("pages/error.html");
    });
}

async function handleSaveFile() {
  try {
    const result = await dialog.showSaveDialog({
      title: "Select Directory to Save Results",
      defaultPath: path.join(app.getPath("downloads"), resultsFile),
      properties: ["openDirectory"],
    });

    if (result.canceled || !result.filePath) return null;

    const sourceFile = app.isPackaged
      ? path.join(app.getPath("userData"), resultsFile)
      : resultsFile;

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
ipcMain.handle("runProgram", (event, filePath, fileFormat) => {
  return runProgram(filePath, fileFormat);
});

ipcMain.handle("dialog:saveFile", handleSaveFile);
