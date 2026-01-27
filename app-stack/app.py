#!/usr/bin/env python3

import random
import threading
import time
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, make_asgi_app

app = FastAPI()

# [METRICS] Эндпоинт для сбора метрик Prometheus
# Prometheus (scraper) будет опрашивать этот путь (/metrics) с заданным интервалом.
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# [COUNTER] Общий счетчик запросов.
# Тип Counter: монотонно возрастающая величина (только вверх). Сброс при рестарте.
# Использование: подсчет количества событий (запросы, ошибки, отправленные письма).
# Для получения скорости (RPS) используется функция rate() в PromQL.
HTTP_REQUESTS_TOTAL = Counter(
    "app_http_requests_total",      # Уникальное имя метрики
    "Total number of HTTP requests", # Описание
    ["method", "endpoint"]          # Labels: измерения для сегментации (GROUP BY)
)

# [GAUGE] Измеритель значений (может расти и падать).
# Тип Gauge: снимок состояния в момент времени.
# Использование: загрузка RAM/CPU, размер очереди, температура, кол-во активных потоков.
MEMORY_USAGE_BYTES = Gauge(
    "app_memory_usage_bytes",
    "Current memory usage in Bytes (Simulated)"
)

# [BACKGROUND] Функция для симуляции изменения метрик в реальном времени
def simulate_system_load():
    while True:
        # Генерируем случайное значение от 128 до 1024 МБ и переводим в байты
        random_mb = random.uniform(128, 1024)
        val_bytes = random_mb * 1024 * 1024
        
        # .set() устанавливает конкретное текущее значение для Gauge
        MEMORY_USAGE_BYTES.set(val_bytes)
        time.sleep(5)

# Запускаем симуляцию в отдельном потоке
threading.Thread(target=simulate_system_load, daemon=True).start()

@app.get("/hello") # метод библиотеки FastAPI когда придет запрос на /hello, запускает функцию
def hello():
    # Инкремент счетчика (увеличиваем на 1).
    # Обязательно указываем все labels, заданные при объявлении метрики.
    HTTP_REQUESTS_TOTAL.labels(method="GET", endpoint="/hello").inc()
    return {"message": "Hello, Prometheus!"}

@app.get("/info") # метод библиотеки FastAPI когда придет запрос на /info, запускает функцию
def info():
    # Благодаря метке endpoint="/info", мы сможем отделить этот трафик от /hello
    # и построить отдельные графики нагрузки для каждой ручки.
    HTTP_REQUESTS_TOTAL.labels(method="GET", endpoint="/info").inc()
    return {"message": "App is running and simulating metrics"}
