#!/usr/bin/env python3

# [IMPORT] Импортируем модуль 'random' из стандартной библиотеки.
# Нужен для генерации случайных чисел (симуляция нагрузки).
import random

# [IMPORT] Импортируем модуль 'threading' из стандартной библиотеки.
# Нужен для создания параллельных потоков (чтобы симуляция не блокировала веб-сервер).
import threading

# [IMPORT] Импортируем модуль 'time' из стандартной библиотеки.
# Нужен для пауз (sleep) в цикле симуляции.
import time

# [IMPORT] Импортируем класс 'FastAPI' из внешней библиотеки 'fastapi'.
# Это основной класс для создания веб-приложения.
from fastapi import FastAPI

# [IMPORT] Импортируем классы 'Counter', 'Gauge' и функцию 'make_asgi_app' из внешней библиотеки 'prometheus_client'.
# Counter - для счетчиков (только вверх), Gauge - для измерителей (вверх/вниз).
# make_asgi_app - создает специальное мини-приложение для отдаче метрик.
from prometheus_client import Counter, Gauge, make_asgi_app

# [INSTANCE] Создаем экземпляр класса FastAPI.
# Переменная 'app' становится главным объектом нашего приложения, к которому мы будем всё подключать.
app = FastAPI()

# [FUNCTION CALL] Создаем отдельное ASGI-приложение для метрик, вызывая функцию make_asgi_app().
# Оно умеет отвечать на запросы в формате, понятном Prometheus.
metrics_app = make_asgi_app()

# [METHOD CALL] Монтируем (подключаем) приложение metrics_app к нашему главному приложению 'app'.
# Теперь по адресу /metrics будет отвечать код из библиотеки prometheus_client.
app.mount("/metrics", metrics_app)

# [INSTANCE] Создаем экземпляр класса Counter.
# Это глобальная переменная, хранящая состояние счетчика запросов.
HTTP_REQUESTS_TOTAL = Counter(
    "app_http_requests_total",      # Имя метрики: уникальный идентификатор в системе Prometheus
    "Total number of HTTP requests", # Описание: краткое пояснение назначения метрики (Help text)
    ["method", "endpoint"]          # Метки (Labels): список измерений для группировки и фильтрации данных
)

# [INSTANCE] Создаем экземпляр класса Gauge.
# Это глобальная переменная, хранящая текущее значение "использованной памяти".
MEMORY_USAGE_BYTES = Gauge(
    "app_memory_usage_bytes",        # Имя метрики: под этим именем данные будут в Prometheus
    "Current memory usage in Bytes (Simulated)" # Описание: пояснение, что измеряет данный Gauge
)

# [FUNCTION DEFINITION] Объявляем функцию simulate_system_load.
# Она будет выполняться бесконечно в фоне.
def simulate_system_load():
    """Функция симуляции нагрузки для демонстрации работы Gauge."""
    # [LOOP] Запускаем бесконечный цикл.
    while True:
        # [FUNCTION CALL] Генерируем случайное число от 128 до 1024.
        random_mb = random.uniform(128, 1024)
        
        # [CALCULATION] Переводим мегабайты в байты (умножаем на 1024 дважды).
        val_bytes = random_mb * 1024 * 1024
        
        # [METHOD CALL] Вызываем метод .set() у объекта Gauge (MEMORY_USAGE_BYTES).
        # Это обновляет значение метрики на вычисленное число байт.
        MEMORY_USAGE_BYTES.set(val_bytes)
        
        # [FUNCTION CALL] Приостанавливаем выполнение этого потока на 5 секунд.
        time.sleep(5)

# [INSTANCE & METHOD CALL] Создаем и запускаем поток.
# threading.Thread() создает объект потока, которому мы передаем нашу функцию simulate_system_load.
# daemon=True означает, что поток закроется сам, если основная программа остановится.
# .start() запускает выполнение потока.
threading.Thread(target=simulate_system_load, daemon=True).start()

# [DECORATOR] Используем декоратор @app.get("/hello").
# Он говорит FastAPI: "когда придет GET-запрос на адрес /hello, выполни функцию ниже".
@app.get("/hello")
# [FUNCTION DEFINITION] Объявляем функцию обработки запроса hello.
def hello():
    # [METHOD CALL] Обращаемся к объекту счетчика HTTP_REQUESTS_TOTAL.
    # .labels() выбирает конкретный счетчик для указанных параметров (GET, /hello).
    # .inc() увеличивает значение этого счетчика на 1.
    HTTP_REQUESTS_TOTAL.labels(method="GET", endpoint="/hello").inc()
    
    # [RETURN] Возвращаем словарь, который FastAPI автоматически превратит в JSON-ответ.
    return {"message": "Hello, Prometheus!"}

# [DECORATOR] Регистрируем обработчик для пути /info.
@app.get("/info")
# [FUNCTION DEFINITION] Объявляем функцию обработки запроса info.
def info():
    # [METHOD CALL] Увеличиваем счетчик, но уже с меткой endpoint="/info".
    # В Prometheus это будет выглядеть как отдельная временная шкала.
    HTTP_REQUESTS_TOTAL.labels(method="GET", endpoint="/info").inc()
    
    # [RETURN] Возвращаем JSON-ответ.
    return {"message": "App is running and simulating metrics"}