FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .
COPY app.py .
COPY templates /app/templates  


EXPOSE 8000

CMD [ "python3", "app.py" ]