#!/bin/bash

app=psoftware
credenciales_file=${HOME}/.netrc

[ $# -ne 1 ] && echo "Usage: $(basename $0) <development|production>" && exit 1

[ ! -f $credenciales_file ] && echo "No se está logueado en Heroku" && heroku login

case $1 in
development)
  echo "Poblando en desarrollo..."
  docker exec -i back-end_web_1 python3 test/db_test.py
  ;;
production)
  echo "Poblando en producción..."
  heroku run python3 test/db_test.py --app psoftware
  ;;
*)
  echo "Usage: $(basename $0) <development|production>" && exit 1
esac



