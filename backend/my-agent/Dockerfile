FROM python:3.12.13

RUN apt-get update && apt-get install -y --no-install-recommends portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . .
RUN uv sync

CMD ["uv", "run", "python", "src/agents/main_agent.py", "dev"]
