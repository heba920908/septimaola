FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
USER root
EXPOSE 5173 80
CMD ["sh", "-c", "npm install --no-package-lock && npm run build && serve -s dist -l 80"]
