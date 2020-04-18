#!/bin/bash

poblar_file=poblar.sh
credenciales_file=${HOME}/.netrc

[ $# -ne 1 ] && echo "Usage: $(basename $0) <development|production>" && exit 1

[ ! -x $poblar_file ] && echo "No se encuentra $poblar_file"
[ ! -f $credenciales_file ] && echo "No se está logueado en Heroku" && heroku login

app=psoftware

case $1 in
development)
  echo "Despliegue en desarrollo..."
  docker-compose down
  docker-compose build
  docker-compose up -d
  sleep 2
  ./poblar.sh development
  docker-compose logs -f
  docker-compose stop
  ;;
production)
  echo "Despliegue en producción..."
  docker-compose build
  heroku container:login
  heroku container:push web --app $app
  heroku container:release web --app $app
  ./poblar.sh production
  heroku logs --tail --app psoftware
  ;;
*)
  echo "Usage: $(basename $0) <development|production>" && exit 1
esac

