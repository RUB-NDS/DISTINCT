FROM ubuntu:20.04

# API
EXPOSE 8080

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
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

# Create new app directory
RUN mkdir /app
RUN mkdir -p /app/data/tmp
RUN mkdir -p /app/data/handlers
RUN mkdir -p /app/data/pocs
WORKDIR /app

# Copy the app
COPY ./ ./distinct-core

# Install the backend
WORKDIR /app/distinct-core
RUN pip3 install -r requirements.txt

# Install the GUI
WORKDIR /app/distinct-core/distinct-gui
RUN npm install
ARG VUE_APP_MODE
ENV VUE_APP_MODE=$VUE_APP_MODE
RUN npm run build

# Run
WORKDIR /app/distinct-core
ARG PYTHON_APP_MODE
ENV PYTHON_APP_MODE=$PYTHON_APP_MODE
CMD ["python3", "distinct-core.py"]
