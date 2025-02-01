#!/bin/bash

# First arg is the dummy vault address (https://dummy-ops.dev:8200)
# Second arg is the "VAULT_ID_TOKEN" (the payload used to get a VAULT_TOKEN and so to fetch secrets)
export VAULT_TOKEN="$(vault write -address=$1 -field=token auth/jwt/login role=gitlab_jwt jwt=$2)"
echo "$(vault kv get -address=$1 -field=ADMIN_EMAIL kv/dummy_vault)" | docker secret create ADMIN_EMAIL - &> /dev/null
echo "$(vault kv get -address=$1 -field=ADMIN_LOGIN kv/dummy_vault)" | docker secret create ADMIN_LOGIN - &> /dev/null
echo "$(vault kv get -address=$1 -field=ADMIN_PASSWORD kv/dummy_vault)" | docker secret create ADMIN_PASSWORD - &> /dev/null
echo "$(vault kv get -address=$1 -field=BETTERSTACK_SOURCE_TOKEN kv/dummy_vault)" | docker secret create BETTERSTACK_SOURCE_TOKEN - &> /dev/null
echo "$(vault kv get -address=$1 -field=CELERY_BROKER_URL kv/dummy_vault)" | docker secret create CELERY_BROKER_URL - &> /dev/null
echo "$(vault kv get -address=$1 -field=HCAPTCHA_SITE_SECRET kv/dummy_vault)" | docker secret create HCAPTCHA_SITE_SECRET - &> /dev/null
echo "$(vault kv get -address=$1 -field=POSTGRES_PASSWORD kv/dummy_vault)" | docker secret create POSTGRES_PASSWORD - &> /dev/null
echo "$(vault kv get -address=$1 -field=RABBITMQ_DEFAULT_PASS kv/dummy_vault)" | docker secret create RABBITMQ_DEFAULT_PASS - &> /dev/null
echo "$(vault kv get -address=$1 -field=SECRET_KEY kv/dummy_vault)" | docker secret create SECRET_KEY - &> /dev/null
echo "$(vault kv get -address=$1 -field=SENDGRID_API_KEY kv/dummy_vault)" | docker secret create SENDGRID_API_KEY - &> /dev/null
unset VAULT_TOKEN
