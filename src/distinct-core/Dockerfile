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
  mitmproxy \
  npm

RUN curl -fsSL https://deb.nodesource.com/setup_17.x | bash -
RUN apt install -y nodejs

# create dirs for distinct-core
RUN mkdir -p /app/data/tmp
RUN mkdir -p /app/data/pocs

# copy distinct-core
WORKDIR /app
COPY ./ ./distinct-core

# set production (MODE=prod) or demo (MODE=demo) mode
ARG MODE
ENV VUE_APP_MODE=$MODE
ENV PYTHON_APP_MODE=$MODE

# install distinct-core requirements
WORKDIR /app/distinct-core
RUN pip3 install -r requirements.txt

# install and compile gui
WORKDIR /app/distinct-core/gui
RUN npm install
RUN npm run build

# run distinct-core
WORKDIR /app/distinct-core
CMD ["python3", "distinct-core.py"]
