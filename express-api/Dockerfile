FROM node:20 AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
EXPOSE 3001
CMD ["node", "route.js"]