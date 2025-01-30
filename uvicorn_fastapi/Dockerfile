FROM python:3.12-slim-bookworm

WORKDIR /code
ENV APP_HOME=/code/app
ENV PYTHONDONTWRITEBYTECODE 1
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
EXPOSE 8000
CMD ["uvicorn", "app.fastapi.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
