# 🚀 Налаштування CI/CD для Azure Web App

## Крок 1: Створення Azure Web App

### Через Azure Portal:

1. Відкрийте [Azure Portal](https://portal.azure.com)
2. **Create a resource** → **Web App**
3. Заповніть форму:
   - **Resource Group:** `db-repo-rg` (або створіть новий)
   - **Name:** `db-repo-flask-app` (має бути унікальним глобально)
   - **Publish:** `Code`
   - **Runtime stack:** `Python 3.11`
   - **Operating System:** `Linux`
   - **Region:** `West Europe` (або інший)
   - **Pricing plan:** `Free F1` або `Basic B1`
4. **Review + Create** → **Create**

### Через Azure CLI:

```bash
# Створення Resource Group (якщо не існує)
az group create --name db-repo-rg --location westeurope

# Створення App Service Plan
az appservice plan create \
  --name db-repo-plan \
  --resource-group db-repo-rg \
  --sku B1 \
  --is-linux

# Створення Web App
az webapp create \
  --name db-repo-flask-app \
  --resource-group db-repo-rg \
  --plan db-repo-plan \
  --runtime "PYTHON:3.11"
```

---

## Крок 2: Налаштування змінних середовища

### Через Azure Portal:

1. Відкрийте ваш Web App в Azure Portal
2. **Settings** → **Configuration**
3. **Application settings** → **New application setting**
4. Додайте змінні:
   ```
   DB_HOST=labissserver.mysql.database.azure.com
   DB_USER=roksolana
   DB_PASSWORD=Maks_mia3
   DB_NAME=database_lab1_eer
   PORT=8000
   SCM_DO_BUILD_DURING_DEPLOYMENT=true
   ```
5. **Save**

### Через Azure CLI:

```bash
az webapp config appsettings set \
  --name db-repo-flask-app \
  --resource-group db-repo-rg \
  --settings \
    DB_HOST=labissserver.mysql.database.azure.com \
    DB_USER=roksolana \
    DB_PASSWORD=Maks_mia3 \
    DB_NAME=database_lab1_eer \
    PORT=8000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

---

## Крок 3: Налаштування startup command

Web App потребує команду для запуску Flask:

### Через Azure Portal:

1. **Settings** → **Configuration**
2. **General settings** → **Startup Command**
3. Введіть:
   ```
   gunicorn --bind=0.0.0.0 --timeout 600 app:app
   ```
4. **Save**

### Через Azure CLI:

```bash
az webapp config set \
  --name db-repo-flask-app \
  --resource-group db-repo-rg \
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
```

---

## Крок 4: Отримання Publish Profile

### Через Azure Portal:

1. Відкрийте ваш Web App
2. **Overview** → **Get publish profile** (кнопка зверху)
3. Завантажиться XML файл
4. Відкрийте файл і скопіюйте весь вміст

### Через Azure CLI:

```bash
az webapp deployment list-publishing-profiles \
  --name db-repo-flask-app \
  --resource-group db-repo-rg \
  --xml
```

Скопіюйте весь XML вивід.

---

## Крок 5: Додавання секрету в GitHub

1. Відкрийте ваш репозиторій на GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret**
4. Заповніть:
   - **Name:** `AZUREAPPSERVICE_PUBLISHPROFILE`
   - **Value:** Вставте XML з Publish Profile
5. **Add secret**

---

## Крок 6: Оновлення workflow файлу

Відредагуйте `.github/workflows/azure-deploy.yml`:

```yaml
env:
  AZURE_WEBAPP_NAME: db-repo-flask-app # Змініть на ім'я вашого Web App
```

---

## Крок 7: Запуск CI/CD

### Автоматично:

Просто зробіть commit і push на гілку `main`:

```bash
git add .github/workflows/azure-deploy.yml
git commit -m "Додано CI/CD для Azure Web App"
git push origin main
```

GitHub Actions автоматично почне деплой!

### Вручну:

1. GitHub → **Actions** → **Deploy Flask App to Azure Web App**
2. **Run workflow** → **Run workflow**

---

## Крок 8: Перевірка деплою

### Переглянути статус:

1. GitHub → **Actions**
2. Клікніть на останній workflow run
3. Подивіться логи build та deploy

### Перевірити додаток:

```bash
# URL вашого додатку
https://db-repo-flask-app.azurewebsites.net

# API endpoints
https://db-repo-flask-app.azurewebsites.net/api/users
https://db-repo-flask-app.azurewebsites.net/api/docs/
```

### Перегляд логів Web App:

```bash
# Потокові логи
az webapp log tail \
  --name db-repo-flask-app \
  --resource-group db-repo-rg

# Історія логів
az webapp log download \
  --name db-repo-flask-app \
  --resource-group db-repo-rg \
  --log-file logs.zip
```

---

## Troubleshooting

### Проблема: Application Error

**Рішення:**

1. Перевірте логи:
   ```bash
   az webapp log tail --name db-repo-flask-app --resource-group db-repo-rg
   ```
2. Переконайтеся що `gunicorn` в `requirements.txt`
3. Перевірте startup command

### Проблема: Database connection failed

**Рішення:**

1. Перевірте змінні середовища в Configuration
2. Переконайтеся що Azure MySQL дозволяє підключення з Azure services
3. Перевірте firewall rules в MySQL

### Проблема: Workflow fails

**Рішення:**

1. Перевірте що `AZUREAPPSERVICE_PUBLISHPROFILE` доданий в GitHub Secrets
2. Перевірте що `AZURE_WEBAPP_NAME` правильний в workflow
3. Подивіться детальні логи в GitHub Actions

---

## Додаткові налаштування

### Додавання custom domain:

```bash
az webapp config hostname add \
  --webapp-name db-repo-flask-app \
  --resource-group db-repo-rg \
  --hostname www.yourdomain.com
```

### Увімкнення HTTPS:

```bash
az webapp update \
  --name db-repo-flask-app \
  --resource-group db-repo-rg \
  --https-only true
```

### Масштабування:

```bash
# Збільшити plan до Standard
az appservice plan update \
  --name db-repo-plan \
  --resource-group db-repo-rg \
  --sku S1

# Автоскейлінг
az monitor autoscale create \
  --resource-group db-repo-rg \
  --resource db-repo-flask-app \
  --resource-type Microsoft.Web/sites \
  --name autoscale-db-repo \
  --min-count 1 \
  --max-count 3 \
  --count 1
```

---

## Структура CI/CD Pipeline

```
GitHub Push (main)
    ↓
Build Job
    ├── Checkout code
    ├── Setup Python
    ├── Install dependencies
    ├── Create artifact (ZIP)
    └── Upload artifact
    ↓
Deploy Job
    ├── Download artifact
    ├── Unzip
    └── Deploy to Azure Web App
    ↓
Azure Web App
    ├── Unpack code
    ├── Run pip install
    ├── Start gunicorn
    └── Serve application
```

---

## Корисні команди

```bash
# Перезапуск Web App
az webapp restart --name db-repo-flask-app --resource-group db-repo-rg

# Статус Web App
az webapp show --name db-repo-flask-app --resource-group db-repo-rg --query state

# Список deployments
az webapp deployment list --name db-repo-flask-app --resource-group db-repo-rg

# SSH в контейнер (для діагностики)
az webapp ssh --name db-repo-flask-app --resource-group db-repo-rg
```

---

**Успіхів з CI/CD! 🚀**
