# ── Stage 1 : build du frontend Vue.js ───────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
# Supprimer le lockfile x86 pour forcer npm à résoudre les modules natifs ARM64
RUN rm -f package-lock.json && npm install

COPY . .
RUN npm run build

# ── Stage 2 : serveur Nginx léger ────────────────────────────────────────────
FROM nginx:alpine
RUN apk add --no-cache curl

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
