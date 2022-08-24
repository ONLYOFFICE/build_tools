#!/bin/bash

SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DIR_X2T=$SCRIPTPATH/..
$("$DIR_X2T/x2t" &>/dev/null)
status=$?

[ $status -ne 88 ] && $(cp "$SCRIPTPATH/libstdc++.so.6" "$DIR_X2T/libstdc++.so.6")

