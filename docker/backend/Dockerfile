FROM python:3.12-slim

WORKDIR /app

# Fuerza IPv4 en apt: en algunos hosts (ej. presto) deb.debian.org resuelve solo a
# IPv6 y el contenedor de build no tiene salida IPv6, lo que cuelga apt-get.
RUN echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4 \
    && apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Placeholder para el montaje del perfil del candidato
RUN touch /app/perfil.md

EXPOSE 8000
