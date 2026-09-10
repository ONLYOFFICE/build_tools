# Docker

This directory contains instructions for developers,
who want to change something in sdkjs, web-apps, or the server module,
but don't want to compile the complicated core product to make those changes.

## System requirements

### Windows

You need the latest
[Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
installed.

**Note**: Docker Desktop does not start automatically after installation.
You should manually start the **Docker Desktop** application.

**Note**: If you have problems running Docker Desktop with the
"Use WSL 2 instead of Hyper-V" installation option,
try reinstalling it without this option.

### Linux or macOS

You need the latest
[Docker](https://docs.docker.com/engine/install/)
version installed.

## Create Development Docker Image

To create an image with the ability to include external non-minified sdkjs code,
use the following commands:

### Clone development environment to the working directory

```bash
git clone https://github.com/ONLYOFFICE/build_tools.git
```

### Build Docker Image

**Note**: Do not prefix the docker command with sudo.
[These instructions](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
show how to use docker without sudo.

```bash
cd build_tools/develop
docker build --no-cache --build-arg DOCUMENTSERVER_IMAGE=onlyoffice/documentserver:latest --build-arg BUILDTOOLS_BRANCH=master -t documentserver-develop .
```

**Note**: The dot at the end is required.

**Note**: For a versioned development image, use the matching Document Server
image and build_tools branch, for example
`DOCUMENTSERVER_IMAGE=onlyoffice/documentserver:9.4.0` and
`BUILDTOOLS_BRANCH=release/v9.4.0`.

**Note**: On container startup, the build_tools branch is detected from the
copy used inside the container. The branch selects the matching core archive,
including FileConverter binaries.

**Note**: Sometimes the build may fail due to network errors. Just restart it.

## Clone development modules

Clone development modules to the working directory.

* `sdkjs` repo is located [here](https://github.com/ONLYOFFICE/sdkjs/)
* `web-apps` repo is located [here](https://github.com/ONLYOFFICE/web-apps/)
* `server` repo is located [here](https://github.com/ONLYOFFICE/server/)

```bash
git clone https://github.com/ONLYOFFICE/sdkjs.git
git clone https://github.com/ONLYOFFICE/web-apps.git
git clone https://github.com/ONLYOFFICE/server.git
```

## Start server with external folders

To mount external folders to the container,
you need to pass the "-v" parameter
along with the relative paths to the required folders.  
The folders `sdkjs` and `web-apps` are required for proper development workflow.
The folder `server` is optional.

**Note**: Run the command with the current working directory
containing `sdkjs`, `web-apps`...

**Note**: ONLYOFFICE server uses port 80.
Look for another application using port 80 and stop it.

**Note**: Starting the server with `sdkjs` and `web-apps` takes 15 minutes,
or 20 minutes with `server`.

### docker run on Windows (PowerShell)

**Note**: Run PowerShell as administrator to fix EACCES error when installing
node_modules.

Run with `sdkjs` and `web-apps`

```powershell
docker run -i -t -p 80:80 --restart=always -e ALLOW_PRIVATE_IP_ADDRESS=true -v $pwd/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $pwd/web-apps:/var/www/onlyoffice/documentserver/web-apps documentserver-develop
```

Or run with `sdkjs`, `web-apps`, and `server`

```powershell
docker run -i -t -p 80:80 --restart=always -e ALLOW_PRIVATE_IP_ADDRESS=true -v $pwd/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $pwd/web-apps:/var/www/onlyoffice/documentserver/web-apps -v $pwd/server:/var/www/onlyoffice/documentserver/server documentserver-develop
```

**Note**: If using Git Bash instead of PowerShell, you may need to quote the paths:

```bash
docker run -i -t -p 80:80 --restart=always -e ALLOW_PRIVATE_IP_ADDRESS=true -v "$(pwd)/sdkjs":/var/www/onlyoffice/documentserver/sdkjs -v "$(pwd)/web-apps":/var/www/onlyoffice/documentserver/web-apps documentserver-develop
```

### docker run on Linux or macOS

Run with `sdkjs` and `web-apps`

```bash
docker run -i -t -p 80:80 --restart=always -e ALLOW_PRIVATE_IP_ADDRESS=true -v $(pwd)/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $(pwd)/web-apps:/var/www/onlyoffice/documentserver/web-apps documentserver-develop
```

Or run with `sdkjs`, `web-apps`, and `server`

```bash
docker run -i -t -p 80:80 --restart=always -e ALLOW_PRIVATE_IP_ADDRESS=true -v $(pwd)/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $(pwd)/web-apps:/var/www/onlyoffice/documentserver/web-apps -v $(pwd)/server:/var/www/onlyoffice/documentserver/server documentserver-develop
```

## Open editor

After the server starts successfully, you will see Docker log messages like this.

```text
[Date] [WARN] [localhost] [docId] [userId] nodeJS
```

To try the document editor, open a browser tab and type
[http://localhost/example](http://localhost/example) into the URL bar.

**Note**: Disable **ad blockers** for the localhost page.
They may block some scripts (like Analytics.js).

## Modify sources

### To change something in `sdkjs`, do the following steps

**Step 1.** Edit the source file. Let's insert an image URL into each open document.
The following command inserts (in case of problems, you can replace the URL)
`this.AddImageUrl(['http://localhost/example/images/logo.png']);`  
after event  
`this.sendEvent('asc_onDocumentContentReady');`  
in file  
`sdkjs/common/apiBase.js`

**Windows (PowerShell):**

```powershell
(Get-Content sdkjs/common/apiBase.js) -replace "this\.sendEvent\('asc_onDocumentContentReady'\);", "this.sendEvent('asc_onDocumentContentReady');this.AddImageUrl(['http://localhost/example/images/logo.png']);" | Set-Content sdkjs/common/apiBase.js
```

**Linux:**

```bash
sed -i "s,this.sendEvent('asc_onDocumentContentReady');,this.sendEvent('asc_onDocumentContentReady');this.AddImageUrl(['http://localhost/example/images/logo.png']);," sdkjs/common/apiBase.js
```

**macOS:**

```bash
sed -i '' "s,this.sendEvent('asc_onDocumentContentReady');,this.sendEvent('asc_onDocumentContentReady');this.AddImageUrl(['http://localhost/example/images/logo.png']);," sdkjs/common/apiBase.js
```

**Step 2.** Clear the browser cache or hard reload the page
(`Ctrl + Shift + R` or `Cmd + Shift + R` on macOS)

**Step 3.** Open a new file in the browser

### To change something in `server`, do the following steps

**Step 1.** Edit the source file. Let's send a `"Hello World!"`
chat message every time a document is opened.
The following command inserts  
`yield* onMessage(ctx, conn, {"message": "Hello World!"});`  
in function  
`sendAuthInfo`  
in file  
`server/DocService/sources/DocsCoServer.js`

**Windows (PowerShell):**

```powershell
(Get-Content server/DocService/sources/DocsCoServer.js) -replace 'opt_hasForgotten, opt_openedAt\) \{', 'opt_hasForgotten, opt_openedAt) {yield* onMessage(ctx, conn, {"message": "Hello World!"});' | Set-Content server/DocService/sources/DocsCoServer.js
```

**Linux:**

```bash
sed -i 's#opt_hasForgotten, opt_openedAt) {#opt_hasForgotten, opt_openedAt) {yield* onMessage(ctx, conn, {"message": "Hello World!"});#' server/DocService/sources/DocsCoServer.js
```

**macOS:**

```bash
sed -i '' 's#opt_hasForgotten, opt_openedAt) {#opt_hasForgotten, opt_openedAt) {yield* onMessage(ctx, conn, {"message": "Hello World!"});#' server/DocService/sources/DocsCoServer.js
```

**Step 2.** Restart the document server process

**Note**: Look for `CONTAINER_ID` in the result of `docker ps`.

```bash
docker exec -it CONTAINER_ID supervisorctl restart all
```

**Step 3.** Open a new file in the browser

## Start server with additional functionality (addons)

To get additional functionality and branding, you need to connect a branding folder,
additional addon folders, and pass command line arguments.

For example, run with `onlyoffice` branding and
addons: `sdkjs-forms`, `sdkjs-ooxml`, `web-apps-mobile`.

### docker run on Windows (PowerShell) with branding

**Note**: Run PowerShell as administrator to fix EACCES error when installing
node_modules.

```powershell
docker run -i -t -p 80:80 --restart=always -e ALLOW_PRIVATE_IP_ADDRESS=true `
    -v $pwd/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $pwd/web-apps:/var/www/onlyoffice/documentserver/web-apps `
    -v $pwd/onlyoffice:/var/www/onlyoffice/documentserver/onlyoffice -v $pwd/sdkjs-ooxml:/var/www/onlyoffice/documentserver/sdkjs-ooxml -v $pwd/sdkjs-forms:/var/www/onlyoffice/documentserver/sdkjs-forms -v $pwd/web-apps-mobile:/var/www/onlyoffice/documentserver/web-apps-mobile `
    documentserver-develop args --branding onlyoffice --branding-url 'https://github.com/ONLYOFFICE/onlyoffice.git' --siteUrl localhost
```

### docker run on Linux or macOS with branding

```bash
docker run -i -t -p 80:80 --restart=always -e ALLOW_PRIVATE_IP_ADDRESS=true \
    -v $(pwd)/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $(pwd)/web-apps:/var/www/onlyoffice/documentserver/web-apps \
    -v $(pwd)/onlyoffice:/var/www/onlyoffice/documentserver/onlyoffice -v $(pwd)/sdkjs-ooxml:/var/www/onlyoffice/documentserver/sdkjs-ooxml -v $(pwd)/sdkjs-forms:/var/www/onlyoffice/documentserver/sdkjs-forms -v $(pwd)/web-apps-mobile:/var/www/onlyoffice/documentserver/web-apps-mobile \
    documentserver-develop args --branding onlyoffice --branding-url 'https://github.com/ONLYOFFICE/onlyoffice.git' --siteUrl localhost
```
