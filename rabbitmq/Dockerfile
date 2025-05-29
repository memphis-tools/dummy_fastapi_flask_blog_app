FROM rabbitmq:4.1.0-management

COPY ./rabbitmq/rabbitmq.conf /etc/rabbitmq/conf.d/20-custom.conf

RUN chown -R rabbitmq:rabbitmq /etc/rabbitmq/

EXPOSE 5672

USER rabbitmq

CMD ["rabbitmq-server"]
