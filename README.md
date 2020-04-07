build_tools
===========

Overview
--------

**build_tools** allow you to automatically get and install all the components
necessary for the compilation process, all the dependencies required for the
**ONLYOFFICE Document Server**, **Document Builder** and **Desktop Editors** correct work, as well as to get the latest version of
**ONLYOFFICE products** source code and build all their components.

How to use
----------

### Linux

**Note**: The solution has been tested on **Ubuntu 14.04**.

#### Installing dependencies

You might need to install **Python**, depending on your version of Ubuntu:

```
sudo apt-get install -y python
```

#### Building ONLYOFFICE products source code

1.  Clone the build_tools repository:

```
git clone https://github.com/ONLYOFFICE/build_tools.git
```

2.  Go to the `build_tools/tools/linux` directory:

```
cd build_tools/tools/linux
```

3.  Run the `automate.py` script:

```
./automate.py
```

If you run the script without any parameters this allows to build **ONLYOFFICE
Document Server**, **Document Builder** and **Desktop Editors**.

To build **ONLYOFFICE** products separately run the script with the parameter
corresponding to the necessary product.

##### Building Document Server

```
./automate.py server
```

##### Building Document Builder

```
./automate.py builder
```

##### Building Desktop Editors

```
./automate.py desktop
```

It’s also possible to build several products at once as shown in the example
below.

##### Building Desktop Editors and Document Server

```
./automate.py desktop server
```

The result will be available in the `./out` directory.

### Using Docker

You can also build all **ONLYOFFICE products** at once using Docker. 
Build the `onlyoffice-document-editors-builder` Docker image using the provided `Dockerfile` and run the corresponding Docker container.

```bash
mkdir out
docker build --tag onlyoffice-document-editors-builder .
docker run -v $PWD/out:/build_tools/out onlyoffice-document-editors-builder
```

The result will be available in the `./out` directory.

#### Installing and configuring NGINX and PostgreSQL for Document Server on Linux

**Document Server** uses **NGINX** as a web server and **PostgreSQL** as a database.

##### Installing and configuring NGINX

1. Install NGINX:

```
sudo apt-get install nginx
```
2. Disable the default website:

```
sudo rm -f /etc/nginx/sites-enabled/default
```
3. Set up the new website. To do that create the `/etc/nginx/sites-available/onlyoffice-documentserver` file with the following contents:

```
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
  location /spellchecker/ {
    proxy_pass http://localhost:8080/;
    proxy_http_version 1.1;
  }
}
```
4. Add the symlink to the newly created website to the `/etc/nginx/sites-available` directory:

```
sudo ln -s /etc/nginx/sites-available/onlyoffice-documentserver /etc/nginx/sites-enabled/onlyoffice-documentserver
```
5. Restart NGINX to apply the changes:

```
sudo nginx -s reload
```

##### Installing and configuring PostgreSQL

1. Install PostgreSQL:

```
sudo apt-get install postgresql
```
2. Create the PostgreSQL database and user:

**Note**: The created database must have **onlyoffice** both for user and password.

```
sudo -i -u postgres psql -c "CREATE DATABASE onlyoffice;"
sudo -i -u postgres psql -c "CREATE USER onlyoffice WITH password 'onlyoffice';"
sudo -i -u postgres psql -c "GRANT ALL privileges ON DATABASE onlyoffice TO onlyoffice;"
```
3. Configure the database:

```
psql -hlocalhost -Uonlyoffice -d onlyoffice -f ../../out/linux_64/onlyoffice/documentserver/server/schema/postgresql/createdb.sql
```
**Note**: Upon that, you will be asked to provide a password for the **onlyoffice** PostgreSQL user. Please enter the **onlyoffice** password.


#### Running ONLYOFFICE products

##### Running Document Server

**Note**: All **Document Server** components run as foreground processes. Thus
you need separate terminal consoles to run them or specific tools which will
allow to run foreground processes in background mode.

1.  Start the **FileConverter** service:

```
cd ../../out/linux_64/onlyoffice/documentserver/server/FileConverter
```

```
NODE_ENV=development-linux NODE_CONFIG_DIR=$PWD/../Common/config ./converter
```

2.  Start the **SpellChecker** service:

```
cd ../../out/linux_64/onlyoffice/documentserver/server/SpellChecker
```

```
NODE_ENV=development-linux NODE_CONFIG_DIR=$PWD/../Common/config ./spellchecker
```

3.  Start the **DocService** service:

```
cd ../../out/linux_64/onlyoffice/documentserver/server/DocService
```

```
NODE_ENV=development-linux NODE_CONFIG_DIR=$PWD/../Common/config ./docservice
```

##### Running Document Builder

```
cd ../../out/linux_64/onlyoffice/documentbuilder
```

```
./docbuilder
```

##### Running Desktop Editors

```
cd ../../out/linux_64/onlyoffice/desktopeditors
```

```
LD_LIBRARY_PATH=./ ./DesktopEditors
```
