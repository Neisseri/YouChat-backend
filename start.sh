#!/bin/sh
python3 manage.py makemigrations User
python3 manage.py migrate

# TODO Start: [Student] Run with uWSGI instead
# python3 manage.py runserver 80
uwsgi --module=st_im_django.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=st_im_django.settings \
    --master \
    --http=0.0.0.0:80 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum
#TODO End: [Student] Run with uWSGI instead