#!/bin/bash

# Скрипт для розгортання на Azure Container Apps з автомасштабуванням

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функція для виводу повідомлень
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Перевірка чи встановлений Azure CLI
if ! command -v az &> /dev/null; then
    error "Azure CLI не встановлений. Встановіть його: https://docs.microsoft.com/cli/azure/install-azure-cli"
fi

# Конфігураційні змінні (ЗМІНІТЬ НА СВОЇ)
RESOURCE_GROUP="labs"
LOCATION="westus"
ACR_NAME="dbreporegistry"
CONTAINER_APP_NAME="db-repo-app"
CONTAINER_APP_ENV="db-repo-env"
IMAGE_NAME="flask-rest-api"
IMAGE_TAG="latest"

# База даних (використовуйте існуючу Azure MySQL або змініть)
DB_HOST="${DB_HOST:-labissserver.mysql.database.azure.com}"
DB_USER="${DB_USER:-roksolana}"
DB_PASSWORD="${DB_PASSWORD:-Maks_mia3!}"
DB_NAME="${DB_NAME:-database_lab1_eer}"

log "Початок розгортання на Azure..."

# 1. Вхід в Azure (якщо потрібно)
log "Перевірка автентифікації Azure..."
az account show &> /dev/null || az login

# 2. Реєстрація необхідних resource providers
log "Реєстрація resource providers..."
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait
az provider register --namespace Microsoft.ContainerRegistry --wait
log "Resource providers зареєстровано"

# 3. Створення Resource Group (якщо не існує)
log "Створення Resource Group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# 4. Перевірка та створення Azure Container Registry
log "Перевірка існування ACR: $ACR_NAME"
ACR_EXISTS=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -z "$ACR_EXISTS" ]; then
    log "Створення нового Azure Container Registry: $ACR_NAME"
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Basic \
        --admin-enabled true \
        --output none
    
    if [ $? -ne 0 ]; then
        error "Не вдалося створити ACR. Перевірте чи назва '$ACR_NAME' доступна (має бути унікальною глобально)"
    fi
    log "ACR створено успішно"
else
    log "ACR вже існує, використовуємо існуючий"
    # Переконуємося що admin enabled
    az acr update --name $ACR_NAME --admin-enabled true --output none
fi

# 5. Вхід в ACR
log "Вхід в Azure Container Registry..."
az acr login --name $ACR_NAME

if [ $? -ne 0 ]; then
    error "Не вдалося увійти в ACR"
fi

# 6. Побудова Docker образу
log "Побудова Docker образу..."
docker build -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    error "Не вдалося побудувати Docker образ"
fi
log "Docker образ побудовано успішно"

# 7. Публікація образу в ACR
log "Публікація образу в Azure Container Registry..."
docker push ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}

if [ $? -ne 0 ]; then
    error "Не вдалося запушити образ в ACR"
fi
log "Образ успішно завантажено в ACR"

# 8. Отримання облікових даних ACR
log "Отримання облікових даних ACR..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv 2>/dev/null)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv 2>/dev/null)

if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
    error "Не вдалося отримати облікові дані ACR. Переконайтеся що admin-enabled=true"
fi
log "Облікові дані отримано: $ACR_USERNAME"

# 9. Створення Container Apps Environment
log "Створення Container Apps Environment..."
ENV_EXISTS=$(az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -z "$ENV_EXISTS" ]; then
    log "Створення нового Environment..."
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --output none
    
    if [ $? -ne 0 ]; then
        error "Не вдалося створити Container Apps Environment"
    fi
    log "Environment створено успішно"
else
    log "Environment вже існує, використовуємо існуючий"
fi

# 10. Видалення існуючого Container App (якщо є) та створення нового
log "Перевірка існування Container App..."
APP_EXISTS=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -n "$APP_EXISTS" ]; then
    warning "Container App вже існує, видаляємо старий..."
    az containerapp delete \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --yes \
        --output none
    log "Старий Container App видалено"
fi

log "Створення Container App з автомасштабуванням..."
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} \
    --registry-server ${ACR_NAME}.azurecr.io \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --target-port 5000 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 10 \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars \
        DB_HOST="$DB_HOST" \
        DB_USER="$DB_USER" \
        DB_PASSWORD="$DB_PASSWORD" \
        DB_NAME="$DB_NAME" \
        PORT=5000 \
    --output none

if [ $? -ne 0 ]; then
    error "Не вдалося створити Container App"
fi
log "Container App створено успішно"

# 11. Налаштування правил автомасштабування
log "Налаштування правил автомасштабування..."

log "Додавання правила масштабування за CPU..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --scale-rule-name cpu-scaling \
    --scale-rule-type cpu \
    --scale-rule-metadata type=Utilization value=70 \
    --output none

log "Додавання правила масштабування за Memory..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --scale-rule-name memory-scaling \
    --scale-rule-type memory \
    --scale-rule-metadata type=Utilization value=80 \
    --output none

log "Правила автомасштабування налаштовано"

# 12. Отримання URL додатку
log "Отримання URL додатку..."
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

if [ -z "$APP_URL" ]; then
    warning "Не вдалося отримати URL додатку"
    APP_URL="невідомо"
fi

log "=========================================="
log "Розгортання завершено успішно!"
log "=========================================="
log "URL вашого додатку: https://$APP_URL"
log "Swagger документація: https://$APP_URL/api/docs/"
log "Resource Group: $RESOURCE_GROUP"
log "Container Registry: ${ACR_NAME}.azurecr.io"
log "Container App: $CONTAINER_APP_NAME"
log "=========================================="
log "Автомасштабування налаштовано:"
log "  - Мінімум: 1 екземпляр"
log "  - Максимум: 10 екземплярів"
log "  - Правило CPU: >70%"
log "  - Правило Memory: >80%"
log "=========================================="

# Збереження URL в файл
echo "APP_URL=https://$APP_URL" > .env.azure
log "URL збережено у файл .env.azure"

