FROM python:3.12-bookworm

# ---------------------------------------------------------------------------
# System packages + Node.js
# ---------------------------------------------------------------------------
# Node is installed HERE (not by the devcontainer feature) so that npm is
# available during the Docker build for installing Playwright browsers.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget jq ripgrep unzip \
    # Chromium + runtime deps
    chromium \
    fonts-liberation fonts-noto-color-emoji fonts-freefont-ttf \
    libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 xdg-utils \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Python dependencies
# ---------------------------------------------------------------------------
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install --break-system-packages -r /tmp/requirements-dev.txt \
    && rm /tmp/requirements-dev.txt

# ---------------------------------------------------------------------------
# Playwright (installed as root so it has permission to write everywhere)
# ---------------------------------------------------------------------------
RUN npm install -g @playwright/test \
    && npx playwright install --with-deps chromium

# ---------------------------------------------------------------------------
# Browser env vars
# ---------------------------------------------------------------------------
ENV CHROME_BIN=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# ---------------------------------------------------------------------------
# Create non-root user + copy Playwright browsers to their cache
# ---------------------------------------------------------------------------
RUN useradd -m -s /bin/bash dev \
    && mkdir -p /home/dev/.claude \
    && mkdir -p /home/dev/.config/claude \
    && mkdir -p /home/dev/.config/gh \
    && mkdir -p /home/dev/.cache \
    && if [ -d /root/.cache/ms-playwright ]; then cp -r /root/.cache/ms-playwright /home/dev/.cache/ms-playwright; fi \
    && chown -R dev:dev /home/dev \
    && npm_prefix="$(npm config get prefix)" \
    && npm_root="$(npm root -g)" \
    && if [ -d "$npm_root" ]; then chown -R dev:dev "$npm_root"; fi \
    && if [ -d "$npm_prefix/bin" ]; then chown -R dev:dev "$npm_prefix/bin"; fi

ENV PLAYWRIGHT_BROWSERS_PATH=/home/dev/.cache/ms-playwright

WORKDIR /workspace
CMD ["bash"]