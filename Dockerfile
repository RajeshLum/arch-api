FROM python:3.12-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    clamav \
    clamav-daemon \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Update ClamAV database
RUN freshclam

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Configure CRON job
COPY cronjob /etc/cron.d/populate-cron
RUN chmod 0644 /etc/cron.d/populate-cron
RUN crontab /etc/cron.d/populate-cron

# Copy application files
COPY . /app/
COPY .env /app/.env

EXPOSE 8000

# Start ClamAV daemon, cron, and Django server
CMD ["sh", "-c", "service clamav-daemon start && cron -f & python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
