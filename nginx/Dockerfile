FROM nginx:latest

RUN apt-get update && apt-get install -y openssl --no-install-recommends
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/conf/nginx.conf /etc/nginx/conf.d
