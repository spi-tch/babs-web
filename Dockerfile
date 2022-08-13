FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /app/requierments.txt
COPY . /app
RUN pip install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0

EXPOSE 5000
COPY start.sh /usr/start.sh
RUN chmod +x /usr/start.sh

CMD ['./temi/start.sh']

