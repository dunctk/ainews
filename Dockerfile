FROM ghcr.io/astral-sh/uv:python3.11-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app


COPY ./requirements.txt /requirements.txt

RUN uv sync --frozen

COPY . /usr/src/app

EXPOSE 80

CMD ["sh", "./startup.sh"]
