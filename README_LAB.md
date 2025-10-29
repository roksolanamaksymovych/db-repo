# 📚 Лабораторна робота: Docker + Azure Container Apps

## ✅ Що вже зроблено

### 1. Docker конфігурація

- ✅ `Dockerfile` - образ для Flask REST API
- ✅ `docker-compose.yml` - локальне тестування з MySQL
- ✅ `.dockerignore` - оптимізація розміру образу

### 2. Azure розгортання

- ✅ `azure-deploy.sh` - автоматичне розгортання на Azure Container Apps
- ✅ Налаштовано автомасштабування (CPU > 70%, Memory > 80%)
- ✅ Мінімум 1, максимум 10 реплік

### 3. Тестування навантаження

- ✅ `load_test.py` - Python скрипт для генерації навантаження
- ✅ `run_load_test.sh` - швидкий запуск тестів

### 4. Допоміжні інструменти

- ✅ `check-acr-name.sh` - перевірка доступності імені ACR
- ✅ `azure-status.sh` - швидка перевірка статусу
- ✅ `TROUBLESHOOTING.md` - вирішення проблем

### 5. Документація

- ✅ `QUICKSTART.md` - швидкий старт
- ✅ `DOCKER_AZURE_GUIDE.md` - повний посібник
- ✅ `TROUBLESHOOTING.md` - вирішення проблем

---

## 🚀 Наступні кроки

### Крок 1: Виберіть унікальне ім'я для ACR

Проблема яку ви зіткнулися - ім'я `dbreporegistry` вже зайняте глобально.

```bash
# Перевірте доступність нового імені
./check-acr-name.sh dbreporoksolana2025

# Або згенеруйте унікальне
./check-acr-name.sh dbrepo$(date +%s | tail -c 6)
```

### Крок 2: Оновіть azure-deploy.sh

Відредагуйте файл `azure-deploy.sh`, знайдіть рядок 33 та змініть:

```bash
ACR_NAME="вашеунікальнеімя"  # Замініть на доступне ім'я з Кроку 1
```

### Крок 3: Запустіть розгортання

```bash
# Переконайтеся що Docker Desktop запущено
docker ps

# Запустіть розгортання
./azure-deploy.sh
```

Це займе **10-15 хвилин**. Скрипт автоматично:

- Зареєструє необхідні resource providers
- Створить ACR з вашим унікальним іменем
- Побудує та завантажить Docker образ
- Створить Container App з автомасштабуванням

### Крок 4: Перевірте розгортання

```bash
# Швидка перевірка статусу
./azure-status.sh

# Або в Azure Portal
open https://portal.azure.com
```

### Крок 4.5: Додайте тестові дані (якщо база порожня)

Якщо Swagger показує порожні списки:

```bash
# Отримайте URL вашого додатку
APP_URL=$(cat .env.azure | grep APP_URL | cut -d'=' -f2)

# Або вручну встановіть
APP_URL="https://your-app-url.azurecontainerapps.io"

# Додайте тестові дані
python3 add_test_data.py $APP_URL
```

Це додасть:

- 3 тестових користувачів
- 3 категорії
- 4 властивості

Після цього перевірте Swagger - дані мають з'явитися!

### Крок 5: Запустіть тест навантаження

```bash
# Отримайте URL вашого додатку (буде виведено після розгортання)
# Або знайдіть у файлі .env.azure

# Легкий тест (5 хвилин)
python3 load_test.py --url https://YOUR-APP-URL --threads 10 --duration 300

# Середній тест (10 хвилин)
python3 load_test.py --url https://YOUR-APP-URL --threads 30 --duration 600

# Важкий тест (15 хвилин) - для гарантованого масштабування
python3 load_test.py --url https://YOUR-APP-URL --threads 50 --duration 900
```

### Крок 6: Моніторинг масштабування

**В окремому терміналі:**

```bash
# Моніторинг кількості реплік
watch -n 5 'az containerapp replica list \
  --name db-repo-app \
  --resource-group labs \
  --query "[].name" -o table'
```

**Або в Azure Portal:**

1. Відкрийте https://portal.azure.com
2. Resource Groups → `labs`
3. Container App `db-repo-app`
4. Metrics → виберіть:
   - Replica Count
   - CPU Usage
   - Memory Usage

### Крок 7: Збережіть результати для звіту

#### Скріншоти з Azure Portal:

- ✅ Графік Replica Count під час тесту
- ✅ Графік CPU Usage
- ✅ Графік Memory Usage
- ✅ Список активних реплік (під час пікового навантаження)
- ✅ Логи подій масштабування

#### Файли для звіту:

- ✅ Результати тестів: `load_test_results_*.txt` (створюється автоматично)
- ✅ Вивід команди: `./azure-status.sh > azure-status-output.txt`
- ✅ Логи: зберіть логи з Container App

#### Як отримати логи масштабування:

```bash
# Останні події
az monitor activity-log list \
  --resource-group labs \
  --max-events 50 \
  --query "[?contains(operationName.localizedValue, 'Scale')].{Time:eventTimestamp, Operation:operationName.localizedValue, Status:status.localizedValue}" \
  --output table > scaling-events.txt

# Логи Container App
az containerapp logs show \
  --name db-repo-app \
  --resource-group labs \
  --tail 200 > container-app-logs.txt
```

---

## 📊 Очікувані результати

### Фази тестування:

| Час         | Репліки | CPU    | Статус                    |
| ----------- | ------- | ------ | ------------------------- |
| 0-2 хв      | 1       | 20-40% | ⏳ Початкове навантаження |
| 2-5 хв      | 1-3     | 70-90% | 📈 Початок масштабування  |
| 5-10 хв     | 3-8     | 60-80% | ⚡ Активне масштабування  |
| 10-15 хв    | 5-10    | 50-70% | ✅ Стабільна робота       |
| Після тесту | 10→1    | ↓      | 📉 Масштабування вниз     |

### Критерії успіху:

- ✅ Container App успішно розгорнуто
- ✅ Автомасштабування налаштовано (CPU 70%, Memory 80%)
- ✅ Під час навантаження репліки збільшилися (мінімум до 3-5)
- ✅ Після зменшення навантаження репліки зменшилися назад до 1
- ✅ Зафіксовано події масштабування в логах
- ✅ Створено скріншоти метрик з Azure Portal

---

## 🔧 Якщо щось пішло не так

### Проблема з ACR

```bash
# Перевірте ім'я ACR
./check-acr-name.sh вашеімя

# Дивіться детально в TROUBLESHOOTING.md
```

### Container App не працює

```bash
# Перевірте логи
az containerapp logs show --name db-repo-app --resource-group labs --follow

# Перевірте статус
./azure-status.sh
```

### Не масштабується

- Збільшіть навантаження: `--threads 50`
- Збільшіть тривалість: `--duration 900`
- Зменшіть поріг CPU до 50%

**Детальніше:** `TROUBLESHOOTING.md`

---

## 🧹 Очищення після завершення

```bash
# Видалення всіх ресурсів Azure
az group delete --name labs --yes --no-wait

# Очищення локального Docker
docker-compose down -v
docker system prune -a
```

⚠️ **Увага:** Це видалить ВСІ ресурси в Resource Group `labs`!

---

## 📖 Детальна документація

- **Швидкий старт:** [QUICKSTART.md](./QUICKSTART.md)
- **Повний посібник:** [DOCKER_AZURE_GUIDE.md](./DOCKER_AZURE_GUIDE.md)
- **Вирішення проблем:** [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

## 📝 Структура звіту (рекомендації)

1. **Вступ**

   - Мета роботи
   - Використані технології

2. **Створення Docker образів**

   - Dockerfile
   - docker-compose.yml
   - Скріншот: `docker images`

3. **Розгортання на Azure**

   - Скріншот Azure Portal: Resource Group
   - Скріншот: Container App Overview
   - URL додатку

4. **Налаштування автомасштабування**

   - Скріншот: Scale rules
   - Параметри: min/max replicas, CPU/Memory thresholds

5. **Тестування навантаження**

   - Опис скрипту load_test.py
   - Параметри тестування
   - Вивід результатів тестування

6. **Результати масштабування**

   - Графік: Replica Count
   - Графік: CPU Usage
   - Графік: Memory Usage
   - Таблиця подій масштабування
   - Аналіз результатів

7. **Висновки**
   - Що працювало добре
   - Які були складнощі
   - Висновки про автомасштабування

---

## ✨ Порада для успішного виконання

1. **Почніть з локального тестування:**

   ```bash
   docker-compose up -d
   curl http://localhost:5000/api/docs/
   ```

2. **Перевірте унікальність ACR ім'я** перед розгортанням

3. **Моніторте розгортання** - не відходьте, перевіряйте логи

4. **Для гарантованого масштабування** використовуйте `--threads 50 --duration 900`

5. **Збережіть всі скріншоти** одразу під час тестування

6. **Не видаляйте ресурси** поки не збережете всі результати!

---

**Успіхів у виконанні лабораторної роботи! 🎓🚀**

Якщо виникнуть питання - дивіться TROUBLESHOOTING.md або Azure Portal logs.
