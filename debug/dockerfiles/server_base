FROM python:3.9-slim-bullseye

RUN apt -y update
RUN apt -y install gcc socat libsdl2-2.0-0
RUN mkdir -p /codequest

COPY requirements.txt .
RUN pip install -r requirements.txt

ADD src /codequest/src
ADD maps /codequest/maps

# Set the display to connect to an Xserver on host
ENV DISPLAY host.docker.internal:0

# Hide pygame's logs to prevent interference with std in/out
ENV PYGAME_HIDE_SUPPORT_PROMPT hide

WORKDIR /codequest

RUN echo "python src/main.py" > run.sh
RUN chmod +x /codequest/run.sh

CMD ["/bin/sh", "-c", "./run.sh"]
