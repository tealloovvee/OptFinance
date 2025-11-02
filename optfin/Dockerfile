FROM python:3.13-slim-bookworm

SHELL ["/bin/bash", "-c"]

RUN mkdir codefile
WORKDIR codefile

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /codefile/
RUN pip install -r requirements.txt

ADD . /codefile/
COPY .env.docker /codefile/.env

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY coingecko_scraper_cron /etc/cron.d/coingecko_scraper
RUN chmod 0644 /etc/cron.d/coingecko_scraper && crontab /etc/cron.d/coingecko_scraper

ENTRYPOINT ["/entrypoint.sh"]

