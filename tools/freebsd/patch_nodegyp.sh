#!/usr/local/bin/bash

echo "Trying to find whether current node version is buggy under FreeBSD"
CURDIR=`pwd`
TEMP=`mktemp -d`
cd $TEMP
npm install statsd  >& out.log
grep -q "_LIBCPP_TRIVIAL_PAIR_COPY_CTOR" out.log
if [ $? -eq 0 ]; then
        cd ~/.cache/node-gyp/10.*/include/node
        patch -s -N -p1 <<EOF
diff -p a/common.gypi b/common.gypi
*** a/common.gypi       2021-07-19 15:26:27.407830000 +0200
--- b/common.gypi       2021-07-19 15:27:03.047869000 +0200
***************
*** 512,526 ****
          'libraries': [ '-lelf' ],
        }],
        ['OS=="freebsd"', {
-         'conditions': [
-           ['"0" < llvm_version < "4.0"', {
-             # Use this flag because on FreeBSD std::pairs copy constructor is non-trivial.
-             # Doesn't apply to llvm 4.0 (FreeBSD 11.1) or later.
-             # Refs: https://lists.freebsd.org/pipermail/freebsd-toolchain/2016-March/002094.html
-             # Refs: https://svnweb.freebsd.org/ports/head/www/node/Makefile?revision=444555&view=markup
-             'cflags': [ '-D_LIBCPP_TRIVIAL_PAIR_COPY_CTOR=1' ],
-           }],
-         ],
          'ldflags': [
            '-Wl,--export-dynamic',
          ],
--- 512,517 ----
EOF
        echo "Patching bugged ~/.cache/node-gyp/10.*/include/node/common.gypi file"
fi
cd $CURDIR
rm -rf $TEMP
