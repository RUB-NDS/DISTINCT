# compile gui with the official node image (the nodesource repository for node 17 no longer installs)
FROM node:22-slim AS gui
ARG MODE
ENV VUE_APP_MODE=$MODE
WORKDIR /gui
COPY ./gui/package.json ./gui/package-lock.json ./
RUN npm ci
COPY ./gui ./
RUN npm run build

FROM ubuntu:20.04

# install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt upgrade -y
RUN apt install -y \
  curl \
  python3 \
  python3-pip \
  openjdk-11-jre \
  mitmproxy

# create dirs for distinct-core
RUN mkdir -p /app/data/tmp
RUN mkdir -p /app/data/pocs

# copy distinct-core and compiled gui
WORKDIR /app
COPY ./ ./distinct-core
COPY --from=gui /gui/dist ./distinct-core/gui/dist

# set production (MODE=prod) or demo (MODE=demo) mode
ARG MODE
ENV PYTHON_APP_MODE=$MODE

# install distinct-core requirements
WORKDIR /app/distinct-core
RUN pip3 install -r requirements.txt

# run distinct-core
WORKDIR /app/distinct-core
CMD ["python3", "distinct-core.py"]
