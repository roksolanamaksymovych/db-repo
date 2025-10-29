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
RESOURCE_GROUP="db-repo-rg"
LOCATION="westeurope"
ACR_NAME="dbreporegistry"
CONTAINER_APP_NAME="db-repo-app"
CONTAINER_APP_ENV="db-repo-env"
IMAGE_NAME="flask-rest-api"
IMAGE_TAG="latest"

# База даних (використовуйте існуючу Azure MySQL або змініть)
DB_HOST="${DB_HOST:-your-mysql-server.mysql.database.azure.com}"
DB_USER="${DB_USER:-adminuser}"
DB_PASSWORD="${DB_PASSWORD:-YourPassword123!}"
DB_NAME="${DB_NAME:-database_lab1_eer}"

log "Початок розгортання на Azure..."

# 1. Вхід в Azure (якщо потрібно)
log "Перевірка автентифікації Azure..."
az account show &> /dev/null || az login

# 2. Створення Resource Group
log "Створення Resource Group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION

# 3. Створення Azure Container Registry
log "Створення Azure Container Registry: $ACR_NAME"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# 4. Вхід в ACR
log "Вхід в Azure Container Registry..."
az acr login --name $ACR_NAME

# 5. Побудова Docker образу
log "Побудова Docker образу..."
docker build -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} .

# 6. Публікація образу в ACR
log "Публікація образу в Azure Container Registry..."
docker push ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}

# 7. Отримання облікових даних ACR
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# 8. Створення Container Apps Environment
log "Створення Container Apps Environment..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# 9. Розгортання Container App з автомасштабуванням
log "Створення Container App з автомасштабуванням..."
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} \
    --registry-server ${ACR_NAME}.azurecr.io \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 5000 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 10 \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars \
        DB_HOST=$DB_HOST \
        DB_USER=$DB_USER \
        DB_PASSWORD=$DB_PASSWORD \
        DB_NAME=$DB_NAME \
        PORT=5000

# 10. Налаштування правил автомасштабування
log "Налаштування правил автомасштабування..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --scale-rule-name cpu-scaling \
    --scale-rule-type cpu \
    --scale-rule-metadata type=Utilization value=70

az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --scale-rule-name memory-scaling \
    --scale-rule-type memory \
    --scale-rule-metadata type=Utilization value=80

# 11. Отримання URL додатку
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

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

