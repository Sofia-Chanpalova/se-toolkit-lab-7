FROM harbor.pg.innopolis.university/docker-hub-cache/python:3.14-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY bot/pyproject.toml bot/uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy bot source code
COPY bot/ ./bot/

# Set working directory to bot
WORKDIR /app/bot

# Run bot
CMD ["uv", "run", "bot.py"]
