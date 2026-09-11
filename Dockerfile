FROM python:3.12-slim

ARG VERSION=1.0.0

LABEL org.opencontainers.image.source=https://github.com/dsk-dev-ai/algorithm-discovery-engine
LABEL org.opencontainers.image.version=$VERSION
LABEL org.opencontainers.image.revision=$VERSION
LABEL org.opencontainers.image.description="Multi-language algorithms & data structures engine with a local algorithm synthesizer (Python tier)."
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir . && \
    python -m compileall -q src && \
    rm -rf .git

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

ENTRYPOINT ["python", "-m", "synth", "discover"]
CMD ["--smoke"]