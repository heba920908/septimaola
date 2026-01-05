FROM node:18-alpine
WORKDIR /app
USER root
EXPOSE 5173
CMD ["sh", "-c", "npm install --no-package-lock && npm run dev -- --host 0.0.0.0 --port 5173"]
