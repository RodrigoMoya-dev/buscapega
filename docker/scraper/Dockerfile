FROM python:3.12-slim

WORKDIR /app

# Fuerza IPv4 en apt: en algunos hosts (ej. presto) deb.debian.org resuelve solo a
# IPv6 y el contenedor de build no tiene salida IPv6, lo que cuelga apt-get. El
# archivo persiste en la imagen, así que también aplica al `playwright install` de abajo.
RUN echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4 \
    && apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .

EXPOSE 8001
