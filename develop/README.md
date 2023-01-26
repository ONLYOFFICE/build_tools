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

**Note**: server start with `sdkjs` and `web-apps` takes 20 minutes
and takes 30 minutes with `server`

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
    -v %cd%/server:/var/www/onlyoffice/documentserver/server-src ^
    documentserver-develop
```

### Linux or macOS

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
    -v $(pwd)/server:/var/www/onlyoffice/documentserver/server-src \
    documentserver-develop
```

### Open editor

After server succesfully starts you will see docker log messages like this  
_[Date] [WARN] [localhost] [docId] [userId] nodeJS
 - Express server listening on port 8000 in production-linux mode. Version: *.*.*. Build: *_
To try the document editor, open a tab and type
[http://localhost/example](http://localhost/example) into the URL bar.

### Modify sources


