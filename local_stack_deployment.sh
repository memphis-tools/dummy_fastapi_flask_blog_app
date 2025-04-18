#!/bin/bash
#A dummy deployment for local docker swarm execution

GREEN='\033[1;32m'
RESET='\033[0m'
WHITE='\033[1;97m'
source .env

echo -e "$WHITE[+] Ensure docker swarm is not at used $RESET"
SWARM_STATE=$(docker info --format '{{.Swarm.LocalNodeState}}')
if ! [[ $SWARM_STATE == 'inactive' ]]
then
	docker swarm leave --force &>/dev/null
fi

echo -e "$WHITE[+] Building the services images $RESET"
docker compose -f local_build_docker-images.yml build
echo -e "$GREEN[+] Services images built $RESET"

echo -e "$WHITE[+] Initializing docker swarm $RESET"
docker swarm init --advertise-addr=$SWARM_IP &>/dev/null
echo -e "$GREEN[+] Docker swarm initialized $RESET"

echo -e "$WHITE[+] Creating docker swarm secrets $RESET"
echo "$ADMIN_EMAIL" | docker secret create ADMIN_EMAIL - &> /dev/null
echo "$ADMIN_LOGIN" | docker secret create ADMIN_LOGIN - &> /dev/null
echo "$ADMIN_PASSWORD" | docker secret create ADMIN_PASSWORD - &> /dev/null
echo "$BETTERSTACK_SOURCE_TOKEN" | docker secret create BETTERSTACK_SOURCE_TOKEN - &> /dev/null
echo "$BETTERSTACK_TEAM_TOKEN" | docker secret create BETTERSTACK_TEAM_TOKEN - &> /dev/null
echo "$CELERY_BROKER_URL" | docker secret create CELERY_BROKER_URL - &> /dev/null
echo "$HCAPTCHA_SITE_SECRET" | docker secret create HCAPTCHA_SITE_SECRET - &> /dev/null
echo "$POSTGRES_PASSWORD" | docker secret create POSTGRES_PASSWORD - &> /dev/null
echo "$RABBITMQ_DEFAULT_PASS" | docker secret create RABBITMQ_DEFAULT_PASS - &> /dev/null
echo "$SECRET_KEY" | docker secret create SECRET_KEY - &> /dev/null
echo "$SENDGRID_API_KEY" | docker secret create SENDGRID_API_KEY - &> /dev/null
echo -e "$GREEN[+] Docker swarm secrets created $RESET"

echo -e "$WHITE[+] Deploying the swarm stack $RESET"
docker stack deploy --detach -c local_docker-stack.yml dummy_flask_fastapi_stack &>/dev/null
echo -e "$GREEN[+] [$SCOPE] The swarm stack is deployed $RESET"
