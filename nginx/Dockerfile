FROM nginx

RUN apt-get update && apt-get install -y openssl
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/conf/nginx.conf /etc/nginx/conf.d
