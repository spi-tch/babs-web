FROM python:3.10-slim-buster

WORKDIR /app

ARG GIT_TOKEN

COPY requirements.txt /app/requierments.txt
COPY . /app

RUN apt-get update && apt-get install libgeos-dev git -y
RUN pip install --no-cache-dir git+https://oauth2:$GIT_TOKEN@github.com/Babs-Technologies/kg.git@staging
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0

EXPOSE 5000
COPY start.sh /usr/start.sh
RUN chmod +x /usr/start.sh

CMD ["sh", "/usr/start.sh"]
