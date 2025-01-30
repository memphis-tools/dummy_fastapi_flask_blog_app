FROM nginx:1.27.3-alpine3.20-slim

RUN apk upgrade --no-cache && apk add openssl
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/conf/nginx.conf /etc/nginx/conf.d
