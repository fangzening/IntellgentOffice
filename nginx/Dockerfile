FROM nginx:1.19.0-alpine

RUN rm /etc/nginx/conf.d/default.conf
#RUN curl -L https://raw.githubusercontent.com/wmnnd/nginx-certbot/master/init-letsencrypt.sh > init-letsencrypt.sh
#RUN ./init-letsencrypt.sh
COPY nginx.conf /etc/nginx/conf.d
COPY ssl /