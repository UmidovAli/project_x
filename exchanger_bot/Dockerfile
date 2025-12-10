FROM python:3.11-alpine

WORKDIR /exchanger

# Копируем requirements отдельно для кэширования
COPY requirements.txt .

# Устанавливаем только необходимые системные зависимости
RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

COPY . /exchanger

CMD ["python", "main.py"]