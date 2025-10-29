# 🚀 Швидкий старт - Docker + Azure Container Apps

## 📋 Завдання лабораторної роботи

1. ✅ Створити Docker образи для REST сервісу
2. ✅ Завантажити контейнери на Azure
3. ✅ Налаштувати автоматичне масштабування
4. ✅ Написати сценарій генерування навантаження
5. ✅ Запустити тест і відслідкувати масштабування

---

## 🏃 Швидке локальне тестування

### 1. Запуск через Docker Compose

```bash
# Запуск Flask API + MySQL
docker-compose up -d

# Перевірка
curl http://localhost:5000/api/docs/
```

### 2. Тестування навантаження локально

```bash
# Простий спосіб
./run_load_test.sh http://localhost:5000 10 60

# Або детальний Python скрипт
python3 load_test.py --url http://localhost:5000 --threads 10 --duration 60
```

---

## ☁️ Розгортання на Azure

### 1. Підготовка

```bash
# Вхід в Azure
az login

# Встановлення Docker (якщо потрібно)
# macOS: brew install docker
```

### 2. Налаштування змінних

Відредагуйте `azure-deploy.sh`:

```bash
# Змініть ці значення
RESOURCE_GROUP="db-repo-rg"
ACR_NAME="dbreporegistry"          # Має бути унікальним!
CONTAINER_APP_NAME="db-repo-app"

# Налаштуйте підключення до БД
DB_HOST="your-server.mysql.database.azure.com"
DB_USER="adminuser"
DB_PASSWORD="YourPassword123!"
```

### 3. Розгортання

```bash
chmod +x azure-deploy.sh
./azure-deploy.sh
```

Очікуйте 10-15 хвилин для повного розгортання.

---

## 🧪 Тестування автомасштабування

### 1. Отримайте URL вашого додатку

Після розгортання скрипт виведе URL, наприклад:
```
https://db-repo-app.nicecoast-xxxxx.westeurope.azurecontainerapps.io
```

Або знайдіть його:
```bash
az containerapp show \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --query properties.configuration.ingress.fqdn -o tsv
```

### 2. Запустіть тест навантаження

```bash
# Легке навантаження (10 потоків, 5 хвилин)
python3 load_test.py --url https://YOUR-APP-URL --threads 10 --duration 300

# Середнє навантаження (30 потоків, 10 хвилин)
python3 load_test.py --url https://YOUR-APP-URL --threads 30 --duration 600

# Важке навантаження (50 потоків, 15 хвилин)
python3 load_test.py --url https://YOUR-APP-URL --threads 50 --duration 900
```

### 3. Моніторинг масштабування

**В іншому терміналі відкрийте моніторинг:**

```bash
# Перегляд кількості реплік в реальному часі
watch -n 5 'az containerapp replica list \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --query "[].name" -o table'
```

**Або через Azure Portal:**
1. Відкрийте https://portal.azure.com
2. Знайдіть Resource Group: `db-repo-rg`
3. Відкрийте Container App: `db-repo-app`
4. Перейдіть в **Metrics** → виберіть **Replica Count**
5. Додайте метрики **CPU Usage** та **Memory Usage**

### 4. Що очікувати

| Час        | Репліки | CPU    | Опис                          |
|------------|---------|--------|-------------------------------|
| 0-2 хв     | 1       | 20-40% | Початкова фаза                |
| 2-5 хв     | 1-3     | 70%+   | Навантаження зростає          |
| 5-10 хв    | 3-8     | 60-80% | Автомасштабування активне     |
| 10-15 хв   | 5-10    | 50-70% | Стабільна робота              |
| Після тесту| 10→1    | ↓      | Масштабування вниз (2-5 хв)   |

---

## 📊 Перегляд логів та метрик

### Логи в реальному часі

```bash
az containerapp logs show \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --follow
```

### Список активних реплік

```bash
az containerapp replica list \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --output table
```

### Поточний стан масштабування

```bash
az containerapp show \
  --name db-repo-app \
  --resource-group db-repo-rg \
  --query "properties.template.scale"
```

---

## 🎯 Критерії успішного виконання

- [x] Docker образ створено та працює локально
- [x] Контейнер завантажено на Azure Container Registry
- [x] Container App розгорнуто з автомасштабуванням
- [x] Правила масштабування: CPU > 70%, Memory > 80%
- [x] Мінімум 1, максимум 10 реплік
- [x] Скрипт для генерації навантаження працює
- [ ] Зафіксовано масштабування вгору (1 → 5-10 реплік)
- [ ] Зафіксовано масштабування вниз (10 → 1 репліка)
- [ ] Збережено скріншоти метрик з Azure Portal
- [ ] Збережено логи подій масштабування

---

## 📸 Що зафіксувати для звіту

1. **Скріншоти Azure Portal:**
   - Метрики: Replica Count, CPU Usage, Memory Usage
   - Логи: Events масштабування
   - Container Apps: Список реплік під час навантаження

2. **Вивід консолі:**
   - Результати `load_test.py`
   - Вивід команди `az containerapp replica list`
   - Логи `az containerapp logs show`

3. **Файли:**
   - `load_test_results_*.txt` (автоматично створюється)
   - Скріншоти графіків з Azure Portal

---

## 🧹 Очищення після роботи

```bash
# Видалення всіх ресурсів Azure
az group delete --name db-repo-rg --yes --no-wait

# Очищення локального Docker
docker-compose down -v
docker system prune -a
```

⚠️ **Увага:** Видалення Resource Group видалить ВСІ ресурси в ньому!

---

## 📖 Детальна документація

Для детальної інформації дивіться:
- **[DOCKER_AZURE_GUIDE.md](./DOCKER_AZURE_GUIDE.md)** - повний посібник

---

## 💡 Підказки

### Якщо Container App не масштабується:

1. Збільште кількість потоків: `--threads 50`
2. Збільште тривалість: `--duration 900`
3. Перевірте метрики CPU в Azure Portal
4. Можливо потрібно понизити поріг CPU:
   ```bash
   az containerapp update \
     --name db-repo-app \
     --resource-group db-repo-rg \
     --scale-rule-metadata type=Utilization value=50
   ```

### Якщо швидкість відповіді низька:

1. Збільште ресурси контейнера:
   ```bash
   az containerapp update \
     --name db-repo-app \
     --resource-group db-repo-rg \
     --cpu 1.0 \
     --memory 2.0Gi
   ```

2. Збільште кількість workers у Gunicorn (змініть Dockerfile):
   ```dockerfile
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "app:app"]
   ```

---

## 📞 Допомога

Якщо виникли проблеми:
1. Перевірте логи: `az containerapp logs show ...`
2. Перевірте статус: `az containerapp show ...`
3. Перевірте БД підключення
4. Дивіться розділ Troubleshooting у DOCKER_AZURE_GUIDE.md

---

**Успіхів у виконанні лабораторної роботи! 🚀**

