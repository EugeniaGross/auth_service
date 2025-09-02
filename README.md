# Микросервис для аутентификации
###### Подготовка сервиса к запуску
Создать приватный и публичный ключи
```
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
```
В корневой папке проекта создать файл .env. Пример содержания .env:</br>
```
JWT_ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 7

ALLOWED_HOSTS_STRING=localhost,127.0.0.1
ORIGINS_STRING=http://localhost:5173

TEST_ALLOWED_HOSTS_STRING=test
TEST_ORIGINS_STRING=http://test

POSTGRES_PORT=5432
POSTGRES_DB=resumes
POSTGRES_USER=resumes
POSTGRES_PASSWORD=resumes
POSTGRES_HOST=localhost

PRIVATE_KEY_PATH = <path/to/private.pem>
PUBLIC_KEY_PATH = <path/to/public.pem>

TESTING = 1 # указывается при проведении тестирования
```

###### Запуск проекта c помошью docker compose: </br>
```
docker compose up --build
```
###### Запуск проекта без docker compose (Windows): </br>
```
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cd application
uvicorn main:app --reload
```
Запуск проекта без docker compose (Linux, MacOS): </br>
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd application
uvicorn main:app --reload
```
