# Docker

This directory containing instruction for developers,
who want to change something in sdkjs or web-apps or server module,
but don't want to compile pretty compilcated core product to make those changes.

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

## Create develop Docker Images

To create a image with the ability to include external non-minified sdkjs code,
use the following commands:

### Clone development environment to work dir

```bash
git clone -b feature/docker-instruction https://github.com/ONLYOFFICE/build_tools.git
```

### Modify Docker Images

**Note**: Do not prefix docker command with sudo.
[This](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
instruction show how to use docker without sudo.

```bash
cd build_tools/develop
docker pull onlyoffice/documentserver
docker build -t documentserver-develop .
```

**Note**: The dot at the end is required.

## Clone development modules

Clone development modules to the work dir

* `sdkjs` repo is located [here](https://github.com/ONLYOFFICE/sdkjs/)
* `web-apps` repo is located [here](https://github.com/ONLYOFFICE/web-apps/)
* `server` repo is located [here](https://github.com/ONLYOFFICE/server/)

```bash
cd ../..
git clone https://github.com/ONLYOFFICE/sdkjs.git
git clone https://github.com/ONLYOFFICE/web-apps.git
git clone https://github.com/ONLYOFFICE/server.git
```

## Start server with external folders

To mount external folders to the container,
you need to pass the "-v" parameter
along with the relative paths to the required folders.  
The folders `sdkjs` and `web-apps` are required for proper development workflow.
The folders `server` is optional

**Note**: ONLYOFFICE server uses port 80.
Look for another application using port 80 and stop it

**Note**: Server start with `sdkjs` and `web-apps` takes 15 minutes
and takes 20 minutes with `server`

**Note**: Run command from work dir with development modules

**Windows (PowerShell)**

**Note**: Run PowerShell as administrator to fix EACCES error when installing
node_modules

run with `sdkjs` and `web-apps`

```bash
docker run -i -t -p 80:80 --restart=always -v $pwd/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $pwd/web-apps:/var/www/onlyoffice/documentserver/web-apps documentserver-develop
```

or run with `sdkjs`, `web-apps` and `server`

```bash
docker run -i -t -p 80:80 --restart=always -v $pwd/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $pwd/web-apps:/var/www/onlyoffice/documentserver/web-apps -v $pwd/server:/var/www/onlyoffice/documentserver/server documentserver-develop
```

**Linux or macOS**

run with `sdkjs` and `web-apps`

```bash
docker run -i -t -p 80:80 --restart=always -v $(pwd)/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $(pwd)/web-apps:/var/www/onlyoffice/documentserver/web-apps documentserver-develop
```

or run with `sdkjs`, `web-apps` and `server`

```bash
docker run -i -t -p 80:80 --restart=always -v $(pwd)/sdkjs:/var/www/onlyoffice/documentserver/sdkjs -v $(pwd)/web-apps:/var/www/onlyoffice/documentserver/web-apps -v $(pwd)/server:/var/www/onlyoffice/documentserver/server documentserver-develop
```

## Open editor

After the server starts successfully, you will see Docker log messages like this

```bash
[Date] [WARN] [localhost] [docId] [userId] nodeJS
```

To try the document editor, open a browser tab and type
[http://localhost/example](http://localhost/example) into the URL bar.

**Note**: Disable **ad blockers** for localhost page.
It may block some scripts (like Analytics.js)

## Modify sources

### To change something in `sdkjs` do the following steps

1)Edit source file. Let's insert an image url into each open document.
Do the following command.

**Windows (PowerShell)**

```bash
(Get-Content sdkjs/common/apiBase.js) -replace "this\.sendEvent\('asc_onDocumentContentReady'\);", "this.sendEvent('asc_onDocumentContentReady');this.AddImageUrl(['http://localhost/example/images/logo.png']);"  | Set-Content sdkjs/common/apiBase.js
```

**Linux or macOS**

```bash
sed -i "s,this.sendEvent('asc_onDocumentContentReady');,this.sendEvent('asc_onDocumentContentReady');this.AddImageUrl(['http://localhost/example/images/logo.png']);," sdkjs/common/apiBase.js
```

2)Delete browser cache or hard reload the page `Ctrl + Shift + R`

3)Open new file in browser

### To change something in `server` do the following steps

1)Edit source file. Let's send `"Hello World!"`
chart message every time a document is opened.Do the following command

**Windows (PowerShell)**

```bash
(Get-Content server/DocService/sources/DocsCoServer.js) -replace 'opt_hasForgotten, opt_openedAt\) \{', 'opt_hasForgotten, opt_openedAt) {yield* onMessage(ctx, conn, {"message": "Hello World!"});' | Set-Content server/DocService/sources/DocsCoServer.js
```

**Linux or macOS**

```bash
sed -i 's#opt_hasForgotten, opt_openedAt) {#opt_hasForgotten, opt_openedAt) {yield* onMessage(ctx, conn, {"message": "Hello World!"});#' server/DocService/sources/DocsCoServer.js
```

2)Restart document server process

**Note**: Look for ``CONTAINER_ID`` in the result of ``docker ps``.

```bash
docker exec -it CONTAINER_ID supervisorctl restart all
```

3)Open new file in browser
