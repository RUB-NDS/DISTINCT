FROM ubuntu:20.04

# install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt upgrade -y

RUN apt install -y \
  xfce4 \
  xfce4-goodies \
  curl \
  python3 \
  python3-pip \
  openjdk-11-jre \
  mitmproxy \
  npm \
  tightvncserver \
  novnc \
  net-tools \
  nano \
  curl \
  wget \
  firefox \
  git \
  python3 \
  python3-pip \
  mitmproxy \
  gnupg

# install nodejs
RUN curl -fsSL https://deb.nodesource.com/setup_17.x | bash -
RUN apt install -y nodejs

# install mongodb
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
RUN apt update
RUN apt install -y mongodb-org
RUN mkdir -p /workspace/distinct-db-data

# create dirs for distinct-browser
RUN mkdir -p /app/data/tmp
RUN mkdir -p /app/data/pocs
RUN mkdir -p /app/data/chrome-profiles
RUN mkdir -p /app/data/chrome-extensions
RUN mkdir -p /app/data/chrome-proxy

# fix: set default terminal emulator
RUN update-alternatives --set x-terminal-emulator /usr/bin/xfce4-terminal.wrapper

# setup vnc
RUN mkdir -p /root/.vnc/
RUN echo "#!/bin/sh \n\
xrdb $HOME/.Xresources \n\
xsetroot -solid grey \n\
#x-terminal-emulator -geometry 80x24+10+10 -ls -title "$VNCDESKTOP Desktop" & \n\
#x-window-manager & \n\
# Fix to make GNOME work \n\
export XKL_XMODMAP_DISABLE=1 \n\
/etc/X11/Xsession \n\
startxfce4 & \n\
" > /root/.vnc/xstartup
RUN chmod +x /root/.vnc/xstartup

# setup novnc
RUN openssl req -new -x509 -days 365 -nodes \
  -subj "/C=US/ST=IL/L=Springfield/O=OpenSource/CN=localhost" \
  -out /etc/ssl/certs/novnc_cert.pem -keyout /etc/ssl/private/novnc_key.pem \
  > /dev/null 2>&1
RUN cat /etc/ssl/certs/novnc_cert.pem /etc/ssl/private/novnc_key.pem \
  > /etc/ssl/private/novnc_combined.pem
RUN chmod 600 /etc/ssl/private/novnc_combined.pem

# setup chromium
RUN git clone https://github.com/scheib/chromium-latest-linux.git /chromium
RUN /chromium/update.sh

# setup distinct-chromium
COPY ./src/distinct-browser/distinct-chromium.zip /distinct-chromium.zip
RUN unzip /distinct-chromium.zip -d /
