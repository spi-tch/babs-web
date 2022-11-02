FROM python:3.10-slim-buster

WORKDIR /app

ARG GIT_USER
ARG GIT_PASSWORD

COPY requirements.txt /app/requierments.txt
COPY . /app

RUN apt-get update && apt-get install libgeos-dev -y
RUN git config --global user.email $GIT_USER
RUN git config --global user.password $GIT_PASSWORD
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
RUN ssh-keyscan -t rsa github.com >>~/.ssh/known_hosts

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0

EXPOSE 5000
COPY start.sh /usr/start.sh
RUN chmod +x /usr/start.sh

CMD ["sh", "/usr/start.sh"]
