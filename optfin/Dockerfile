FROM python:3.13-slim-bookworm

SHELL ["/bin/bash", "-c"]

RUN mkdir codefile
WORKDIR codefile

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


COPY requirements.txt /codefile/
RUN pip install -r requirements.txt

ADD . /codefile/
COPY .env.docker /codefile/.env

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

