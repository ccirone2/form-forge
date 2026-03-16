FROM python:3.12-bookworm

# ---------------------------------------------------------------------------
# System packages + Node.js 20
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget jq ripgrep unzip \
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
# Playwright — installs Chromium + all required system deps via --with-deps
# ---------------------------------------------------------------------------
RUN npm install -g @playwright/test \
    && npx playwright install --with-deps chromium

# ---------------------------------------------------------------------------
# Non-root user
# ---------------------------------------------------------------------------
RUN useradd -m -s /bin/bash dev \
    && mkdir -p /home/dev/.claude /home/dev/.config/claude /home/dev/.config/gh /home/dev/.cache \
    && if [ -d /root/.cache/ms-playwright ]; then \
         cp -r /root/.cache/ms-playwright /home/dev/.cache/ms-playwright; \
       fi \
    && chown -R dev:dev /home/dev

ENV PLAYWRIGHT_BROWSERS_PATH=/home/dev/.cache/ms-playwright

WORKDIR /workspace
CMD ["bash"]
