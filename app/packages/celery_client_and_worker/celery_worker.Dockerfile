FROM python:slim-bookworm

# create directory for the dummy-operator user
RUN mkdir -p /home/dummy-operator

# create the dummy-operator user
RUN addgroup --system dummy-operator && adduser --system --group dummy-operator

# create the appropriate directories
ENV HOME=/home/dummy-operator

RUN mkdir $HOME/database/; \
    mkdir $HOME/staticfiles/

WORKDIR $HOME

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

COPY ./app/packages/celery_client_and_worker/requirements.txt $HOME/requirements.txt
RUN pip install --no-cache-dir --upgrade -r $HOME/requirements.txt
COPY ./app/packages/celery_client_and_worker/celery_app_folder $HOME/
COPY ./app/packages/database $HOME/database
COPY ./app/packages/utils.py $HOME
COPY ./app/packages/settings.py $HOME
RUN chown -R dummy-operator:dummy-operator $HOME
EXPOSE 5555
USER dummy-operator
CMD ["celery", "-A", "celery_app", "worker", "-l", "info"]
