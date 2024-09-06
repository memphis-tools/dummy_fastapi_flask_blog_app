FROM redis:latest

RUN echo "vm.overcommit_memory = 1" > /etc/sysctl.conf

COPY ./redis/redis.conf /etc/redis/redis.conf

EXPOSE 6379

CMD ["redis-server"]
