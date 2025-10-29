#!/bin/bash

# Швидкий запуск тесту навантаження

# Кольори
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}ТЕСТ НАВАНТАЖЕННЯ REST API${NC}"
echo -e "${GREEN}========================================${NC}"

# Перевірка URL
if [ -z "$1" ]; then
    echo -e "${YELLOW}Використання: $0 <URL> [threads] [duration]${NC}"
    echo ""
    echo "Приклади:"
    echo "  $0 http://localhost:5000"
    echo "  $0 https://your-app.azurecontainerapps.io 20 600"
    echo ""
    read -p "Введіть URL API (або Enter для localhost:5000): " API_URL
    API_URL=${API_URL:-http://localhost:5000}
else
    API_URL=$1
fi

THREADS=${2:-10}
DURATION=${3:-300}

echo ""
echo "Параметри тесту:"
echo "  URL: $API_URL"
echo "  Потоки: $THREADS"
echo "  Тривалість: $DURATION секунд"
echo ""

# Встановлення залежностей якщо потрібно
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Встановлення залежностей..."
    pip3 install requests
fi

# Запуск тесту
echo -e "${GREEN}Запуск тесту...${NC}"
python3 load_test.py --url "$API_URL" --threads "$THREADS" --duration "$DURATION"

echo ""
echo -e "${GREEN}Тест завершено!${NC}"

