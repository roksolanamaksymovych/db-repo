# 🔧 Вирішення проблем

## Проблема: ACR з такою назвою не доступний

### Симптоми

```
ERROR: The resource with name 'dbreporegistry' could not be found
```

або

```
failed to do request: dial tcp: lookup dbreporegistry.azurecr.io: no such host
```

### Причина

Ім'я Azure Container Registry має бути **унікальним глобально**. Якщо хтось вже використовує це ім'я, ви не можете його використати.

### Рішення

#### Крок 1: Перевірте доступність імені

```bash
chmod +x check-acr-name.sh

# Перевірте поточне ім'я
./check-acr-name.sh dbreporegistry

# Спробуйте нове ім'я
./check-acr-name.sh dbrepo$(date +%s | tail -c 6)
```

#### Крок 2: Змініть ім'я в azure-deploy.sh

Відредагуйте файл `azure-deploy.sh` та змініть рядок:

```bash
ACR_NAME="вашеунікальнеімя123"  # Замініть на доступне ім'я
```

**Вимоги до імені:**

- Тільки малі латинські літери та цифри
- Довжина: 5-50 символів
- Без дефісів, підкреслень, інших символів
- Має бути унікальним глобально

**Приклади хороших імен:**

- `dbreporoksolana2025`
- `flaskapplab123456`
- `myuniquerepo789`

---

## Проблема: Subscription not registered

### Симптоми

```
Subscription is not registered for the Microsoft.OperationalInsights resource provider
```

### Рішення

Виправлений скрипт `azure-deploy.sh` вже автоматично реєструє необхідні провайдери. Якщо проблема залишається:

```bash
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait
az provider register --namespace Microsoft.ContainerRegistry --wait
```

Це може зайняти 2-5 хвилин.

---

## Проблема: Пусті credentials для registry

### Симптоми

```
argument --registry-username: expected one argument
```

### Причина

ACR не має увімкненого admin доступу або credentials не отримані.

### Рішення

Виправлений скрипт перевіряє це автоматично. Якщо проблема залишається:

```bash
# Увімкніть admin доступ
az acr update --name вашеacr --admin-enabled true

# Перевірте credentials
az acr credential show --name вашеacr
```

---

## Проблема: Docker образ не будується

### Симптоми

```
ERROR: failed to solve: ...
```

### Рішення

1. Переконайтеся що Docker Desktop запущено:

```bash
docker ps
```

2. Очистіть Docker кеш:

```bash
docker system prune -a
```

3. Спробуйте побудувати вручну:

```bash
docker build -t test-image .
```

---

## Проблема: Platform mismatch (linux/amd64)

### Симптоми

```
Field 'template.containers.db-repo-app.image' is invalid with details:
'Invalid value: "dbreporegistry.azurecr.io/flask-rest-api:latest":
no child with platform linux/amd64 in index'
```

### Причина

На Mac з Apple Silicon (M1/M2/M3) Docker за замовчуванням будує образи для ARM64, але Azure Container Apps потребує linux/amd64.

### Рішення

**Оновлений скрипт вже виправлено!** Він автоматично будує для правильної платформи.

Якщо потрібно вручну:

```bash
# Побудова для linux/amd64
docker buildx build --platform linux/amd64 \
  -t dbreporegistry.azurecr.io/flask-rest-api:latest .

# Або якщо buildx не працює
docker build --platform linux/amd64 \
  -t dbreporegistry.azurecr.io/flask-rest-api:latest .

# Перевірка платформи образу
docker inspect dbreporegistry.azurecr.io/flask-rest-api:latest | grep Architecture
```

**Після виправлення:**

1. Видаліть старий образ з ACR:

```bash
az acr repository delete \
  --name dbreporegistry \
  --repository flask-rest-api \
  --yes
```

2. Запустіть azure-deploy.sh знову - він побудує правильний образ

---

## Проблема: Container App не створюється

### Симптоми

```
The containerapp 'db-repo-app' does not exist
```

### Причини

1. Помилка на попередніх кроках
2. Недостатньо квоти в підписці
3. Проблеми з мережею

### Рішення

1. Перевірте логи попередніх кроків
2. Спробуйте створити вручну:

```bash
az containerapp create \
    --name db-repo-app \
    --resource-group labs \
    --environment db-repo-env \
    --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
    --target-port 80 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 2
```

3. Перевірте квоти:

```bash
az vm list-usage --location westus -o table
```

---

## Проблема: База даних не доступна

### Симптоми

- Container App запущений але не працює
- Помилки в логах про підключення до БД

### Рішення

1. Перевірте чи правильні credentials у `azure-deploy.sh`:

```bash
DB_HOST="labissserver.mysql.database.azure.com"
DB_USER="roksolana"
DB_PASSWORD="Maks_mia3!"
DB_NAME="database_lab1_eer"
```

2. Перевірте чи Azure MySQL дозволяє підключення з Azure services:

   - Azure Portal → MySQL → Networking
   - Увімкніть "Allow public access from any Azure service"

3. Перевірте логи Container App:

```bash
az containerapp logs show \
    --name db-repo-app \
    --resource-group labs \
    --follow
```

---

## Корисні команди для діагностики

### Перевірка статусу всього розгортання

```bash
chmod +x azure-status.sh
./azure-status.sh labs db-repo-app dbreporegistry
```

### Перегляд логів в реальному часі

```bash
az containerapp logs show \
    --name db-repo-app \
    --resource-group labs \
    --follow
```

### Список всіх ресурсів у Resource Group

```bash
az resource list \
    --resource-group labs \
    --output table
```

### Видалення всього та початок спочатку

```bash
# УВАГА: Видалить ВСІ ресурси в Resource Group!
az group delete --name labs --yes --no-wait

# Зачекайте 2-3 хвилини
# Потім запустіть azure-deploy.sh знову
```

### Перевірка Container App

```bash
# Статус
az containerapp show \
    --name db-repo-app \
    --resource-group labs

# Репліки
az containerapp replica list \
    --name db-repo-app \
    --resource-group labs \
    --output table

# Revision history
az containerapp revision list \
    --name db-repo-app \
    --resource-group labs \
    --output table
```

---

## Повний workflow після виправлення

1. **Перевірте ім'я ACR:**

```bash
./check-acr-name.sh вашеімя123
```

2. **Змініть azure-deploy.sh** з новим іменем ACR

3. **Очистіть попередні ресурси** (якщо є помилки):

```bash
az group delete --name labs --yes --no-wait
# Зачекайте 2-3 хвилини
```

4. **Запустіть розгортання:**

```bash
./azure-deploy.sh
```

5. **Моніторте статус:**

```bash
./azure-status.sh
```

6. **Тестуйте:**

```bash
python3 load_test.py --url https://your-app-url --threads 20 --duration 300
```

---

## Контакти для допомоги

Якщо проблема не вирішується:

1. Перевірте [Azure Status](https://status.azure.com/) - можливо проблеми з Azure
2. Подивіться [Azure Container Apps Issues](https://github.com/microsoft/azure-container-apps/issues)
3. Збережіть повний вивід команд для аналізу

---

**Успіхів! 🚀**
