# build_tools

## Overview

**build_tools** allow you to automatically get and install all the components
necessary for the compilation process, all the dependencies required for the
**ONLYOFFICE Document Server**, **Document Builder** and **Desktop Editors**
 correct work, as well as to get the latest version of
**ONLYOFFICE products** source code and build all their components.

**Important!**  We can only guarantee the correct work of the products built from
the `master` branch.

## How to use - Linux

**Note**: The solution has been tested on **Ubuntu 16.04**.

### Installing dependencies

You might need to install **Python**, depending on your version of Ubuntu:

```bash
sudo apt-get install -y python
```

### Building ONLYOFFICE products source code

1. Clone the build_tools repository:

    ```bash
    git clone https://github.com/ONLYOFFICE/build_tools.git
    ```

2. Go to the `build_tools/tools/linux` directory:

    ```bash
    cd build_tools/tools/linux
    ```

3. Run the `automate.py` script:

    ```bash
    ./automate.py
    ```

If you run the script without any parameters this allows to build **ONLYOFFICE
Document Server**, **Document Builder** and **Desktop Editors**.

The result will be available in the `./out` directory.

To build **ONLYOFFICE** products separately run the script with the parameter
corresponding to the necessary product.

It’s also possible to build several products at once as shown in the example
below.

**Example**: Building **Desktop Editors** and **Document Server**

```bash
./automate.py desktop server
```

### Using Docker

You can also build all **ONLYOFFICE products** at once using Docker.
Build the `onlyoffice-document-editors-builder` Docker image using the
provided `Dockerfile` and run the corresponding Docker container.

```bash
mkdir out
docker build --tag onlyoffice-document-editors-builder .
docker run -v $PWD/out:/build_tools/out onlyoffice-document-editors-builder
```

The result will be available in the `./out` directory.

### Building and running ONLYOFFICE products separately

#### Document Builder

##### Building Document Builder

```bash
./automate.py builder
```

##### Running Document Builder

```bash
cd ../../out/linux_64/onlyoffice/documentbuilder
./docbuilder
```

#### Desktop Editors

##### Building Desktop Editors

```bash
./automate.py desktop
```

##### Running Desktop Editors

```bash
cd ../../out/linux_64/onlyoffice/desktopeditors
LD_LIBRARY_PATH=./ ./DesktopEditors
```

#### Document Server

##### Building Document Server

```bash
./automate.py server
```

##### Installing and configuring Document Server dependencies

**Document Server** uses **NGINX** as a web server and **PostgreSQL** as a database.
**RabbitMQ** is also required for **Document Server** to work correctly.

###### Installing and configuring NGINX

1. Install NGINX:

    ```bash
    sudo apt-get install nginx
    ```

2. Disable the default website:

    ```bash
    sudo rm -f /etc/nginx/sites-enabled/default
    ```

3. Set up the new website. To do that create the `/etc/nginx/sites-available/onlyoffice-documentserver`
   file with the following contents:

    ```bash
    map $http_host $this_host {
      "" $host;
      default $http_host;
    }
    map $http_x_forwarded_proto $the_scheme {
      default $http_x_forwarded_proto;
      "" $scheme;
    }
    map $http_x_forwarded_host $the_host {
      default $http_x_forwarded_host;
      "" $this_host;
    }
    map $http_upgrade $proxy_connection {
      default upgrade;
      "" close;
    }
    proxy_set_header Host $http_host;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $proxy_connection;
    proxy_set_header X-Forwarded-Host $the_host;
    proxy_set_header X-Forwarded-Proto $the_scheme;
    server {
      listen 0.0.0.0:80;
      listen [::]:80 default_server;
      server_tokens off;
      rewrite ^\/OfficeWeb(\/apps\/.*)$ /web-apps$1 redirect;
      location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
      }
    }
    ```

4. Add the symlink to the newly created website to the
   `/etc/nginx/sites-available` directory:

    ```bash
    sudo ln -s /etc/nginx/sites-available/onlyoffice-documentserver /etc/nginx/sites-enabled/onlyoffice-documentserver
    ```

5. Restart NGINX to apply the changes:

    ```bash
    sudo nginx -s reload
    ```

###### Installing and configuring PostgreSQL

1. Install PostgreSQL:

    ```bash
    sudo apt-get install postgresql
    ```

2. Create the PostgreSQL database and user:

    **Note**: The created database must have **onlyoffice** both for user and password.

    ```bash
    sudo -i -u postgres psql -c "CREATE DATABASE onlyoffice;"
    sudo -i -u postgres psql -c "CREATE USER onlyoffice WITH password 'onlyoffice';"
    sudo -i -u postgres psql -c "GRANT ALL privileges ON DATABASE onlyoffice TO onlyoffice;"
    ```

3. Configure the database:

    ```bash
    psql -hlocalhost -Uonlyoffice -d onlyoffice -f ../../out/linux_64/onlyoffice/documentserver/server/schema/postgresql/createdb.sql
    ```

**Note**: Upon that, you will be asked to provide a password for the **onlyoffice**
PostgreSQL user. Please enter the **onlyoffice** password.

###### Installing RabbitMQ

```bash
sudo apt-get install rabbitmq-server
```

###### Generate fonts data

```bash
cd out/linux_64/onlyoffice/documentserver/
mkdir fonts
LD_LIBRARY_PATH=${PWD}/server/FileConverter/bin server/tools/allfontsgen \
  --input="${PWD}/core-fonts" \
  --allfonts-web="${PWD}/sdkjs/common/AllFonts.js" \
  --allfonts="${PWD}/server/FileConverter/bin/AllFonts.js" \
  --images="${PWD}/sdkjs/common/Images" \
  --selection="${PWD}/server/FileConverter/bin/font_selection.bin" \
  --output-web='fonts' \
  --use-system="true"
```

###### Generate presentation themes

```bash
cd out/linux_64/onlyoffice/documentserver/
LD_LIBRARY_PATH=${PWD}/server/FileConverter/bin server/tools/allthemesgen \
  --converter-dir="${PWD}/server/FileConverter/bin"\
  --src="${PWD}/sdkjs/slide/themes"\
  --output="${PWD}/sdkjs/common/Images"
```

##### Running Document Server

**Note**: All **Document Server** components run as foreground processes. Thus
you need separate terminal consoles to run them or specific tools which will
allow to run foreground processes in background mode.

1. Start the **FileConverter** service:

    ```bash
    cd out/linux_64/onlyoffice/documentserver/server/FileConverter
    LD_LIBRARY_PATH=$PWD/bin \
    NODE_ENV=development-linux \
    NODE_CONFIG_DIR=$PWD/../Common/config \
    ./converter
    ```

2. Start the **DocService** service:

    ```bash
    cd out/linux_64/onlyoffice/documentserver/server/DocService
    NODE_ENV=development-linux \
    NODE_CONFIG_DIR=$PWD/../Common/config \
    ./docservice
    ```
