const fs = require("fs");
const path = require("path");
const { test, expect, _electron: electron } = require("@playwright/test");

let electronApp;
let window;

test.beforeAll(async () => {
  // Launch app
  electronApp = await electron.launch({ args: ["."] });

  // Wait for the first BrowserWindow to open and return its Page object
  window = await electronApp.firstWindow();

  // Take initial screenshot
  await window.screenshot({
    path: path.resolve(__dirname, "screenshots", "intro.png"),
  });
});

test.afterAll(async () => {
  await window.screenshot({
    path: path.resolve(__dirname, "screenshots", "final.png"),
  });
  await window.context().close();
  await window.close();
  await electronApp.close();
});

test("start app", async () => {
  const isPackaged = await electronApp.evaluate(async ({ app }) => {
    // This runs in Electron's main process, parameter here is always
    // the result of the require('electron') in the main app script.
    return app.isPackaged;
  });

  expect(isPackaged).toBe(false);

  // Evaluation expression in the Electron context.
  const appPath = await electronApp.evaluate(async ({ app }) => {
    // This runs in the main Electron process, parameter here is always
    // the result of the require('electron') in the main app script.
    return app.getAppPath();
  });
});

test("window title", async () => {
  // test number of windows
  const windows = electronApp.windows();
  expect(windows.length).toBe(1);

  // test window title
  expect(await window.title()).toBe("DedupliFHIR");
});

test("UI elements present", async () => {
  // Check for content
  const content = await window.locator("div.content");
  expect(content).not.toBeNull();
  expect(content.locator("h1")).toHaveText("DedupliFHIR");
  const instructionText = await window.locator("#file-input-copy");
  expect(instructionText).toHaveText("To start deduplication, load your file into DedupliFHIR.");

  // Check for file dropper
  const fileDropper = await window.locator("input[type='file']");
  expect(fileDropper).not.toBeNull();
  expect(fileDropper).toHaveId("file-input-specific");
  expect(fileDropper).toHaveAttribute("accept", ".json,.csv");

  // Check for dropdown
  const dropdown = await window.locator("select");
  expect(dropdown).not.toBeNull();
  expect(dropdown).toHaveId("options");
  expect(dropdown).toHaveClass("usa-select");

  // Check for submit button
  const submitButton = await window.locator("button[type='button']");
  expect(submitButton).not.toBeNull();
  expect(submitButton).toHaveId("submit");

  // Check for security section
  const securityText = await window.locator("#security-section");
  expect(securityText).not.toBeNull();
});

test("submit without loading file", async () => {
  const submitButton = await window.locator("button[type='button']");
  await submitButton.click();

  const alert = await window.locator("#file-input-alert");
  expect(alert).not.toBeNull();
  expect(alert.locator("p")).toHaveText(
    "File not found. Please load a file.",
  );
});

test("load file and submit", async () => {
  const fileDropper = await window.locator("input[type='file']");

  await fileDropper.setInputFiles(
    path.resolve(
      __dirname,
      "..",
      "..",
      "cli",
      "deduplifhirLib",
      "tests",
      "test_data.csv",
    ),
  );
  // OR, put a custom test file in frontend/tests/
  // await fileDropper.setInputFiles("tests/test_data.csv");

  const submitButton = await window.locator("button[type='button']");
  await submitButton.click();

  await window.waitForSelector("div.loader");
  const loader = await window.locator("div.loader");
  expect(loader).not.toBeNull();
});

test("finished results present", async () => {
  await window.waitForSelector("div.content");
  const content = await window.locator("div.content");
  expect(content).not.toBeNull();
  expect(content.locator("h1")).toHaveText("DedupliFHIR");

  // Wait for results
  await window.waitForSelector("p", {
    timeout: 1000 * 60 * 2, // two minutes
  });
  expect(content.locator("#results-ready-text")).toHaveText("Your results are ready.");
  expect(content.locator("a[href='../index.html']")).not.toBeNull();
  expect(content.locator("#save-file")).not.toBeNull();

  expect(content.locator("#save-file-success-alert")).toBeHidden();
  expect(content.locator("#results-spreadsheet-instructions")).toBeHidden();
  expect(content.locator("#save-file-fail-alert")).toBeHidden();
});

test("save file", async () => {
  const saveButton = await window.locator("#save-file");
  expect(saveButton).not.toBeNull();

  // https://stackoverflow.com/a/75966734
  const xlsxPath = path.join(
    __dirname,
    "downloads",
    "deduped_record_mapping.xlsx",
  );
  await electronApp.evaluate(async ({ dialog }, xlsxPath) => {
    dialog.showSaveDialog = () =>
      Promise.resolve({ filePath: xlsxPath, canceled: false });
  }, xlsxPath);
  await saveButton.click();

  await window.waitForSelector("#save-file-success-alert");
  const successAlert = await window.locator("#save-file-success-alert");
  expect(successAlert).not.toBeNull();
  expect(successAlert.locator("p")).toHaveText("Results file saved to your computer.");

  const instructions = await window.locator(
    "#results-spreadsheet-instructions",
  );
  expect(instructions).not.toBeNull();

  const homeLink = await window.locator("a[href='../index.html']");
  expect(homeLink).not.toBeNull();

  expect((await fs.promises.stat(xlsxPath)).size).toBeGreaterThan(100 * 1024); // file size should be > 100 KB
});

test("return home", async () => {
  const homeButton = await window.locator("a[href='../index.html']");
  expect(homeButton).not.toBeNull();
  await homeButton.click();

  await window.waitForSelector("div.content");

  // Check for content
  const content = await window.locator("div.content");
  expect(content).not.toBeNull();
  expect(content.locator("h1")).toHaveText("DedupliFHIR");
  const instructionText = await window.locator("#file-input-copy");
  expect(instructionText).toHaveText("To start deduplication, load your file into DedupliFHIR.");
});
