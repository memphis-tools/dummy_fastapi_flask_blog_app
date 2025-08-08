FROM rabbitmq:4.1.3-management

COPY ./rabbitmq/rabbitmq.conf /etc/rabbitmq/conf.d/20-custom.conf
COPY ./rabbitmq/rabbitmq-entrypoint.sh /usr/local/bin/

RUN chown -R rabbitmq:rabbitmq /etc/rabbitmq/
RUN chmod +x /usr/local/bin/rabbitmq-entrypoint.sh
RUN chown rabbitmq:rabbitmq /usr/local/bin/rabbitmq-entrypoint.sh

EXPOSE 5672

USER rabbitmq

ENTRYPOINT ["/usr/local/bin/rabbitmq-entrypoint.sh"]
