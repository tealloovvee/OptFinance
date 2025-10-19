FROM python:3.13-slim-bookworm

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

RUN mkdir codefile
WORKDIR codefile

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


COPY requirements.txt /codefile/
RUN pip install -r requirements.txt

ADD . /codefile/
COPY .env.docker /codefile/.env

WORKDIR /codefile/templates
RUN npm install
RUN npm run build

WORKDIR /codefile

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

