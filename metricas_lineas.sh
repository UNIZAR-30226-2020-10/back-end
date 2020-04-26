#!/bin/bash

backend='git@github.com:UNIZAR-30226-2020-10/back-end.git'
web='git@github.com:UNIZAR-30226-2020-10/front-end_web.git'
android='git@github.com:UNIZAR-30226-2020-10/front-end_android.git'
tmp=directoriometricas

[ -d "${HOME}/${tmp}" ] && rm -r "${HOME}/${tmp}"

mkdir "${HOME}/${tmp}" || exit 1
cd "${HOME}/${tmp}" || exit 1

git clone "$backend"
git clone "$web"
git clone "$android"

rm ./front-end_web/package-lock.json

cd ..
cloc $tmp

rm -rf $tmp
