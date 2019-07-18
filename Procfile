web: bin/start-nginx python -m spacy download en && gunicorn -c conf/gunicorn.conf.py wsgi:app
