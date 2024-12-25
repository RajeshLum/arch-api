FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Running CRON job for database population
RUN apt-get update && apt-get install -y cron
COPY cronjob /etc/cron.d/populate-cron
RUN chmod 0644 /etc/cron.d/populate-cron
RUN crontab /etc/cron.d/populate-cron

# Copy the rest of the app files
COPY . /app/
COPY .env /app/.env

EXPOSE 8000

CMD ["sh", "-c", "cron && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
