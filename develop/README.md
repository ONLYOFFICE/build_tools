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

### Storing data outside containers

All the data are stored in the specially-designated directories, data volumes, at the following location:

1. /var/log/onlyoffice for ONLYOFFICE Docs logs
2. /var/www/onlyoffice/Data for certificates
3. /var/lib/onlyoffice for file cache
4. /var/lib/postgresql for database

**Note**: We strongly recommend that you store the data outside the Docker containers on the host machine as it allows you to easily update ONLYOFFICE Docs once the new version is released without losing your data.

To get access to your data located outside the container, you need to mount the volumes. It can be done by specifying the -v option in the docker run command.

```bash
sudo docker run -i -t -d -p 80:80 --restart=always \
    -v /app/onlyoffice/DocumentServer/logs:/var/log/onlyoffice  \
    -v /app/onlyoffice/DocumentServer/data:/var/www/onlyoffice/Data  \
    -v /app/onlyoffice/DocumentServer/lib:/var/lib/onlyoffice \
    -v /app/onlyoffice/DocumentServer/db:/var/lib/postgresql  onlyoffice/documentserver
```

**Note**:Please note, that in case you are trying to mount the folders which are not yet created, these folders will be created but the access to them will be limited. You will need to change their access rights manually.

Normally, you do not need to store container data because the container operation does not depend on its state. Saving data will be useful:

1. For easy access to container data, such as logs;
2. To remove the limit on the size of the data inside the container;
3. When using services launched outside the container such as PostgreSQL, Redis, RabbitMQ.

### Mount sdkjs and web-apps
To get access to your non-minufied sdkjs code outside the container, you need to mount the volumes. It can be done by specifying the -v option in the docker run command.

**Note**: By default, the image uses minified sdkjs code. If you need to use non-minified code, then you should create a custom image using a dockerfile from the directory. Instructions can be found at the beginning of the Readme.

```bash
sudo docker run -i -t -d -p 80:80 --restart=always \
    -v /host-dir/sdkjs:/var/www/onlyoffice/documentserver/sdkjs  \
    -v /host-dir/web-apps:/var/www/onlyoffice/documentserver/web-apps imageName
```

