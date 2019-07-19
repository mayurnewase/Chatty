web: chmod -R 777 dist && python manage.py install_nltk_dependencies && bin/start-nginx exec gunicorn -c conf/gunicorn.conf.py wsgi:app
