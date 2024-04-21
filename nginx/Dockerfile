FROM nginx

RUN apt-get update && apt-get install -y openssl
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/conf/nginx.conf /etc/nginx/conf.d
RUN mkdir /etc/ssl/dhparam/ 
COPY ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx","-g","daemon off;"]
