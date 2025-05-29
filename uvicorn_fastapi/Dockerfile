FROM python:3.13.3-slim-bookworm

# create directory for the dummy-operator user
RUN mkdir -p /home/dummy-operator

# create the dummy-operator user
RUN addgroup --system dummy-operator && adduser --system --group dummy-operator

WORKDIR /code
ENV APP_HOME=/code/app

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1

# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

COPY ./app/packages/fastapi/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN mkdir -p /code/app/fastapi
COPY ./app/packages/fastapi $APP_HOME/fastapi
COPY ./app/packages/database /code/database
COPY ./app/packages/settings.py .
COPY ./app/packages/handle_passwords.py .
COPY ./app/packages/log_events.py .
COPY ./app/packages/logtail_handler.py .
COPY ./app/packages/utils.py .

RUN chown -R dummy-operator:dummy-operator /code

EXPOSE 8000

USER dummy-operator

CMD ["uvicorn", "app.fastapi.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
