#!/usr/bin/env python3

# [IMPORT] Импорт модуля 'random' из стандартной библиотеки.
# Генерация случайных чисел (симуляция нагрузки).
import random

# [IMPORT] Импорт модуля 'threading' из стандартной библиотеки.
# Создание параллельных потоков (предотвращение блокировки веб-сервера симуляцией).
import threading

# [IMPORT] Импорт модуля 'time' из стандартной библиотеки.
# Организация пауз (sleep) в цикле симуляции.
import time

# [IMPORT] Импорт класса 'FastAPI' из внешней библиотеки 'fastapi'.
# Основной класс для создания веб-приложения.
from fastapi import FastAPI

# [IMPORT] Импорт классов 'Counter', 'Gauge' и функции 'make_asgi_app' из внешней библиотеки 'prometheus_client'.
# Counter - для счетчиков (только вверх), Gauge - для измерителей (вверх/вниз).
# make_asgi_app - создание специального мини-приложения для отдачи метрик.
from prometheus_client import Counter, Gauge, make_asgi_app

# [INSTANCE] Создание экземпляра класса FastAPI.
# Инициализация главного объекта приложения 'app' для подключения компонентов.
app = FastAPI()

# [FUNCTION CALL] Создание отдельного ASGI-приложения для метрик вызовом make_asgi_app().
# Обработка запросов в формате Prometheus.
metrics_app = make_asgi_app()

# [METHOD CALL] Монтирование (подключение) приложения metrics_app к главному приложению 'app'.
# Обеспечение ответа кода библиотеки prometheus_client по адресу /metrics.
app.mount("/metrics", metrics_app)

# [INSTANCE] Создание экземпляра класса Counter.
# Глобальная переменная для хранения состояния счетчика запросов.
HTTP_REQUESTS_TOTAL = Counter(
    "app_http_requests_total",      # Имя метрики: уникальный идентификатор в системе Prometheus
    "Total number of HTTP requests", # Описание: краткое пояснение назначения метрики (Help text)
    ["method", "endpoint"]          # Метки (Labels): список измерений для группировки и фильтрации данных
)

# [INSTANCE] Создание экземпляра класса Gauge.
# Глобальная переменная для хранения текущего значения "использованной памяти".
MEMORY_USAGE_BYTES = Gauge(
    "app_memory_usage_bytes",        # Имя метрики: под этим именем данные будут в Prometheus
    "Current memory usage in Bytes (Simulated)" # Описание: пояснение, что измеряет данный Gauge
)

# [FUNCTION DEFINITION] Объявление функции simulate_system_load.
# Бесконечное выполнение в фоне.
def simulate_system_load():
    """Функция симуляции нагрузки для демонстрации работы Gauge."""
    # [LOOP] Запуск бесконечного цикла.
    while True:
        # [FUNCTION CALL] Генерация случайного числа от 128 до 1024.
        random_mb = random.uniform(128, 1024)
        
        # [CALCULATION] Перевод мегабайт в байты (двойное умножение на 1024).
        val_bytes = random_mb * 1024 * 1024
        
        # [METHOD CALL] Вызов метода .set() у объекта Gauge (MEMORY_USAGE_BYTES).
        # Обновление значения метрики на вычисленное число байт.
        MEMORY_USAGE_BYTES.set(val_bytes)
        
        # [FUNCTION CALL] Приостановка выполнения потока на 5 секунд.
        time.sleep(5)

# [INSTANCE & METHOD CALL] Создание и запуск потока.
# threading.Thread() - создание объекта потока с передачей функции simulate_system_load.
# daemon=True - автоматическое закрытие потока при остановке основной программы.
# .start() - запуск выполнения потока.
threading.Thread(target=simulate_system_load, daemon=True).start()

# [DECORATOR] Использование декоратора @app.get("/hello").
# Указание FastAPI выполнить функцию ниже при поступлении GET-запроса на /hello.
@app.get("/hello")
# [FUNCTION DEFINITION] Объявление функции обработки запроса hello.
def hello():
    # [METHOD CALL] Обращение к объекту счетчика HTTP_REQUESTS_TOTAL.
    # .labels() - выбор конкретного счетчика для параметров (GET, /hello).
    # .inc() - увеличение значения счетчика на 1.
    HTTP_REQUESTS_TOTAL.labels(method="GET", endpoint="/hello").inc()
    
    # [RETURN] Возврат словаря для автоматического преобразования в JSON-ответ средствами FastAPI.
    return {"message": "Hello, Prometheus!"}

# [DECORATOR] Регистрация обработчика для пути /info.
@app.get("/info")
# [FUNCTION DEFINITION] Объявление функции обработки запроса info.
def info():
    # [METHOD CALL] Увеличение счетчика с меткой endpoint="/info".
    # Отображение в Prometheus как отдельной временной шкалы.
    HTTP_REQUESTS_TOTAL.labels(method="GET", endpoint="/info").inc()
    
    # [RETURN] Возврат JSON-ответа.
    return {"message": "App is running and simulating metrics"}
