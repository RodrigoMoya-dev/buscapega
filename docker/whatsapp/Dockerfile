FROM node:20-alpine

WORKDIR /app

# Dependencias del sistema para Baileys
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    libc6-compat

# Instalar dependencias primero (cache)
COPY package.json ./
RUN npm install --omit=dev --legacy-peer-deps

# Copiar código fuente
COPY . .

# Puerto del servicio HTTP
EXPOSE 3001

# Directorio de autenticación (montado como volumen)
VOLUME ["/app/auth"]

CMD ["node", "server.js"]
