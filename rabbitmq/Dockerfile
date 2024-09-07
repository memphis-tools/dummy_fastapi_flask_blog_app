FROM rabbitmq:3-management

COPY ./rabbitmq/rabbitmq.conf /etc/rabbitmq/conf.d/20-custom.conf

EXPOSE 5672

CMD ["rabbitmq-server"]
