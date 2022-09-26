FROM ubuntu:20.04

# install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt upgrade -y

RUN apt install -y \
  xfce4 \
  xfce4-goodies \
  tightvncserver \
  novnc \
  net-tools \
  curl \
  wget \
  python3 \
  python3-pip \
  mitmproxy

# fix: set default terminal emulator
RUN update-alternatives --set x-terminal-emulator /usr/bin/xfce4-terminal.wrapper

# setup vnc and novnc
ENV USER root
ENV VNCPORT 9091
ENV NOVNCPORT 9090
ENV VNCDISPLAY 1920x1080
ENV VNCDEPTH 16
RUN mkdir -p /root/.vnc/
RUN touch /root/.vnc/passwd
RUN chmod 600 /root/.vnc/passwd
RUN echo "#!/bin/sh\n\
xrdb $HOME/.Xresources\n\
xsetroot -solid grey\n\
#x-terminal-emulator -geometry 80x24+10+10 -ls -title "$VNCDESKTOP Desktop" &\n\
#x-window-manager &\n\
# Fix to make GNOME work\n\
export XKL_XMODMAP_DISABLE=1\n\
/etc/X11/Xsession\n\
startxfce4 &\n\
" > /root/.vnc/xstartup
RUN chmod +x /root/.vnc/xstartup

# create dirs for distinct-browser
RUN mkdir -p /app/data/chrome-profiles
RUN mkdir -p /app/data/chrome-extensions
RUN mkdir -p /app/data/chrome-proxy

# copy distinct-browser
WORKDIR /app
COPY ./ ./distinct-browser

# setup distinct-chromium
WORKDIR /app/distinct-browser
RUN unzip ./distinct-chromium.zip -d /app

# install mitmproxy requirements
WORKDIR /app/distinct-browser/mitmproxy
RUN pip3 install -r requirements.txt

# install api requirements
WORKDIR /app/distinct-browser/api
RUN pip3 install -r requirements.txt

# run distinct-browser
WORKDIR /app/distinct-browser/api
ENTRYPOINT [ "/bin/bash", "-c", "\
  echo ${VNCPWD:-changeme} | vncpasswd -f > /root/.vnc/passwd; \
  vncserver :0 -rfbport $VNCPORT -geometry $VNCDISPLAY -depth $VNCDEPTH -localhost; \
  /usr/share/novnc/utils/launch.sh --listen $NOVNCPORT --vnc localhost:$VNCPORT & \
  python3 distinct-browser.py \
" ]
