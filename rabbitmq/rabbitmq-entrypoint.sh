#!/bin/bash

DEFAULT_PASS=$(cat /run/secrets/RABBITMQ_DEFAULT_PASS)

echo "default_user = dummy_ops_admin" >> /etc/rabbitmq/rabbitmq.conf
echo "default_pass = ${DEFAULT_PASS}" >> /etc/rabbitmq/rabbitmq.conf

exec docker-entrypoint.sh rabbitmq-server
