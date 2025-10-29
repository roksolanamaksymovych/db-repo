#!/bin/bash

# Скрипт для перевірки статусу розгортання на Azure

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Конфігурація (має співпадати з azure-deploy.sh)
RESOURCE_GROUP="${1:-labs}"
CONTAINER_APP_NAME="${2:-db-repo-app}"
ACR_NAME="${3:-dbreporegistry}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}СТАТУС AZURE CONTAINER APP${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "Container App: $CONTAINER_APP_NAME"
echo "ACR: $ACR_NAME"
echo ""

# Перевірка автентифікації
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Увійдіть в Azure: az login${NC}"
    exit 1
fi

echo -e "${GREEN}1. Статус Container App:${NC}"
az containerapp show \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "{name:name, status:properties.provisioningState, url:properties.configuration.ingress.fqdn, replicas:properties.template.scale}" \
    2>/dev/null || echo "Container App не знайдено"

echo ""
echo -e "${GREEN}2. URL додатку:${NC}"
APP_URL=$(az containerapp show \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.configuration.ingress.fqdn -o tsv 2>/dev/null)

if [ -n "$APP_URL" ]; then
    echo "https://$APP_URL"
    echo "Swagger: https://$APP_URL/api/docs/"
else
    echo "URL не знайдено"
fi

echo ""
echo -e "${GREEN}3. Активні репліки:${NC}"
az containerapp replica list \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --output table \
    2>/dev/null || echo "Не вдалося отримати список реплік"

echo ""
echo -e "${GREEN}4. Правила масштабування:${NC}"
az containerapp show \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.template.scale" \
    2>/dev/null || echo "Не вдалося отримати правила"

echo ""
echo -e "${GREEN}5. Останні події:${NC}"
az monitor activity-log list \
    --resource-group "$RESOURCE_GROUP" \
    --max-events 5 \
    --query "[].{Time:eventTimestamp, Level:level, Operation:operationName.localizedValue}" \
    --output table \
    2>/dev/null || echo "Не вдалося отримати події"

echo ""
echo -e "${GREEN}6. Образи в ACR:${NC}"
az acr repository list \
    --name "$ACR_NAME" \
    --output table \
    2>/dev/null || echo "ACR не знайдено або немає образів"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Корисні команди:${NC}"
echo ""
echo "Логи в реальному часі:"
echo "  az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "Моніторинг реплік:"
echo "  watch -n 5 'az containerapp replica list --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --output table'"
echo ""
echo "Ручне масштабування:"
echo "  az containerapp update --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --min-replicas 2 --max-replicas 15"
echo ""
echo -e "${BLUE}========================================${NC}"

