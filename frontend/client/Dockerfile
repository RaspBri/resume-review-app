FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
COPY . .

ARG REACT_APP_URL
ENV REACT_APP_URL=$REACT_APP_URL

RUN npm install
RUN npm run build

FROM nginx:stable-alpine AS production
COPY --from=build /app/build /usr/share/nginx/html

# CMD ["npm", "start"]

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]