const { test, expect, _electron: electron } = require("@playwright/test");

test("start app", async () => {
	const electronApp = await electron.launch({ args: ["."] });
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
	console.log(appPath);

	// close app
	await electronApp.close();
});

test("window title", async () => {
	const electronApp = await electron.launch({ args: ["."] });

	// Wait for the first BrowserWindow to open
	// and return its Page object
	const window = await electronApp.firstWindow();
	expect(await window.title()).toBe("DedupliFHIR");
	await window.screenshot({ path: "tests/screenshots/intro.png" });

	// test number of windows
	const windows = electronApp.windows();
	expect(windows.length).toBe(1);

	// close app
	await electronApp.close();
});
