# base image
FROM docker.io/library/node:18-alpine

RUN apk update && apk add --no-cache --virtual .gyp python3 make g++
# Install Chrome
RUN apk add chromium
ENV CHROME_BIN='/usr/bin/chromium-browser'

# create directory frontend on container
WORKDIR /frontend
# copy package.json and yarn.lock from host machine to container
COPY package.json yarn.lock /frontend/
# install frontend libraries on container
RUN yarn
RUN apk del .gyp
# add all configuration files
COPY angular.json tsconfig.json karma.conf.js proxy.conf.docker.json /frontend/
