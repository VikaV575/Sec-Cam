FROM python:3.12-slim

WORKDIR /app

# התקנות בסיסיות (רשות, אבל נחמד)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# הקוד
COPY ./app ./app

# תיקיות לנתונים
RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]