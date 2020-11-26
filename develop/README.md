# Docker

## Installing ONLYOFFICE Docs

## How to use - Linux

**Note**: You need the latest Docker version installed.

You might need to pull **onlyoffice/documentserver** image:

```bash
sudo docker pull onlyoffice/documentserver
```

### Create develop image
To create a image with the ability to include external non-minified sdkjs code, use the following command from the dockerfile directory:
```bash
sudo docker build -t your_imageName .
```
**Note**: The dot at the end is required.

### Connecting external folders
To connect external folders to the container, you need to pass the "-v" parameter along with the relative paths to the required folders.

**For example, let's connect the external folders "sdkjs" and "web-apps" to the container:** 

```bash
sudo docker run -i -t -d -p 80:80 --restart=always \
    -v /host-dir/sdkjs:/var/www/onlyoffice/documentserver/sdkjs  \
    -v /host-dir/web-apps:/var/www/onlyoffice/documentserver/web-apps imageName
```

