![Screenshot](https://img.shields.io/badge/python-v3.12-blue?logo=python&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/fastapi--blue?logo=fastapi&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/flask--blue?logo=gitlab&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/sqlalchemy--blue?logo=fastapi&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/postgresql-v17-blue?logo=postgresql&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/docker--blue?logo=docker&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/gitlab-ci:cd-blue?logo=gitlab&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/terraform--blue?logo=hashicorp&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/vault--blue?logo=hashicorp&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/celery-5.4.0-blue?logo=celery&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/rabbitmq-4-blue?logo=rabbitmq&logoColor=yellow)
![Screenshot](https://img.shields.io/badge/digitalocean--black?logo=digitalocean&logoColor=yellow&color=blue)
![Screenshot](https://img.shields.io/badge/betterstack--blue)
![Screenshot](https://img.shields.io/badge/coveralls--blue?logo=coveralls&logoColor=yellow)
[![Coverage Status](https://coveralls.io/repos/gitlab/memphis-tools/dummy_fastapi_flask_blog_app/badge.svg?branch=HEAD)](https://coveralls.io/gitlab/memphis-tools/dummy_fastapi_flask_blog_app?branch=HEAD)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5aa0869a8f5a4835a74f84ba0088f69e)](https://app.codacy.com/gh/memphis-tools/dummy_fastapi_flask_blog_app/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
![Known Vulnerabilities](https://snyk.io/test/github/memphis-tools/dummy_fastapi_flask_blog_app/badge.svg)
[![Better Stack Badge](https://uptime.betterstack.com/status-badges/v1/monitor/1yx67.svg)](https://uptime.betterstack.com/?utm_source=status_badge)

# DUMMY APP FOR LEARNING PURPOSES
**This is dummy blog application.**

The project is mirored from <a href="https://gitlab.com/memphis-tools/dummy_fastapi_flask_blog_app">GITHUB DUMMY FASTAPI FLASK BLOG APP</a>

Application is simultaneously served as a Flask and a FastAPI front-end. Postgresql the database and Nginx as reverse proxy.

Certbot and Nginx handle the HTTPS.

Celery and RabbitMQ are set to be able to send mail through Twilio SendGrid, as asynchrinous tasks.

Redis lists Celery's tasks executions.

Each of these services run on Docker. To avoid excessive spending only 1 virtual machine is used.

Also the Gitlab subscription is the free default one.

**Focus is more on technologies and how bind it for a project. This is the aim.**

Do not pay much attention to the HTML-CSS-JS part.

**Look at GitHub issues to see what has to be done, what should be updated.**

If the dummy example application is up you will find it at:

  Flask Front: https://dummy-ops.dev

  FastAPI Front: https://dummy-ops.dev/api/v1/docs

A **visitor account** is created for anybody: visiteur / @pplepie94 / visiteur@localhost.fr

**About Vault and sensitive datas**

The Vault here has a simple jwt authentication method. Idea is just to a avoid to have sensitive datas on Gitlab.

Purpose is that we do not want a project user, be able to echo the vars through the gitlab-ci.yml.

The SSH_PRIVATE_KEY is protected with a SSH passphrase. So the private key can be display in logs, but not the passphrase.

POSTGRES_PASSWORD in the Gitlab settings stands for the default Postgresql's Docker image password. This password is only used during unit_tests step.

By convenience, and because we do not want to use multiple virtual machines (droplets) the Vault is recreated at each new deployment into production.

Vault service is used to set sensitive datas as Docker swarm secrets. The service is shutdown before the swarm stack deployment.

So currently the Docker swarm is run by a "dummy_user"; he can exec into containers and so see the docker secrets.

Next step will be to have a Vault service always running so no secrets could be see within containers.

Remember it's just a dummy project.

**A default virtual machine with 1vcpu and 2gb RAM is needed**

## TECHNOLOGIES
Python 3.12 and later

Postgresql 15 (driver psycopg 3)

Gunicorn (for Flask)

Uvicorn (for FastAPI)

Nginx

Docker (docker compose), DockerHub, Docker Scout

Gitlab (the CI/CD chain is engaged throuh the Gitlab repo)

Terraform

Certbot

Vault

RabbitMQ

Celery

Redis

Twilio SendGrid

Lynis (for the virtual machine, droplet, hardening)

hCaptcha

Codacy

Snyk

Aikido Security

Cursor

TabNine

Cloudflare

## HOW TO SET IT, HOW IT WORKS

  Notice: if you use VisualCode remember that you can preview the markdown from VisualCode by running: Ctrl+Shift+V

  Notice: currently the postgres password is the default one.

  There is no use of the create_app design pattern for Flask.

  The FastAPI app is the main one, and executes the database initialization at boot.

  Github Action workflows are used. You must set secrets (tokens which allow the exchanges).

  ![Screenshot](illustrations/github_secrets.png)

  Celery worker use a default configuration.

  Rabbitmq is setup with a default configuration (we just set a specific user, password and vhost).

  Celery uses 2 types of exchanges: fanout and direct.

  The first one is a broadcast, which spread a task execution order.

  The second one is for the celery worker to return message result to the rabbitmq queue.

        rabbitmqctl list_queues -p your_rabbitmq_vhost name messages

        rabbitmqctl list_bindings -p your_rabbitmq_vhost

  Cloudflare even with a free subscription offers a basic protection against bots:

  ![Screenshot](illustrations/cloudflare_security_events.png)

  **Codacy and Snyk** already display updates to be done. You can also see from **Sonarqube** that there's much to be done:

  ![Screenshot](illustrations/sonarqube_stats.png)

  Also **Zed Attack Proxy (ZAP)** raises warnings and alerts:

  ![Screenshot](illustrations/zap_stats.png)

### POSTGRESQL PREQUISITES FOR LOCAL USAGE
--------------------------
  - For a local usage (without docker) first be sure service is running (Linux example command):

        sudo systemctl start postgresql

  - Password must match the POSTGRES_PASSWORD defined in the .envrc.* files. So you may have to update it.

        [postgres@sanjurolab ~]$ psql
        psql (15.1)
        Type "help" for help.

        postgres=# \password postgres
        Enter new password for user "postgres":
        Enter it again:


### LOCAL EXECUTION PREQUISITES
-------------------------
  You will need a SECRET_KEY var in able to run the application.

  To create one, either use python secrets module, or openssl:

    python -c "import secrets;print(secrets.token_hex())"

  or

    openssl rand -hex 32

  - For a local docker execution:

    At the project root folder, touch (create) a **".env"** file.

    Notice that this file is the one used for local deployment with local-docker-stack.yml.

    The admin user is an application's admin. Not a Postgresql role. The engine use the default postgres user.

    The "dummy-operator" must match the one defined in the Gunicorn Dockerfile.

    Set something like this:

        export ADMIN_LOGIN="admin"
        export ADMIN_PASSWORD="@pplepie94" #notice this is not the real password
        export ADMIN_EMAIL="admin@localhost.fr" #use a real email
        export APP_FOLDER=/home/dummy-operator/flask
        export BETTERSTACK_SOURCE_TOKEN="yourBetterstackToken"
        export CELERY_BROKER_URL="pyamqp://$RABBITMQ_DEFAULT_USER:$RABBITMQ_DEFAULT_PASS@rabbitmq:5672/$RABBITMQ_DEFAULT_VHOST"
        export CELERY_RESULT_BACKEND="your redis url"
        export COVERALLS_REPO_TOKEN="yourCoverallsToken"
        export FLASK_APP=project/__init__.py
        export FLASK_DEBUG=1
        export HCAPTCHA_SITE_KEY="yourHcaptchaSiteSecret"
        export HCAPTCHA_SITE_SECRET="yourHcaptchaSecret"
        export PDF_FOLDER_PATH="/tmp"
        export PDF_FILE_NAME="dummy_books"
        export POSTGRES_USER="postgres"
        export POSTGRES_PASSWORD="postgres"
        export POSTGRES_TEST_DB_NAME="test_dummy_blog"
        export POSTGRES_PORT="5432"
        export POSTGRES_HOST="db"
        export RABBITMQ_DEFAULT_USER="your_rabbitmq_user"
        export RABBITMQ_DEFAULT_PASS="your_rabbitmq_password"
        export RABBITMQ_DEFAULT_VHOST="your_rabbitmq_vhost"
        export SECRET_KEY="YourSUperSecretKey123oclock"
        export SCOPE="development"
        export SENDGRID_API_KEY="your sendgrid api key"
        export SWARM_IP="your_ip"
        export TEST_USER_PWD="@pplepie94"
        export TIMEZONE="Europe/Paris"
        export MPLCONFIGDIR=/tmp/matplotlib_config

    Notice:

    POSTGRES_HOST refers to the postgresql service name

    SCOPE: for a local execution you set "development".

    Anything else than "production" or "development" allow tests to be run.

### HOW RUN IT LOCALLY
----------------------------------------------

Clone the repository

    `git clone https://github.com/memphis-tools/dummy_fastapi_flask_blog_app.git`

    `cd dummy_fastapi_flask_blog_app`

You do not need to create a python virtualenv.

  - Example (for Linux):

      ./local_stack_deployment.sh

      docker service ls

      docker swarm leave --force

  - Flask front-end will be reachable at:

      http://localhost/

  - Swagger docs will then be served at:

      http://localhost/api/v1/docs

    As we run locally, there is a default test database set with some dummies data (see app/packages/utils.py).

    You will be able to login with following (example) credentials: donald / applepie94 / donald@localhost.fr.

    You can set some default variables in "app/packages/settings.py".

### HOW TEST IT
---------------
  Notice we set a pytest.ini file to define our patterns.

  Tests occure when you run it locally, or during the ci-cd execution.

  Avoid to change tests order (particulary about the session cookie in tests_flask_urls).

  To run test for a local execution (**ensure postgresql service is started, and the .env file created**):

      python -m venv venv

      source venv/bin/activate

      source .env

      pip install -U pip

      pip install -r app/packages/celery_client_and_worker/requirements.txt

      pip install -r app/packages/fastapi/requirements.txt

      pip install -r app/packages/flask_app/requirements.txt

      SCOPE="test"

      POSTGRES_HOST="your_local_ipv4"

      python -m coverage run -m pytest -vs app/

      python -m coverage report

  To create a friendly html report in a cov_html folder:

      python -m coverage html -d cov_html

  90 should be the minimum relevent score.

  To run test during the gilab-ci execution, see .gitlab-ci.yml file.

  You must also pay attention to the following Gitlab's CI/CD settings variables.
  During gitlab-ci tests, the official postgresql image is used.

      POSTGRES_HOST: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_PORT: 5432
      POSTGRES_USER: postgres
      POSTGRES_DB: test_dummy_blog

### HOW CHECK PEP'S RECOMMENDED SYNTAX
--------------------------------------
      pip install black pylint flake8-html bandit

  You can use black to format code:

      black app/packages/

      black app/tests/

  You can check for a flake8's lint:

      flake8 app/ --max-line-length=127 --count --statistics

  You can check the lint score:

      pylint app/

  You can check for common security issues in Python code:

      python -m bandit -r app/

### HOW RUN IT IN PRODUCTION
----------------------------

  - You must have a virtual machine. Here we used [DigitalOcean](https://www.digitalocean.com/) cloud provider.

    We use HashiCorp Terraform tool to generate the virtual machine (the "droplet") on DigitalOcean.

    [Install Hashicorp's terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

    Notice and adapt the [VirtualMachine /Droplet's definition](https://github.com/memphis-tools/dummy_fastapi_flask_blog_app/tree/development/terraform/debian_with_docker.tf) file.

    These variables are used to create the virtual machine ("droplet"), and to setup the Vault.

    Notice the "terraform/digitalocean_firewall.tf" file which set the desired rules (8200 is for the Vault).

    You must have a DigitalOcean account, then created a personal access token, and a ssh dedicated key-pair.

    In the following sequence you can change directory into the terraform dir (cd terraform) to avoid the "-chdir" usage.

      Copy the variables file and set the ones you need:

      `cp terraform/variables.tf.ORI terraform/variables.tf`

      Export your DigitalOcean personal access token:

      `export DO_PAT="dop_v1_2WhatADopSecretIsNotItAsLongItIs"`

      Initialize terraform:

      `terraform -chdir=terraform init`

      Create terraform plan:

      `terraform -chdir=terraform plan -var "do_token=${DO_PAT}" -var "pvt_key=[path to your private key]"`

      Execute the plan,

      `terraform -chdir=terraform apply -var "do_token=${DO_PAT}" -var "pvt_key=[path to your private key]" -auto-approve`

      Watch out the end of execution and because it succeeded, consult the following.

      `terraform -chdir=terraform state list`

      `terraform -chdir=terraform state show digitalocean_droplet.dummy-django-with-docker`

      Notice the public ipv4_address. Source your ssh private key and login through ssh.

      `ssh dummy-user@PublicIpAddress`

      If you need to destroy the droplet:

      `terraform -chdir=terraform plan -destroy -out=terraform.tfplan \
          -var "do_token=${DO_PAT}" \
          -var "pvt_key=/home/sanjuro/.ssh/terraform/id_rsa"
      `

      `terraform -chdir=terraform apply terraform.tfplan`

  - Only a push to the master branch will trigger the deploy step of the gitlab-ci.yml file

  - Do not remove the "dummy_user_certbot-etc" volume because certbot will store the https cert in it.

  - For the production docker execution:

    As we use the gitlab-ci we have to set these settings in the Gitlab project.

    Remember to add a blank line at the end of SSH_PRIVATE_KEY declaration.

    The passwords vars are used for the tests steps. They are not the ones in the vault.

        CELERY_RESULT_BACKEND
        CERTBOT_EMAIL
        CI_REGISTRY_TOKEN
        CI_REGISTRY_USER
        CODACY_PROJECT_TOKEN
        COVERALLS_REPO_TOKEN
        HCAPTCHA_SITE_KEY
        HOST_IP
        PDF_FILE_NAME
        PDF_FOLDER_PATH
        POSTGRES_PASSWORD
        RABBITMQ_DEFAULT_USER
        RABBITMQ_DEFAULT_VHOST
        SSH_PASSPHRASE
        SSH_PRIVATE_KEY
        TEST_USER_PWD
        TIMEZONE

    CERTBOT_EMAIL is set as Protected, Masked, Hidden and Expanded.

    Notice: not all the necessary CI/CD variables are illustrated in the picture below.

    ![Screenshot](illustrations/dummy_fastapi_gitlab_settings.png)

    See logs on Betterstack.

    ![Screenshot](illustrations/betterstack_dummyops_logs.png)

### USEFUL COMMANDS
------------------------------

  - to see rabbitmq queue (once you get into the container)

      rabbitmqctl list_users

      rabbitmqctl list_vhosts

      rabbitmqctl list_queues -p your_rabbitmq_user name messages

      rabbitmqctl list_bindings -p your_rabbitmq_vhost

  - to see the history of tasks executed by celery workers (once you get into the container)

      redis-cli KEYS *

      redis-cli GET <key>

      to reset the redis database: redis-cli FLUSHDB

      to remove sepecific task: redis-cli DEL celery-task-meta-<task_id>

### HARDENING

  You should use the "lynis" tool on the virtual machine and run "lynis audit system".

  80 is a minimum relevent score.

### USEFUL LINKS
-----------------
To run Flask behind Gunicorn and Nginx i used the following link:

https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/

For Flask i used:

https://www.udemy.com/course/100-days-of-code/

https://blog.miguelgrinberg.com/category/Flask

https://realpython.com/flask-blueprint/

For Flask image upload i used:

https://flask-wtf.readthedocs.io/en/0.15.x/form/

https://flask.palletsprojects.com/en/2.3.x/config/

https://flask-resize.readthedocs.io/index.html

For Flask template custom filters i used:

https://stackoverflow.com/questions/4830535/how-do-i-format-a-date-in-jinja2

For Flask hCaptcha i used:

https://github.com/KnugiHK/flask-hcaptcha

For FastAPI, the ci-cd i used:

https://fastapi.tiangolo.com/tutorial/security/

https://fastapi.tiangolo.com/tutorial/bigger-applications/

https://pypi.org/project/pytest-postgresql/

https://gitlab.com/gitlab-examples/postgres/-/blob/master/.gitlab-ci.yml?ref_type=heads

https://medium.com/metro-platform/continuous-integration-for-python-3-in-gitlab-e1b4446be76b

To avoid log warning "AttributeError: module 'bcrypt' has no attribute '__about__'" i followed theses links:

https://github.com/pyca/bcrypt/issues/684

https://www.geeksforgeeks.org/hashing-passwords-in-python-with-bcrypt/

Because of "CVE-2024-23342 ecdsa may be vulnerable to the Minerva attack" we do not use python-jose:

https://github.com/mpdavis/python-jose/blob/master/jose/jwt.py

See how we implement the FastAPI security principles in app/packages/fastapi/routes/routes_and_authentication.py

To use the Hashicorp Vault, and learn how to use it:

https://hub.docker.com/r/hashicorp/vault

https://testdriven.io/blog/dynamic-secret-generation-with-vault-and-flask/

https://testdriven.io/blog/managing-secrets-with-vault-and-consul/

https://developer.hashicorp.com/vault/tutorials/auto-unseal/autounseal-transit

https://docs.gitlab.com/ee/integration/vault.html

https://developer.hashicorp.com/vault/docs/auth/jwt#redirect-uris

https://developer.hashicorp.com/vault/tutorials/auth-methods/approle

https://support.hashicorp.com/hc/en-us/articles/12406076771347-Vault-JWT-auth-with-static-keys

To understand Terraform templates usage i used:

https://spacelift.io/blog/terraform-templates

To set the DigitalOcean Firewall through Terraform i used:

https://www.digitalocean.com/community/tutorials/how-to-import-existing-digitalocean-assets-into-terraform

https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs/resources/firewall

To set Nginx i used:

https://www.ssllabs.com/ssltest/analyze.html

https://nginx.org/en/docs/http/ngx_http_ssl_module.html

https://nginx.org/en/docs/http/configuring_https_servers.html

https://www.nginx.com/blog/http-strict-transport-security-hsts-and-nginx/

https://www.nginx.com/resources/glossary/http2/

https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP

For the matplotlib charts i used:

https://matplotlib.org/stable/gallery/user_interfaces/web_application_server_sgskip.html

For the logo and favicon.ico i used:

https://www.canva.com

About predefined variables for gitlab-ci:

https://docs.gitlab.com/ee/ci/variables/

For the Docker-Hub registry credentials:

https://docs.gitlab.com/ee/user/packages/container_registry/authenticate_with_container_registry.html

For Celery, RabbitMQ and Redis is used:

https://github.com/memphis-tools/dummy_flask_rabbitmq_celery/blob/main/start_application.sh
