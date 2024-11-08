FROM ghcr.io/astral-sh/uv:debian-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

RUN uv sync --frozen

EXPOSE 80

CMD ["sh", "./startup.sh"]
