FROM python:alpine

WORKDIR /app

COPY requirements.txt ./

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev  
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps

COPY . .

ENV FLASK_APP=flask_app
ENV FLASK_ENV=development
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]