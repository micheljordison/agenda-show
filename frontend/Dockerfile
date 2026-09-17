FROM node:22-alpine AS development

WORKDIR /app

ARG VITE_API_BASE_URL=http://localhost:4050
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

EXPOSE 4000

CMD ["sh", "docker-entrypoint.sh"]

FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
ARG VITE_API_BASE_URL=/
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM nginxinc/nginx-unprivileged:stable-alpine AS production
ENV BACKEND_UPSTREAM=backend:4050
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist/spa /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/health || exit 1
