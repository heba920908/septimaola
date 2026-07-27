FROM node:18-alpine
WORKDIR /app
USER root
EXPOSE 5173
CMD ["sh", "-c", "npm ci --no-audit --no-fund || npm install --no-audit --no-fund && npm run dev -- --host 0.0.0.0 --port 5173"]
