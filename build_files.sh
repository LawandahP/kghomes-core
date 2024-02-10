pip install -r requirements.txt 
python3 manage.py collectstatic --noinput
python3 manage.py migrate

# celery -A config worker -l INFO
# celery -A config beat -l INFO