#!/bin/bash

# Скрипт для перевірки доступності імені Azure Container Registry

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}ПЕРЕВІРКА ІМЕНІ ACR${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Перевірка чи вказано ім'я
if [ -z "$1" ]; then
    echo "Використання: $0 <acr-name>"
    echo ""
    echo "Приклад: $0 myuniqueacr123"
    echo ""
    echo "Вимоги до імені ACR:"
    echo "  - Тільки латинські літери та цифри"
    echo "  - Довжина: 5-50 символів"
    echo "  - Має бути унікальним глобально"
    echo ""
    exit 1
fi

ACR_NAME=$1

echo "Перевірка доступності імені: $ACR_NAME"
echo ""

# Перевірка формату
if [[ ! "$ACR_NAME" =~ ^[a-z0-9]{5,50}$ ]]; then
    echo -e "${RED}❌ Некоректний формат імені!${NC}"
    echo "Ім'я має містити тільки малі літери та цифри (5-50 символів)"
    exit 1
fi

# Перевірка доступності
result=$(az acr check-name --name "$ACR_NAME" 2>/dev/null)

if echo "$result" | grep -q '"nameAvailable": true'; then
    echo -e "${GREEN}✅ Ім'я '$ACR_NAME' доступне!${NC}"
    echo ""
    echo "Використайте це ім'я у файлі azure-deploy.sh:"
    echo -e "${YELLOW}ACR_NAME=\"$ACR_NAME\"${NC}"
    exit 0
elif echo "$result" | grep -q '"nameAvailable": false'; then
    echo -e "${RED}❌ Ім'я '$ACR_NAME' вже зайняте${NC}"
    echo ""
    echo "Спробуйте інше ім'я, наприклад:"
    RANDOM_SUFFIX=$(date +%s | tail -c 6)
    echo "  - ${ACR_NAME}${RANDOM_SUFFIX}"
    echo "  - ${ACR_NAME}app"
    echo "  - dbrepo${RANDOM_SUFFIX}"
    exit 1
else
    echo -e "${RED}❌ Помилка перевірки імені${NC}"
    echo "Переконайтеся що Azure CLI встановлено та ви увійшли: az login"
    exit 1
fi

