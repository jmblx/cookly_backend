---

## Установка зависимостей 

### uv:
```shell
pip install uv
```

### Рабочие зависимости:

#### Windows:
```shell
cd backend
uv venv .venv
.venv\Scripts\activate
uv pip install -e .
```

#### Linux/macOS:
```shell
cd backend
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

### Для разработки backend:
```shell
uv pip install -e ".[dev]"
```

---

## Запуск для локальной разработки

В корне проекта можно использовать:

```bash
make run
```

Эта команда запускает Gunicorn с `uvicorn.workers.UvicornWorker` и считывает параметры из конфигурационного файла (`config.toml`).  
Используется `main:app` из FastAPI.

> ⚠️ Для Windows вместо `make` можно запускать эквивалентную команду вручную:
> ```bash
> uvicorn main:app --reload
> ```

---

## Конфигурация `config.toml`

```toml
[global]
debug = false
secret = "fakesecret"

[gunicorn]
bind = "0.0.0.0:8080"
workers = 2
timeout = 30
worker_class = "uvicorn.workers.UvicornWorker"

[database]
host = "localhost"
port = "5432"
name = "cookly"
user = "postgres"
password = "postgres"

[redis]
host = "localhost"
port = 6379

[smtp]
smtp_password = "aaaa bbbb cccc dddd"
smtp_user = "cooklyservice@gmail.com"
smtp_host = "smtp.gmail.com"
smtp_port = 465

[admin]
admin_passwords = "support@mail.ru"
admin_emails = "youradminpswd"

[jwt]
public_key_path = "/home/user/cookly_backend/сerts/jwt-public.pem"
algorithm = "RS512"

[auth_core]
api_url = "http://auth_service:8000"

[minio]
endpoint_url = "minio:9000"
access_key = "login"
secret_key = "password"
user_avatar_bucket_name = "user-avatars"
recipe_bucket_name = "recipes"
recipe_step_bucket_name = "recipe-steps"
alias = "myminio"
url = "http://myminio.url"

[ollama]
url = "http://host.docker.internal:11434"
model = "qwen3:4b-instruct"
timeout = 60

```

---