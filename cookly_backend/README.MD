# Cookly app

### Аутентификация через [кастомный OpenID провайдер](https://github.com/jmblx/OpenID-provider)

### Общий стек бэка:

PostgreSQL, Grafana, NGINX, Docker Compose, Python

### Для работы необходимы сертификаты публичный и приватный от openssl в ./certs:

```
cd ./certs
openssl genrsa -out private_key_rs512.pem 4096
openssl rsa -in private_key_rs512.pem -pubout -out public_key_rs512.pem
```

### Далее заполнить:
- .env файл по аналогии с ./env-dist
- ./recipe_backend/config.toml по шаблону в ./recipe_backend/config.template.toml

Докуменатация по разработке в соответствующих папках проекта.
