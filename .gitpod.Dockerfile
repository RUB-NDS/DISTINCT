FROM ubuntu:20.04

# install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt upgrade -y

RUN apt install -y \
  xfce4 \
  xfce4-goodies \
  curl \
  wget \
  python3 \
  python3-pip \
  openjdk-11-jre \
  mitmproxy \
  npm \
  tightvncserver \
  novnc \
  git \
  git-lfs \
  gnupg \
  sudo

# install nodejs
RUN curl -fsSL https://deb.nodesource.com/setup_17.x | bash -
RUN apt install -y nodejs

# install mongodb
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
RUN apt update
RUN apt install -y mongodb-org

# create dirs for distinct-browser
RUN mkdir -p /app/data/tmp
RUN mkdir -p /app/data/pocs
RUN mkdir -p /app/data/chrome-profiles
RUN mkdir -p /app/data/chrome-extensions
RUN mkdir -p /app/data/chrome-proxy
RUN mkdir -p /app/data/db
RUN chmod -R 777 /app/data

# fix: set default terminal emulator
RUN update-alternatives --set x-terminal-emulator /usr/bin/xfce4-terminal.wrapper
