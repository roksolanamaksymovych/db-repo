
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

RESOURCE_GROUP="${RESOURCE_GROUP:-labs}"
ACR_NAME="${ACR_NAME:-dbreporegistry}"
CONTAINER_APP_NAME="${CONTAINER_APP_NAME:-db-repo-app}"
IMAGE_NAME="${IMAGE_NAME:-flask-rest-api}"
IMAGE_TAG="latest"

log "Швидке оновлення Container App..."

log "Вхід в Azure Container Registry..."
az acr login --name $ACR_NAME

log "Побудова нового Docker образу..."
docker buildx build --platform linux/amd64 -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    warning "Buildx не вдався, пробуємо звичайний build..."
    docker build --platform linux/amd64 -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} .
fi

log "Публікація образу..."
docker push ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}

log "Оновлення Container App (це займе 1-2 хвилини)..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} \
    --output none



APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)


log "Swagger: https://$APP_URL/api/docs/"


