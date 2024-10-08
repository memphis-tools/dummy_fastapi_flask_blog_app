FROM python:3.11-slim-bookworm

# create directory for the dummy-operator user
RUN mkdir -p /home/dummy-operator

# create the dummy-operator user
RUN addgroup --system dummy-operator && adduser --system --group dummy-operator

# create the appropriate directories
ENV HOME=/home/dummy-operator
ENV APP_HOME=/home/dummy-operator/flask
RUN mkdir $APP_HOME; \
    mkdir /var/log/gunicorn; \
    mkdir -p $APP_HOME/flask_app; \
    mkdir -p $APP_HOME/database; \
    mkdir -p $APP_HOME/staticfiles/{css,js,img};

WORKDIR $APP_HOME

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

COPY ./app/packages/flask_app/project/static/favicon.ico $APP_HOME/staticfiles/
COPY ./app/packages/flask_app/project/static/css/* $APP_HOME/staticfiles/css/
COPY ./app/packages/flask_app/project/static/js/* $APP_HOME/staticfiles/js/
COPY ./app/packages/flask_app/project/static/js/all.js $APP_HOME/staticfiles/js/
COPY ./app/packages/flask_app/project/static/img/* $APP_HOME/staticfiles/img/
COPY ./app/packages/flask_app/project/media/* $APP_HOME/staticfiles/img/
RUN touch /var/log/gunicorn/flask.logs
COPY ./app/packages/flask_app/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy Flask project
COPY /app/packages/flask_app $APP_HOME/flask_app
COPY /app/packages/database $APP_HOME/database
COPY /app/packages/handle_passwords.py $APP_HOME/
COPY /app/packages/log_events.py $APP_HOME/
COPY /app/packages/logtail_handler.py $APP_HOME/
COPY /app/packages/settings.py $APP_HOME/
COPY /app/packages/utils.py $APP_HOME/

EXPOSE 8001

# chown all the app files to the dummy-operator user
RUN chown -R dummy-operator:dummy-operator $APP_HOME
RUN chown -R dummy-operator:dummy-operator /var/log/gunicorn/

USER dummy-operator
