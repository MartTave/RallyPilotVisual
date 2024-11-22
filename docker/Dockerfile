# Dockerfile
FROM debian:stable-slim
RUN apt-get -y update
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y


# Rally part.
WORKDIR /app
RUN apt-get update && apt-get install -y git && apt-get clean
RUN git clone -b GA https://github.com/MartTave/RallyPilotVisual.git .

RUN apt-get update && apt-get install -y xvfb


RUN set -xe \
    && apt-get update \
    && apt-get install -y python3.10 && apt-get install -y python3-venv

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip install python3_xlib

RUN apt-get update && \
    apt-get install -y xvfb x11-utils libgl1-mesa-dri && \
    rm -rf /var/lib/apt/lists/*
  
WORKDIR /usr/bin
COPY xvfb-startup.sh .
RUN chmod +x xvfb-startup.sh

RUN sed -i 's/\r$//' xvfb-startup.sh
ARG RESOLUTION="1920x1080x24"
ENV XVFB_RES="${RESOLUTION}"
ENV DISPLAY=":99"

RUN apt-get update -y \
  && apt-get install --no-install-recommends -y mesa-utils

EXPOSE 5000
CMD ["docker/startup.sh"]
