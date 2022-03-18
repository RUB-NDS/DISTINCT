FROM ubuntu:20.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update dependencies
RUN apt update
RUN apt upgrade -y

# Install desktop
RUN apt install -y xfce4 xfce4-goodies

# Install dependencies
RUN apt install -y \
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
  mitmproxy

# Fixes
RUN update-alternatives --set x-terminal-emulator /usr/bin/xfce4-terminal.wrapper

# VNC and NoVNC config
ENV USER root
ENV VNCPORT 5900
ENV NOVNCPORT 9090
ENV VNCPWD changeme
ENV VNCDISPLAY 1920x1080
ENV VNCDEPTH 16

# VNC
EXPOSE 5900
# NoVNC
EXPOSE 9090
# API
EXPOSE 8080

# Setup VNC
RUN mkdir -p /root/.vnc/
RUN echo $VNCPWD | vncpasswd -f > /root/.vnc/passwd
RUN chmod 600 /root/.vnc/passwd
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

# Setup NoVNC
RUN openssl req -new -x509 -days 365 -nodes \
  -subj "/C=US/ST=IL/L=Springfield/O=OpenSource/CN=localhost" \
  -out /etc/ssl/certs/novnc_cert.pem -keyout /etc/ssl/private/novnc_key.pem \
  > /dev/null 2>&1
RUN cat /etc/ssl/certs/novnc_cert.pem /etc/ssl/private/novnc_key.pem \
  > /etc/ssl/private/novnc_combined.pem
RUN chmod 600 /etc/ssl/private/novnc_combined.pem

# Setup Chromium
RUN git clone https://github.com/scheib/chromium-latest-linux.git /chromium
RUN /chromium/update.sh

# Create app
RUN mkdir /app
WORKDIR /app

# Copy chrome extensions
COPY ./distinct-chrome-extension ./distinct-chrome-extension
COPY ./ace-chrome-extension ./ace-chrome-extension

# Install mitmproxy
COPY ./mitmproxy ./mitmproxy
RUN pip3 install -r ./mitmproxy/requirements.txt

# Install browser api
COPY ./distinct-browser-api ./distinct-browser-api
RUN pip3 install -r ./distinct-browser-api/requirements.txt

WORKDIR /app
ENTRYPOINT [ "/bin/bash", "-c", " \
  mkdir -p /app/data/chrome-profiles; \
  mkdir -p /app/data/chrome-extensions; \
  mkdir -p /app/data/chrome-proxy; \
  echo 'NoVNC Certificate Fingerprint:'; \
  openssl x509 -in /etc/ssl/certs/novnc_cert.pem -noout -fingerprint -sha256; \
  vncserver :0 -rfbport $VNCPORT -geometry $VNCDISPLAY -depth $VNCDEPTH -localhost; \
  /usr/share/novnc/utils/launch.sh --listen $NOVNCPORT --vnc localhost:$VNCPORT \
    --cert /etc/ssl/private/novnc_combined.pem & \
  python3 distinct-browser-api/distinct-browser-api.py \
" ]
