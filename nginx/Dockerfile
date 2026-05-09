FROM nginx:1.30.0-alpine3.23-slim

RUN apk upgrade --no-cache && apk add openssl
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/conf/nginx.conf /etc/nginx/conf.d
