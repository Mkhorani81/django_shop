This is a mini shop project in which using redis, celery, pay gateway using django

For runing this project:
  1. using "pip install -r requirements.txt"
  2. python manage.py runserver

  3. For using celery need to open another terminal and running celery worker by:
    "celery -A shop worker --pool=solo --loglevel=info"
