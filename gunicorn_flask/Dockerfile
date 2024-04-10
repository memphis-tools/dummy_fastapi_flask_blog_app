FROM python:3.11-slim-buster

# create directory for the dummy-operator user
RUN mkdir -p /home/dummy-operator

# create the dummy-operator user
RUN addgroup --system dummy-operator && adduser --system --group dummy-operator

# create the appropriate directories
ENV HOME=/home/dummy-operator
ENV APP_HOME=/home/dummy-operator/flask
RUN mkdir $APP_HOME; \
    mkdir /var/log/gunicorn; \
    mkdir $APP_HOME/staticfiles;

WORKDIR $APP_HOME

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

COPY ./app/packages/flask_app/project/static/* $APP_HOME/staticfiles/
COPY ./app/packages/flask_app/project/static/js/all.js $APP_HOME/staticfiles/
COPY ./app/packages/flask_app/project/media/* $APP_HOME/staticfiles/
RUN touch /var/log/gunicorn/flask.logs
COPY ./app/packages/flask_app/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy project
COPY . $APP_HOME

EXPOSE 8001

# chown all the app files to the dummy-operator user
RUN chown -R dummy-operator:dummy-operator $APP_HOME
RUN chown -R dummy-operator:dummy-operator /var/log/gunicorn/

USER dummy-operator
