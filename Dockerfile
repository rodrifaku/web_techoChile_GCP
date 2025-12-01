FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Crear scripts para jobs de Cloud Run
RUN echo '#!/bin/bash\npython manage.py migrate' > /app/migrate.sh && chmod +x /app/migrate.sh
RUN echo '#!/bin/bash\npython manage.py createsuperuser --noinput' > /app/createsuperuser.sh && chmod +x /app/createsuperuser.sh

RUN python manage.py collectstatic --noinput


CMD ["gunicorn", "techo_chile.wsgi:application", "--bind", "0.0.0.0:8080"]
