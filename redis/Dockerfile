FROM redis:alpine

RUN echo "vm.overcommit_memory = 1" > /etc/sysctl.conf

COPY ./redis/redis.conf /etc/redis/redis.conf

RUN chown -R redis:redis /etc/redis

RUN chown -R redis:redis /usr/local/bin/redis*

EXPOSE 6379

USER redis

CMD ["redis-server"]
