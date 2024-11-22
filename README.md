# Foodgragm - социальная сеть для обмена рецептами.

[![Main foodgram workflow](https://github.com/zaphire12/foodgram/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/zaphire12/foodgram/actions/workflows/main.yml)


## Проект «Фудграм» представляет собой веб-платформу, где пользователи могут делиться своими рецептами, добавлять понравившиеся рецепты других авторов в избранное и подписываться на обновления любимых кулинаров. Зарегистрированные участники также получают доступ к удобному сервису «Список покупок», который автоматически формирует перечень необходимых ингредиентов для выбранных блюд.

1. Склонируйте репозиторий на свой компьютер:
    ```
    git clone git@github.com:zaphire12/foodgram.git
    ```
2. Создайте файл `.env` и заполните его своими данными. Все необходимые переменные перечислены в файле `.env.example`, находящемся в корневой директории проекта.

    ```
    DATABASES                  # база данных используема при работе приложения (postgresql/sqlite3)
    POSTGRES_DB                # имя базы
    POSTGRES_USER              # пользователь бд
    POSTGRES_PASSWORD          # пароль пользователя
    DB_HOST                    # хост бд
    DB_PORT                    # порт
    DEBUG                      # булевое значение дебага, для отладки
    SECRET_KEY                 # секретный ключ
    ALLOWED_HOSTS              # доступные хосты (localhost 127.0.0.1 по умолчанию. Указывать в виде localhost,127.0.0.1)
    ``` 

> Далее в проекте мы используем Docker и Docker Compose. Прежде чем начать, убедитесь, что Docker и Docker Compose установлены на вашем компьютере. Если они не установлены, выполните установку Docker согласно официальным инструкциям.

### Создание Docker-образов

> Далее в проекте мы используем Docker и Docker Compose. Прежде чем начать, убедитесь, что Docker и Docker Compose установлены на вашем компьютере. Если они не установлены, выполните установку Docker согласно официальным инструкциям.

1. Замените `username` на свой логин на DockerHub:

    ```
    cd frontend   
    docker build -t username/foodgram_frontend .
    cd ../backend
    docker build -t username/foodgram_backend .
    cd ../nginx
    docker build -t username/foodgram_gateway . 
    ```

2. Загрузите образы на DockerHub:

    ```
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    docker push username/foodgram_gateway
    ```
   
### Деплой на сервер

1. Подключитесь к удаленному серверу
Подключение можно настроить в конфигурационном файле по пути ~/.ssh/config
```
Host remotehost.yourcompany.com
    User yourname
    HostName another-host-fqdn-or-ip-goes-here
    IdentityFile ~/.ssh/id_rsa-remote-ssh
```
или использовать команду 
    ```
    ssh -i path_to_ssh/ssh_key username@host 
    ```
2. Создайте на сервере директорию `kittygram`:

    ```
    mkdir foodgram
    ```
3. Скопируйте файлы `docker-compose.production.yml` и `.env` в директорию `foodgram/` на сервере:

    ```
    scp -i path_to_ssh/ssh_key docker-compose.production.yml username@host:/home/{host}/kittygram/docker-compose.production.yml
    ```
    
    Где:
    - `path_to_ssh` - путь к файлу с вашим SSH-ключом
    - `ssh_key` - имя файла с вашим SSH-ключом
    - `username` - ваше имя пользователя на сервере
    - `host` - IP-адрес вашего сервера

> Не забудьте поменять название образов в [docker-compose.production.yml](docker-compose.production.yml)

### Настройка CI/CD

1. Файл workflow уже написан и находится в директории:

    ```
    foodgram/.github/workflows/main.yml
    ```

2. Для адаптации его к вашему серверу добавьте секреты в GitHub Actions:

    ```
    DOCKER_USERNAME                # имя пользователя в DockerHub
    DOCKER_PASSWORD                # пароль пользователя в DockerHub
    HOST                           # IP-адрес сервера
    USER                           # имя пользователя
    SSH_KEY                        # содержимое приватного SSH-ключа (cat ~/.ssh/privat_key)
    SSH_PASSPHRASE                 # пароль для SSH-ключа

    TELEGRAM_TO                    # ID вашего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
    TELEGRAM_TOKEN                 # токен вашего бота
    ```