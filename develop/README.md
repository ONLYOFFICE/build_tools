# Docker

This directory containing instruction for developers,
who want to change something in sdkjs or web-apps module,
but don't want to compile pretty compilcated core product to make those changes.

## Installing ONLYOFFICE Docs

## How to use - Linux

**Note**: You need the latest Docker version installed.

You might need to pull **onlyoffice/documentserver** image:

**Note**: Do not prefix docker command with sudo.
[This](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
instruction show how to use docker without sudo.

```bash
docker pull onlyoffice/documentserver
```

### Create develop image

To create a image with the ability to include external non-minified sdkjs code,
use the following command from the dockerfile directory:

```bash
docker build -t documentserver-develop .
```

**Note**: The dot at the end is required.

### Connecting external folders

To connect external folders to the container,
you need to pass the "-v" parameter
along with the relative paths to the required folders.

**For example, let's connect the external folders "sdkjs" and "web-apps" to the container:**

```bash
docker run -i -t -d -p 80:80 --restart=always \
    -v /host-dir/sdkjs:/var/www/onlyoffice/documentserver/sdkjs \
    -v /host-dir/web-apps:/var/www/onlyoffice/documentserver/web-apps documentserver-develop
```
