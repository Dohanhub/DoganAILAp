# Build and serve the Vite app with nginx
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* ./
RUN npm ci --prefer-offline --no-audit --fund=false || npm install --no-audit --fund=false
COPY . .
RUN npm run build

FROM nginx:alpine AS runner
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://localhost/ > /dev/null || exit 1
CMD ["nginx", "-g", "daemon off;"]

