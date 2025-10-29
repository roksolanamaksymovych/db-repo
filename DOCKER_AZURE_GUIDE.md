# 🐳 Керівництво з Docker та Azure Container Apps

## Зміст

1. [Огляд](#огляд)
2. [Структура файлів](#структура-файлів)
3. [Локальне тестування з Docker](#локальне-тестування-з-docker)
4. [Розгортання на Azure Container Apps](#розгортання-на-azure-container-apps)
5. [Тестування автомасштабування](#тестування-автомасштабування)
6. [Моніторинг та логи](#моніторинг-та-логи)

---

## Огляд

Цей проект налаштований для розгортання Flask REST API у Docker контейнерах з автоматичним масштабуванням на Azure Container Apps.

### Основні можливості:

- ✅ Docker контейнеризація Flask API
- ✅ Docker Compose для локального тестування
- ✅ Автоматичне розгортання на Azure
- ✅ Автомасштабування за CPU/Memory
- ✅ Інструменти для тестування навантаження

---

## Структура файлів

```
db-repo/
├── Dockerfile                  # Docker образ для Flask API
├── docker-compose.yml          # Локальна композиція (Flask + MySQL)
├── .dockerignore              # Файли які не потрапляють в образ
├── azure-deploy.sh            # Скрипт розгортання на Azure
├── load_test.py               # Python скрипт для тестування навантаження
├── run_load_test.sh           # Швидкий запуск тесту навантаження
└── DOCKER_AZURE_GUIDE.md      # Ця документація
```

---

## Локальне тестування з Docker

### Передумови

- Docker Desktop встановлено
- Docker Compose встановлено

### Крок 1: Створення .env файлу (опціонально)

```bash
cat > .env << EOF
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=database_lab1_eer
EOF
```

### Крок 2: Запуск контейнерів

```bash
# Запуск в фоновому режимі
docker-compose up -d

# Перегляд логів
docker-compose logs -f

# Перегляд статусу
docker-compose ps
```

### Крок 3: Перевірка роботи

Відкрийте браузер:

- API: http://localhost:5000
- Swagger документація: http://localhost:5000/api/docs/

### Крок 4: Тестування API

```bash
# GET запит до користувачів
curl http://localhost:5000/api/users

# GET запит до категорій
curl http://localhost:5000/api/categories

# POST створення користувача
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"Name": "Test User", "email": "test@example.com", "phone": "+380123456789"}'
```

### Крок 5: Зупинка контейнерів

```bash
# Зупинка
docker-compose stop

# Зупинка та видалення контейнерів
docker-compose down

# Видалення контейнерів та volumes
docker-compose down -v
```

---

## Розгортання на Azure Container Apps

### Передумови

1. **Azure CLI встановлено:**

```bash
# macOS
brew install azure-cli

# Або завантажте з: https://docs.microsoft.com/cli/azure/install-azure-cli
```

2. **Docker встановлено та запущено**

3. **Azure підписка активна**

### Крок 1: Вхід в Azure

```bash
az login
```

### Крок 2: Налаштування змінних в скрипті

Відредагуйте файл `azure-deploy.sh` і змініть наступні змінні:

```bash
RESOURCE_GROUP="db-repo-rg"              # Ваша resource group
LOCATION="westeurope"                     # Регіон Azure
ACR_NAME="dbreporegistry"                # Ім'я Container Registry (має бути унікальним)
CONTAINER_APP_NAME="db-repo-app"        # Ім'я Container App
CONTAINER_APP_ENV="db-repo-env"          # Ім'я середовища

# База даних (використовуйте існуючу Azure MySQL або змініть)
DB_HOST="your-mysql-server.mysql.database.azure.com"
DB_USER="adminuser"
DB_PASSWORD="YourPassword123!"
DB_NAME="database_lab1_eer"
```

### Крок 3: Запуск розгортання

```bash
# Надання прав на виконання
chmod +x azure-deploy.sh

# Запуск скрипту
./azure-deploy.sh
```

Скрипт виконає наступні дії:

1. ✅ Створить Resource Group
2. ✅ Створить Azure Container Registry (ACR)
3. ✅ Побудує Docker образ
4. ✅ Завантажить образ в ACR
5. ✅ Створить Container Apps Environment
6. ✅ Розгорне Container App з автомасштабуванням
7. ✅ Налаштує правила масштабування (CPU > 70%, Memory > 80%)

### Крок 4: Перевірка розгортання

Після успішного розгортання ви отримаєте URL:

```
https://db-repo-app.nicecoast-xxxxxxxx.westeurope.azurecontainerapps.io
```

Перевірте:

- API: `https://your-app-url.azurecontainerapps.io/api/users`
- Swagger: `https://your-app-url.azurecontainerapps.io/api/docs/`

---

## Тестування автомасштабування

### Метод 1: Використання load_test.py

Повнофункціональний Python скрипт з детальною статистикою:

```bash
# Локальне тестування
python3 load_test.py --url http://localhost:5000 --threads 10 --duration 300

# Тестування на Azure (легке навантаження)
python3 load_test.py --url https://your-app.azurecontainerapps.io --threads 20 --duration 600

# Тестування на Azure (важке навантаження)
python3 load_test.py --url https://your-app.azurecontainerapps.io --threads 50 --duration 900
```

**Параметри:**

- `--url`: URL вашого API
- `--threads`: Кількість паралельних потоків (рекомендується 10-50)
- `--duration`: Тривалість тесту в секундах (рекомендується 300-900)

**Вивід:**

- Реал-тайм статистика кожні 10 секунд
- Детальна статистика наприкінці
- Результати зберігаються у файл `load_test_results_YYYYMMDD_HHMMSS.txt`

### Метод 2: Використання run_load_test.sh

Простий інтерактивний скрипт:

```bash
chmod +x run_load_test.sh

# Інтерактивний режим
./run_load_test.sh

# З параметрами
./run_load_test.sh https://your-app.azurecontainerapps.io 30 600
```

### Очікувані результати

При правильному налаштуванні ви побачите:

1. **Початкова фаза (0-60 сек):**
   - 1 активний екземпляр
   - CPU використання зростає
2. **Масштабування вгору (60-180 сек):**
   - CPU досягає >70% або Memory >80%
   - Azure запускає додаткові екземпляри (2-10)
   - Час відповіді стабілізується
3. **Стабільна робота (180-600 сек):**
   - Кілька екземплярів обробляють запити
   - Навантаження розподіляється
4. **Масштабування вниз (після завершення тесту):**
   - Через 2-5 хвилин після зменшення навантаження
   - Azure зменшує кількість екземплярів до мінімуму

---

## Моніторинг та логи

### Моніторинг через Azure Portal

1. Відкрийте [Azure Portal](https://portal.azure.com)
2. Знайдіть вашу Container App: `db-repo-app`
3. Перейдіть в розділ **Metrics**

**Основні метрики:**

- **CPU Usage** - використання процесора
- **Memory Usage** - використання пам'яті
- **Replica Count** - кількість запущених екземплярів
- **Requests** - кількість запитів
- **Request Duration** - час обробки запитів

### Перегляд логів

**Через Azure CLI:**

```bash
# Логи Container App
az containerapp logs show \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --follow

# Логи всіх реплік
az containerapp logs show \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --type console \
  --follow
```

**Через Azure Portal:**

1. Container App → **Log stream**
2. Container App → **Logs** → Query logs з Log Analytics

### Корисні Azure CLI команди

```bash
# Статус Container App
az containerapp show \
  --name db-repo-app \
  --resource-group db-repo-rg

# Список реплік
az containerapp replica list \
  --name db-repo-app \
  --resource-group db-repo-rg

# Ручне масштабування (для тестування)
az containerapp update \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --min-replicas 2 \
  --max-replicas 10

# Перегляд правил масштабування
az containerapp show \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --query properties.template.scale
```

### Приклад запиту Log Analytics

```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "db-repo-app"
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
| take 100
```

---

## Налаштування автомасштабування

### Поточні правила

Згідно зі скриптом `azure-deploy.sh`:

- **Мінімум реплік:** 1
- **Максимум реплік:** 10
- **CPU правило:** масштабування при використанні > 70%
- **Memory правило:** масштабування при використанні > 80%

### Зміна правил масштабування

**1. Зміна кількості реплік:**

```bash
az containerapp update \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --min-replicas 2 \
  --max-replicas 20
```

**2. Зміна порогу CPU:**

```bash
az containerapp update \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --scale-rule-name cpu-scaling \
  --scale-rule-type cpu \
  --scale-rule-metadata type=Utilization value=60
```

**3. Додавання правила на основі HTTP запитів:**

```bash
az containerapp update \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --scale-rule-name http-scaling \
  --scale-rule-type http \
  --scale-rule-metadata concurrentRequests=50
```

**4. Видалення правила:**

```bash
az containerapp update \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --remove properties.template.scale.rules[0]
```

---

## Troubleshooting

### Проблема: Контейнер не запускається локально

```bash
# Перевірка логів
docker-compose logs flask-app

# Перезапуск контейнерів
docker-compose down
docker-compose up --build
```

### Проблема: Не можу підключитися до MySQL

```bash
# Перевірка чи запущений MySQL
docker-compose ps

# Перевірка логів MySQL
docker-compose logs mysql

# Підключення до MySQL для діагностики
docker-compose exec mysql mysql -u root -p
```

### Проблема: Образ не завантажується в ACR

```bash
# Перевірка автентифікації
az acr login --name dbreporegistry

# Перевірка існування образу
az acr repository list --name dbreporegistry

# Ручна побудова та push
docker build -t dbreporegistry.azurecr.io/flask-rest-api:latest .
docker push dbreporegistry.azurecr.io/flask-rest-api:latest
```

### Проблема: Container App не масштабується

1. Перевірте метрики CPU/Memory в Azure Portal
2. Переконайтеся що навантаження достатнє (>70% CPU)
3. Перевірте логи масштабування:

```bash
az monitor activity-log list \
  --resource-group db-repo-rg \
  --max-events 50
```

---

## Очищення ресурсів

### Видалення всього Resource Group

```bash
az group delete --name db-repo-rg --yes --no-wait
```

### Видалення лише Container App

```bash
az containerapp delete \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --yes
```

### Локальне очищення Docker

```bash
# Видалення контейнерів
docker-compose down -v

# Очищення образів
docker system prune -a
```

---

## Корисні посилання

- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps/)
- [Docker Documentation](https://docs.docker.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

## Автор

Лабораторна робота з розгортання REST сервісу у Docker контейнерах з автомасштабуванням на Azure Container Apps.

**Дата:** 2025

---

## Ліцензія

Цей проект створено для освітніх цілей.
