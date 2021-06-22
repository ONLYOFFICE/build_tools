#!/bin/sh

ONLYOFFICE_DATA_CONTAINER=false
if [ "$1" != "" ]; then
    ONLYOFFICE_DATA_CONTAINER=$1
fi

DIR="/var/www/onlyoffice/documentserver"

#Start generate AllFonts.js, font thumbnails and font_selection.bin
echo -n Generating AllFonts.js, please wait...


"$DIR/server/tools/allfontsgen"\
  --input="$DIR/core-fonts"\
  --allfonts-web="$DIR/sdkjs/common/AllFonts.js"\
  --allfonts="$DIR/server/FileConverter/bin/AllFonts.js"\
  --images="$DIR/sdkjs/common/Images"\
  --selection="$DIR/server/FileConverter/bin/font_selection.bin"\
  --output-web="$DIR/fonts"\
  --use-system="true"

chown -R ds:ds "$DIR/sdkjs"
chown -R ds:ds "$DIR/server/FileConverter/bin"
chown -R ds:ds "$DIR/fonts"

echo Done

echo -n Generating presentation themes, please wait...
"$DIR/server/tools/allthemesgen"\
  --converter-dir="$DIR/server/FileConverter/bin"\
  --src="$DIR/sdkjs/slide/themes"\
  --output="$DIR/sdkjs/common/Images"

"$DIR/server/tools/allthemesgen"\
  --converter-dir="$DIR/server/FileConverter/bin"\
  --src="$DIR/sdkjs/slide/themes"\
  --output="$DIR/sdkjs/common/Images"\
  --postfix="ios"\
  --params="280,224"

"$DIR/server/tools/allthemesgen"\
  --converter-dir="$DIR/server/FileConverter/bin"\
  --src="$DIR/sdkjs/slide/themes"\
  --output="$DIR/sdkjs/common/Images"\
  --postfix="android"\
  --params="280,224"

echo Done

#Remove gzipped fonts
rm -f $DIR/fonts/*.gz $DIR/sdkjs/common/AllFonts.js.gz

#Restart web-site and converter
if [ "$ONLYOFFICE_DATA_CONTAINER" != "true" ]; then
 supervisorctl restart ds:docservice
 supervisorctl restart ds:converter
fi
