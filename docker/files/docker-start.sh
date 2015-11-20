#!/bin/bash

export DJANGO_SETTINGS_MODULE=formhub.preset.ehealth_docker

sudo service mongodb start
sudo service postgresql start

sudo -H -u postgres bash -c "createdb formhubdjangodb"

cd /code

python manage.py syncdb --noinput

python manage.py migrate

python manage.py runserver 0.0.0.0:8000
