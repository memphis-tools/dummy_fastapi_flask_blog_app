#!/usr/bin/env bash

# First arg is the dummy vault address (https://dummy-ops.dev:8200)
# Second arg is the "VAULT_ID_TOKEN" (the payload used to get a VAULT_TOKEN and so to fetch secrets)
export VAULT_TOKEN="$(vault write -address=$1 -field=token auth/jwt/login role=gitlab_jwt jwt=$2)"
echo "export POSTGRES_PASSWORD=\"$(vault kv get -address=$1 -field=POSTGRES_PASSWORD kv/dummy_vault)\"" >> /home/dummy_user/envrc
echo "export SECRET_KEY=\"$(vault kv get -address=$1 -field=SECRET_KEY kv/dummy_vault)\"" >> /home/dummy_user/envrc
echo "export ADMIN_LOGIN=\"$(vault kv get -address=$1 -field=ADMIN_LOGIN kv/dummy_vault)\"" >> /home/dummy_user/envrc
echo "export ADMIN_EMAIL=\"$(vault kv get -address=$1 -field=ADMIN_EMAIL kv/dummy_vault)\"" >> /home/dummy_user/envrc
echo "export ADMIN_PASSWORD=\"$(vault kv get -address=$1 -field=ADMIN_PASSWORD kv/dummy_vault)\"" >> /home/dummy_user/envrc
echo "export BETTERSTACK_SOURCE_TOKEN=\"$(vault kv get -address=$1 -field=BETTERSTACK_SOURCE_TOKEN kv/dummy_vault)\"" >> /home/dummy_user/envrc
echo "export HCAPTCHA_SECRET_KEY=\"$(vault kv get -address=$1 -field=HCAPTCHA_SECRET_KEY kv/dummy_vault)\"" >> /home/dummy_user/envrc
unset VAULT_TOKEN
