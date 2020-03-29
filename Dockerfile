FROM python:3.7

RUN apt-get update -y && \
    apt-get install -y libcurl4-openssl-dev \
    libssl-dev \
    libpq-dev

WORKDIR /usr/src/Musica

EXPOSE 5000
COPY Musica/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY Musica/flaskr ./flaskr
COPY Musica/test ./test

CMD [ "python3", "flaskr/app.py" ]