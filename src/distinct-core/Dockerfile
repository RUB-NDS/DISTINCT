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
WORKDIR /app

# Copy the app
COPY ./ ./distinct-core

# Compile the GUI
WORKDIR /app/distinct-core/distinct-gui
RUN npm install
RUN npm run build

# Start the backend
WORKDIR /app/distinct-core
RUN pip3 install -r requirements.txt

CMD ["python3", "distinct-core.py"]
