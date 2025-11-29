FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV PORT=8000

# Run migrations and collectstatic in your deployment orchestration before starting the app
CMD ["gunicorn", "pharmagestion.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]