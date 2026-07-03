FROM node:24

WORKDIR /app

RUN npm install

COPY package*.json ./

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]