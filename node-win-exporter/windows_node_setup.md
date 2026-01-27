# Подключение Windows-хоста к мониторингу (windows_exporter)

Для сбора метрик с Windows (CPU, RAM, Disk, Network, IIS, AD и др.) используется **windows_exporter**.

---

## 1. Установка агента (windows_exporter)

### Вариант А: Быстрая установка (MSI)
1. Скачать актуальный релиз `.msi` с [GitHub репозитория](https://github.com/prometheus-community/windows_exporter/releases).
2. Запустить установщик.
3. По умолчанию экспортер слушает порт **9182**.

### Вариант Б: Установка через PowerShell (Automation)
Рекомендуемый метод для воспроизводимости. Позволяет сразу выбрать нужные коллекторы.

```powershell
# Скачиваем MSI (замените версию на актуальную)
Invoke-WebRequest -Uri https://github.com/prometheus-community/windows_exporter/releases/download/v0.25.1/windows_exporter-0.25.1-amd64.msi -OutFile windows_exporter.msi

# Устанавливаем сервис
# ENABLED_COLLECTORS: список метрик (cpu,cs,logical_disk,net,os,service,system,textfile)
# LISTEN_ADDR: адрес и порт (0.0.0.0:9182)
msiexec /i windows_exporter.msi ENABLED_COLLECTORS="cpu,cs,logical_disk,net,os,service,system" LISTEN_ADDR="0.0.0.0:9182" /qn
```

---

## 2. Настройка Firewall

Необходимо открыть порт **9182** для входящих подключений от сервера Prometheus.

```powershell
New-NetFirewallRule -DisplayName "Prometheus windows_exporter" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 9182
```

---

## 3. Проверка

1. Откройте в браузере: `http://<IP-адрес-windows-хоста>:9182/metrics`
2. Вы должны увидеть список метрик (например, `windows_cpu_time_total`).

---

## 4. Добавление в Prometheus

Добавьте новую job в `prometheus.yml` на сервере мониторинга:

```yaml
scrape_configs:
  - job_name: 'windows-node'
    static_configs:
      - targets: ['<IP-адрес-windows-хоста>:9182']
        labels:
          os: 'windows'
          env: 'production'
```

Перезагрузите конфигурацию Prometheus: `curl -X POST http://localhost:9090/-/reload` или перезапустите контейнер.
