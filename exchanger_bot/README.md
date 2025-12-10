ПОСЛЕ КЛОНИРОВАНИЯ РЕПО

ПИШЕМ В ТЕРМИНАЛ - 
    pip install -r requirements.txt 

Дальше входим в ДОКЕР - 
    docker login

Дальше билдим образ нашего бота в ДОКЕР - 
    docker build --no-cache -t exchange_bot:1 . 

Потом копируем id нашего образа
    docker images
    ...ищем наш образ, копируем его IMAGE ID

Запускам контейнер с указанием env-файла
    docker run --name exchanger_cont --env-file .env <image_id>

!!!!!!!!!!!!! В А Ж Н О !!!!!!!!!!!!!!!!!

Не забудьте перед всем этим развернуть сервер Postgres на своем компе
и указать актуальные для вас данные в .env файле

УДАЧИ!

