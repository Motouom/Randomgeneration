FROM python:3.10.12

ENV FLASK_ENV=production

WORKDIR /APP

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD flask run --host=0.0.0.0