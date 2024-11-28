# Dockerfile
FROM debian:stable-slim
RUN apt-get -y update
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y
RUN apt-get update && \
apt-get install -y xvfb x11-utils libgl1-mesa-dri && \
rm -rf /var/lib/apt/lists/*

WORKDIR /usr/bin
COPY startup.sh .
RUN chmod +x startup.sh

RUN sed -i 's/\r$//' startup.sh
ARG RESOLUTION="1920x1080x24"
ENV XVFB_RES="${RESOLUTION}"
ENV DISPLAY=":99"

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y mesa-utils
    


# Rally part.
WORKDIR /app
RUN apt-get update && apt-get install -y git && apt-get clean
RUN git clone -b docker https://github.com/MartTave/RallyPilotVisual.git .
COPY . .


RUN set -xe \
    && apt-get update \
    && apt-get install -y python3-pip  \
    && apt-get install -y python3-venv



ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"


RUN pip install python3_xlib

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["startup.sh"]
