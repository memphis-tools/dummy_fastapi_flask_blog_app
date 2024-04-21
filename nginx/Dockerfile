FROM nginx

RUN apk update && apk add openssl
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/conf/nginx.conf /etc/nginx/conf.d
RUN mkdir /etc/ssl/dhparam/
RUN openssl dhparam -out /etc/ssl/dhparam/dhparam-4096.pem 4096
