# One-layer image since compilation is not necessary
FROM python:3.11-alpine as final

WORKDIR /

RUN apk update && \
    apk add ffmpeg~=6

# Add container user and drop privileges
RUN addgroup -S python && \
    adduser -SG python python

USER python

WORKDIR /app

COPY --chown=python:python ./requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY --chown=python:python ./chetbot .

ENTRYPOINT [ "python3", "chetbot.py" ]
