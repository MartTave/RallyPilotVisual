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
RUN git clone https://github.com/MartTave/RallyPilotVisual.git .
RUN git checkout GA


RUN set -xe \
    && apt-get update \
    && apt-get install -y python3.10 && apt-get install -y python3-venv

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip install python3_xlib

RUN chmod +x docker/startup.sh

EXPOSE 5000
CMD ["docker/./startup.sh"]
