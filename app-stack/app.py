#!/usr/bin/env python3

import random
import threading
import time
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, make_asgi_app

app = FastAPI()

# [METRICS] Эндпоинт для сбора метрик Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# [COUNTER] Общий счетчик запросов
HTTP_REQUESTS_TOTAL = Counter(
    "app_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint"]
)

# [GAUGE] Имитация текущей загрузки памяти (может расти и падать)
# [BEST PRACTICE] Храним значения в БАЗОВЫХ единицах (байты).
# Grafana сама умеет конвертировать их в MB/GB при отображении.
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
        MEMORY_USAGE_BYTES.set(val_bytes)
        time.sleep(5)

# Запускаем симуляцию в отдельном потоке
threading.Thread(target=simulate_system_load, daemon=True).start()

@app.get("/hello")
def hello():
    HTTP_REQUESTS_TOTAL.labels(method="GET", endpoint="/hello").inc()
    return {"message": "Hello, Prometheus!"}

@app.get("/info")
def info():
    HTTP_REQUESTS_TOTAL.labels(method="GET", endpoint="/info").inc()
    return {"message": "App is running and simulating metrics"}