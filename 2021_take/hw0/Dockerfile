# https://nodejs.org/en/docs/guides/nodejs-docker-webapp/
# Why can't kill process with 1 as pid:
# https://stackoverflow.com/questions/32224101/kill-a-running-process-like-a-webserver-inside-a-docker-container-without-killin


FROM node:15

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm ci --only=production

COPY . .

EXPOSE 9000

CMD ["node", "index.js"]