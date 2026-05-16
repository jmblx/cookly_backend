FROM openresty/openresty:jammy

RUN luarocks install lua-resty-jwt

RUN rm -f /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]