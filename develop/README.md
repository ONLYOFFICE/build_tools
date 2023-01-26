# Docker

This directory containing instruction for developers,
who want to change something in sdkjs or web-apps or server module,
but don't want to compile pretty compilcated core product to make those changes.

## Installing ONLYOFFICE Docs

## How to use

### Windows

**Note**: You need the latest
[Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
installed.

```bash
docker pull onlyoffice/documentserver
```

### Linux or macOS

**Note**: You need the latest Docker version installed.

You might need to pull **onlyoffice/documentserver** image:

**Note**: Do not prefix docker command with sudo.
[This](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
instruction show how to use docker without sudo.

```bash
docker pull onlyoffice/documentserver
```

## Create develop image

To create a image with the ability to include external non-minified sdkjs code,
use the following command:

```bash
git clone -b feature/docker-instruction https://github.com/ONLYOFFICE/build_tools.git
cd build_tools/develop
sed -i 's,https://github.com,-b feature/docker-instruction https://github.com,' Dockerfile
docker build -t documentserver-develop .
```

**Note**: The dot at the end is required.

## Connecting external folders

### Clone module

At first clone modules to the working dir

* `sdkjs` repo is located [here](https://github.com/ONLYOFFICE/sdkjs/)
* `web-apps` repo is located [here](https://github.com/ONLYOFFICE/web-apps/)
* `server` repo is located [here](https://github.com/ONLYOFFICE/server/)

```bash
cd ../..
git clone https://github.com/ONLYOFFICE/sdkjs.git
git clone https://github.com/ONLYOFFICE/web-apps.git
git clone https://github.com/ONLYOFFICE/server.git
```

### Start server with external folders

To mount external folders to the container,
you need to pass the "-v" parameter
along with the relative paths to the required folders.  
The folders `sdkjs` and `web-apps` are required for proper development workflow.
The folders `server` is optional

**Note**: server start with `sdkjs` and `web-apps` takes 10 minutes
and takes 15 minutes with `server`

### Windows (cmd)

run with `sdkjs` and `web-apps`

```bash
docker run -i -t -p 80:80 --restart=always ^
    -v %cd%/sdkjs:/var/www/onlyoffice/documentserver/sdkjs ^
    -v %cd%/web-apps:/var/www/onlyoffice/documentserver/web-apps ^
    documentserver-develop
```

run with `sdkjs`, `web-apps` and `server`

```bash
docker run -i -t -p 80:80 --restart=always ^
    -v %cd%/sdkjs:/var/www/onlyoffice/documentserver/sdkjs ^
    -v %cd%/web-apps:/var/www/onlyoffice/documentserver/web-apps ^
    -v %cd%/server:/var/www/onlyoffice/documentserver/server ^
    documentserver-develop
```

### Linux or macOS (bash)

run with `sdkjs` and `web-apps`

```bash
docker run -i -t -p 80:80 --restart=always \
    -v $(pwd)/sdkjs:/var/www/onlyoffice/documentserver/sdkjs \
    -v $(pwd)/web-apps:/var/www/onlyoffice/documentserver/web-apps \
    documentserver-develop
```

run with `sdkjs`, `web-apps` and `server`

```bash
docker run -i -t -p 80:80 --restart=always \
    -v $(pwd)/sdkjs:/var/www/onlyoffice/documentserver/sdkjs \
    -v $(pwd)/web-apps:/var/www/onlyoffice/documentserver/web-apps \
    -v $(pwd)/server:/var/www/onlyoffice/documentserver/server \
    documentserver-develop
```

### Open editor

After the server starts successfully, you will see Docker log messages like this
*[Date] [WARN] [localhost] [docId] [userId] nodeJS*  
To try the document editor, open a browser tab and type
[http://localhost/example](http://localhost/example) into the URL bar.

### Modify sources

To change something in `sdkjs` do the following steps
1. Edit source file. Let's insert an image url into each open document.
Do the following command.

Windows(cmd)

```
sed -i "s,this.sendEvent('asc_onDocumentContentReady');,^
this.sendEvent('asc_onDocumentContentReady');\n^
this.AddImageUrl(['http://localhost/example/images/logo.png']);," ^
sdkjs\common\apiBase.js
```

Linux or macOS (bash)

```
sed -i "s,this.sendEvent('asc_onDocumentContentReady');,\
this.sendEvent('asc_onDocumentContentReady');\n\
this.AddImageUrl(['http://localhost/example/images/logo.png']);," \
sdkjs\common\apiBase.js
```

2. Delete browser cache or hard reload the page `Ctrl + Shift + R`
3. Open new file in browser

To change something in `server` do the following steps
1. Edit source file. Let's send `"Hello World!"`
chart message every time a document is opened.Do the following command

Windows(cmd)

```
sed -i 's#opt_hasForgotten, opt_openedAt) {#^
opt_hasForgotten, opt_openedAt) {^
\nyield* onMessage(ctx, conn, {"message": "Hello World!"});#' ^
server\DocService\sources\DocsCoServer.js
```

Linux or macOS (bash)

```
sed -i 's#opt_hasForgotten, opt_openedAt) {#\
opt_hasForgotten, opt_openedAt) {\
\nyield* onMessage(ctx, conn, {"message": "Hello World!"});#' \
server\DocService\sources\DocsCoServer.js
```

2. Restart document server process

```bash
docker exec -it CONTAINER_ID supervisorctl restart all
``` 

3. Open new file in browser
