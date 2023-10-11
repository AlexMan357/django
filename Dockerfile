FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /django-app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY site_for_learning .

CMD ["gunicorn", "site_for_learning.wsgi:application", "--bind", "0.0.0.0:8000"]