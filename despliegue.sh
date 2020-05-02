#!/bin/bash

poblar_file=poblar.sh
credenciales_file=${HOME}/.netrc

function pruebas() {
    echo "Ejecutando pruebas ..."
    docker-compose down
    docker-compose build
    docker-compose up -d
    sleep 2
    docker exec -i back-end_web_1 python3 test/test_server.py
    if [ $? -ne 0 ]; then
      echo "ERROR: No se ha pasado las pruebas"
      docker-compose down
      exit 1
    else
      echo "... Pruebas superadas"
    fi
}

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
  pruebas
  docker-compose build
  heroku container:login
  heroku container:push web --app $app
  heroku container:release web --app $app
  ./poblar.sh production
  heroku logs --tail --app psoftware
  ;;
test)
  pruebas
  ;;
*)
  echo "Usage: $(basename $0) <development|production|test>" && exit 1
esac

