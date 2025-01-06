FROM python:3.13-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic

EXPOSE 8000

CMD ["gunicorn", "aim.wsgi:application", "--bind", "0.0.0.0:8000"]