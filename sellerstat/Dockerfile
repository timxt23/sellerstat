FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --upgrade pip  --no-cache-dir

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]