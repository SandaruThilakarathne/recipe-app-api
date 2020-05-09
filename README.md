# recipe-app-api
recipe app api source code

docker-compose build
docker-compose up

docker-compose run --rm app sh -c "python manage.py startapp user"
docker-compose run --rm  app sh -c "python manage.py test && flake8"