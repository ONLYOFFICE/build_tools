const puppeteer = require('puppeteer')
const pathfs = require('path')
const fs = require('fs');

function TesterImpl()
{
  this.browser = null;
  this.page = null;
  this.width = 1500;
  this.height = 800;
  this.pixelRatio = 1;

  this.cacheDir = pathfs.resolve("./work_directory/cache");
  this.downloadsDir = pathfs.resolve("./work_directory/downloads");
  this.downloadCounter = 0;

  this.load = async function(url)
  {
    const head = { x: 100, y: 200 };
    this.browser = await puppeteer.launch({
      headless: false,
      product: process.env["PUPPETEER_PRODUCT"],
      args: [
        "--disable-infobars", 
        `--window-size=${this.width+head.x},${this.height+head.y}`, 
        "--disk-cache-dir=" + this.cacheDir
      ],
      defaultViewport : {width: this.width, height: this.height, deviceScaleFactor : this.pixelRatio }
    });

    this.page = await this.browser.newPage();
    await this.page.setViewport({ width: this.width, height: this.height });
    let waitObject = (process.env["PUPPETEER_PRODUCT"] === "firefox") ? { waitUntil: "networkidle0", timeout: 15000 } : {};
    await this.page.goto(url + "&autotest=enabled", waitObject);
    console.log("[tester] pageLoaded");
    return this.page;
  };

  this.close = async function(nosleep)
  {
    if (true !== nosleep)
      await this.waitAutosave();
    await this.browser.close();
  };

  this.sleep = async function(ms) 
  {
    return await new Promise(resolve => setTimeout(resolve, ms));
  };

  this.waitEditor = async function() 
  {
    // TODO: wait first onEndRecalculate
    await this.sleep(5000);
    console.log("[tester] editorReady");
  };

  this.waitAutosave = async function() 
  {
    await this.sleep(5000);    
  };

  this.evaluateInMainFrame = async function(code)
  {
    return await this.page.evaluate(code);
  };
  this.evaluateInEditorFrame = async function(code)
  {
    const frame = await this.page.frames().find(frame => frame.name() === 'frameEditor');
    if (!frame)
      return;
    return await frame.evaluate(code);
  };

  this.click = async function(id)
  {
    let res = await this.evaluateInEditorFrame("document.getElementById(\"" + id + "\").click(); \"[tester] clicked: " + id + "\"");
    //console.log(res);
    await this.sleep(200);
    return res;
  };

  this.mouseClick = async function(x, y, options)
  {
    let res = await this.page.mouse.click(x, y, options);
    await this.sleep(200);
    return res;
  };

  this.eval = async function(code)
  {
    let res = await this.evaluateInEditorFrame(code);
    await this.sleep(200);
    return res;
  };

  this.keyDown = async function(key)
  {
    // https://pptr.dev/api/puppeteer.keyinput
    let res = await this.page.keyboard.down(key);
    await this.sleep(200);
    return res;
  };

  this.keyUp = async function(key)
  {
    // https://pptr.dev/api/puppeteer.keyinput
    let res = await this.page.keyboard.up(key);
    await this.sleep(200);
    return res;
  };

  this.keyClick = async function(key)
  {
    // https://pptr.dev/api/puppeteer.keyinput
    let res = await this.page.keyboard.down(key);
    res = await this.page.keyboard.up(key);
    await this.sleep(200);
    return res;
  };

  this.keyPress = async function(key)
  {
    // https://pptr.dev/api/puppeteer.keyinput
    let res = await this.page.keyboard.press(key);
    await this.sleep(200);
    return res;
  };

  this.input = async function(text)
  {
    let res = await this.page.keyboard.type(text);
    await this.sleep(200);
    return res;
  };

  this.downloadFile = async function(format, path)
  {
    const tmpDir = pathfs.resolve(this.downloadsDir, "./tmp" + this.downloadCounter++);
    fs.mkdirSync(tmpDir);

    // emulate download
    const client = await this.page.target().createCDPSession();
    await client.send("Page.setDownloadBehavior", {
      behavior: "allow",
      downloadPath: tmpDir
    });

    await this.evaluateInEditorFrame("document.querySelectorAll('[data-layout-name=\"toolbar-file\"]')[0].click();");
    await this.sleep(200);
    await this.evaluateInEditorFrame("document.getElementsByClassName(\"svg-format-" + format + "\")[0].click();");
    await this.sleep(200);
    await this.evaluateInEditorFrame("document.getElementById(\"fm-btn-return\").click();");

    await this.sleep(2000);

    const files = fs.readdirSync(tmpDir);
    fs.copyFileSync(pathfs.resolve(tmpDir, "./" + files[0]), pathfs.resolve(path));
    fs.rmSync(tmpDir, { recursive: true, force: true });
  };
}

const Tester = new TesterImpl;

try {
  (async () => {    
    "%%CODE%%"
  })();
} catch (err) {
  console.error(err);
}
