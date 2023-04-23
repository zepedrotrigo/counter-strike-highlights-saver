# docker build . -t react:latest -f ./Dockerfile

# build environment
FROM node:16.14.2-alpine as build
WORKDIR /frontend
ENV PATH /frontend/node_modules/.bin:$PATH
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
RUN yarn global add react-scripts@3.4.1
COPY . ./
RUN yarn run build

# production environment
FROM bitnami/nginx:latest
COPY --from=build /frontend/build /opt/bitnami/nginx/html

# serve the index.html file for all requests, and then let React Router handle the routing based on the URL
RUN echo '    location / {' >> /opt/bitnami/nginx/conf/bitnami/bitnami.conf && \
    echo '        try_files $uri $uri/ /index.html;' >> /opt/bitnami/nginx/conf/bitnami/bitnami.conf && \
    echo '        add_header Cross-Origin-Opener-Policy same-origin;' >> /opt/bitnami/nginx/conf/bitnami/bitnami.conf && \
    echo '        add_header Cross-Origin-Embedder-Policy require-corp;' >> /opt/bitnami/nginx/conf/bitnami/bitnami.conf && \
    echo '    }' >> /opt/bitnami/nginx/conf/bitnami/bitnami.conf

EXPOSE 8080