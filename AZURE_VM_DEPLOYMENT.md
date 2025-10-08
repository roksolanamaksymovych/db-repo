# 🖥️ Покрокова інструкція для деплою на Azure Virtual Machine

Цей документ містить детальну інструкцію для розгортання Flask додатку на віртуальній машині Azure.

## 📋 Зміст

1. [Передумови](#передумови)
2. [Крок 1: Створення Azure MySQL Database](#крок-1-створення-azure-mysql-database)
3. [Крок 2: Створення віртуальної машини](#крок-2-створення-віртуальної-машини)
4. [Крок 3: Підключення до VM](#крок-3-підключення-до-vm)
5. [Крок 4: Налаштування серверного середовища](#крок-4-налаштування-серверного-середовища)
6. [Крок 5: Встановлення та налаштування додатку](#крок-5-встановлення-та-налаштування-додатку)
7. [Крок 6: Налаштування Nginx](#крок-6-налаштування-nginx)
8. [Крок 7: Налаштування systemd service](#крок-7-налаштування-systemd-service)
9. [Крок 8: Перевірка працездатності](#крок-8-перевірка-працездатності)
10. [Додаткові налаштування](#додаткові-налаштування)

---

## Передумови

Перед початком переконайтеся, що у вас є:

- ✅ Акаунт Microsoft Azure (безкоштовна підписка: https://azure.microsoft.com/free/)
- ✅ Встановлений Azure CLI (https://docs.microsoft.com/cli/azure/install-azure-cli)
- ✅ SSH клієнт (термінал на macOS/Linux або PuTTY на Windows)
- ✅ Код проекту на GitHub

---

## Крок 1: Створення Azure MySQL Database

### 1.1. Вхід в Azure Portal

1. Перейдіть на https://portal.azure.com
2. Увійдіть за допомогою облікового запису Microsoft

### 1.2. Створення MySQL сервера

1. Натисніть **"Create a resource"**
2. Знайдіть **"Azure Database for MySQL Flexible Server"**
3. Натисніть **"Create"**

### 1.3. Налаштування сервера

**Вкладка Basics:**

- **Subscription**: Оберіть вашу підписку
- **Resource Group**: Створіть нову (наприклад, `myapp-vm-rg`)
- **Server name**: `myapp-mysql-server` (має бути унікальним)
- **Region**: `West Europe` або найближчий до вас
- **MySQL version**: 8.0
- **Compute + Storage**: **Burstable, B1ms** (найдешевший варіант)
- **Admin username**: `dbadmin`
- **Password**: Створіть надійний пароль та **ЗБЕРЕЖІТЬ ЙОГ**

**Вкладка Networking:**

- **Connectivity method**: Public access
- **Firewall rules**:
  - ✅ **Allow public access from any Azure service**
  - Додайте правило: `0.0.0.0` - `255.255.255.255` (для тестування, пізніше обмежте)

4. Натисніть **"Review + create"** → **"Create"**
5. Зачекайте 5-10 хвилин

### 1.4. Створення бази даних

1. Перейдіть до створеного MySQL сервера
2. **"Databases"** → **"+ Add"**
3. Ім'я: `database_lab1_eer`
4. Charset: `utf8mb4`
5. Collation: `utf8mb4_general_ci`
6. **"Save"**

### 1.5. Збережіть підключення

```
DB_HOST=myapp-mysql-server.mysql.database.azure.com
DB_USER=dbadmin
DB_PASSWORD=ваш_пароль
DB_NAME=database_lab1_eer
```

---

## Крок 2: Створення віртуальної машини

### 2.1. Створення VM через Azure Portal

1. Azure Portal → **"Create a resource"**
2. Знайдіть **"Virtual Machine"**
3. **"Create"**

### 2.2. Налаштування VM

**Вкладка Basics:**

- **Subscription**: Ваша підписка
- **Resource Group**: Та сама що й для MySQL (`myapp-vm-rg`)
- **Virtual machine name**: `myapp-flask-vm`
- **Region**: Той самий що й MySQL (West Europe)
- **Availability options**: No infrastructure redundancy required
- **Security type**: Standard
- **Image**: **Ubuntu Server 22.04 LTS - x64 Gen2**
- **Size**: **Standard_B1s** (найдешевший) або **Standard_B2s** (краще для продакшену)
  - Клікніть "See all sizes" щоб знайти B1s
- **Authentication type**: SSH public key
- **Username**: `azureuser` (або ваше ім'я)
- **SSH public key source**:
  - Оберіть "Generate new key pair"
  - Key pair name: `myapp-vm-key`

**Вкладка Disks:**

- **OS disk type**: Standard SSD (найдешевший)
- Залишіть решту за замовчуванням

**Вкладка Networking:**

- **Virtual network**: Створити нову або використати існуючу
- **Subnet**: default
- **Public IP**: Створити нову
- **NIC network security group**: Basic
- **Public inbound ports**: **Allow selected ports**
- **Select inbound ports**:
  - ✅ SSH (22)
  - ✅ HTTP (80)
  - ✅ HTTPS (443)

**Вкладка Management:**

- Залишіть за замовчуванням

**Вкладка Monitoring:**

- **Boot diagnostics**: Disable (для економії)

4. **"Review + create"** → **"Create"**

### 2.3. Завантажте SSH ключ

**ВАЖЛИВО!** Коли VM створюється, Azure запропонує завантажити приватний SSH ключ.

1. Натисніть **"Download private key and create resource"**
2. Збережіть файл (наприклад, `myapp-vm-key.pem`)
3. Зачекайте 3-5 хвилин до завершення створення

### 2.4. Знайдіть Public IP адресу

1. Перейдіть до створеної VM
2. На сторінці Overview знайдіть **Public IP address**
3. Збережіть цю адресу (наприклад, `20.23.45.67`)

---

## Крок 3: Підключення до VM

### 3.1. На macOS/Linux

```bash
# Налаштуйте права доступу до ключа
chmod 400 ~/Downloads/myapp-vm-key.pem

# Підключіться до VM
ssh -i ~/Downloads/myapp-vm-key.pem azureuser@20.23.45.67
```

### 3.2. На Windows (PowerShell)

```powershell
# Підключіться до VM
ssh -i C:\Users\YourName\Downloads\myapp-vm-key.pem azureuser@20.23.45.67
```

### 3.3. На Windows (PuTTY)

1. Конвертуйте .pem в .ppk за допомогою PuTTYgen
2. Відкрийте PuTTY
3. Введіть IP адресу VM
4. Connection → SSH → Auth → приватний ключ (.ppk)
5. Open

---

## Крок 4: Налаштування серверного середовища

Після підключення до VM виконайте наступні команди:

### 4.1. Оновлення системи

```bash
# Оновити список пакетів
sudo apt update

# Оновити встановлені пакети
sudo apt upgrade -y
```

### 4.2. Встановлення Python та необхідних інструментів

```bash
# Встановити Python 3.11 та pip
sudo apt install -y python3.11 python3.11-venv python3-pip

# Встановити git
sudo apt install -y git

# Встановити Nginx
sudo apt install -y nginx

# Встановити інші необхідні пакети
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### 4.3. Встановлення MySQL клієнта (опціонально, для тестування)

```bash
sudo apt install -y mysql-client
```

---

## Крок 5: Встановлення та налаштування додатку

### 5.1. Клонування репозиторію

```bash
# Перейти в home директорію
cd ~

# Клонувати проект з GitHub
git clone https://github.com/ваш_username/назва_репозиторію.git
cd назва_репозиторію

# Або якщо репозиторій приватний, використовуйте Personal Access Token
```

### 5.2. Створення віртуального середовища

```bash
# Створити віртуальне середовище
python3.11 -m venv venv

# Активувати віртуальне середовище
source venv/bin/activate

# Оновити pip
pip install --upgrade pip
```

### 5.3. Встановлення залежностей

```bash
# Встановити всі залежності з requirements.txt
pip install -r requirements.txt
```

### 5.4. Налаштування змінних середовища

```bash
# Створити .env файл
nano .env
```

Додайте наступний вміст (замініть значення на ваші):

```env
DB_USER=dbadmin
DB_PASSWORD=ваш_mysql_пароль
DB_HOST=myapp-mysql-server.mysql.database.azure.com
DB_NAME=database_lab1_eer
FLASK_ENV=production
SECRET_KEY=згенеруйте_випадковий_складний_ключ
```

Збережіть файл: `Ctrl+O`, `Enter`, `Ctrl+X`

### 5.5. Ініціалізація бази даних (якщо потрібно)

```bash
# Якщо у вас є скрипт ініціалізації
python my_project/db_init.py
```

### 5.6. Тестовий запуск

```bash
# Запустіть додаток для перевірки
python app.py

# Відкрийте новий термінал і перевірте
curl http://localhost:5000/users

# Якщо все працює, зупиніть додаток: Ctrl+C
```

---

## Крок 6: Налаштування Nginx

### 6.1. Створення конфігурації Nginx

```bash
# Створити конфігураційний файл
sudo nano /etc/nginx/sites-available/flask-app
```

Додайте наступний вміст:

```nginx
server {
    listen 80;
    server_name ваш_public_ip або ваш_домен;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Для статичних файлів Swagger
    location /flasgger_static/ {
        proxy_pass http://127.0.0.1:8000/flasgger_static/;
    }
}
```

Збережіть: `Ctrl+O`, `Enter`, `Ctrl+X`

### 6.2. Активація конфігурації

```bash
# Створити symlink
sudo ln -s /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/

# Видалити дефолтну конфігурацію
sudo rm /etc/nginx/sites-enabled/default

# Перевірити конфігурацію
sudo nginx -t

# Перезапустити Nginx
sudo systemctl restart nginx

# Перевірити статус
sudo systemctl status nginx
```

---

## Крок 7: Налаштування systemd service

### 7.1. Створення systemd service файлу

```bash
# Створити service файл
sudo nano /etc/systemd/system/flask-app.service
```

Додайте наступний вміст (замініть шляхи на ваші):

```ini
[Unit]
Description=Flask Application
After=network.target

[Service]
User=azureuser
Group=www-data
WorkingDirectory=/home/azureuser/назва_репозиторію
Environment="PATH=/home/azureuser/назва_репозиторію/venv/bin"
EnvironmentFile=/home/azureuser/назва_репозиторію/.env
ExecStart=/home/azureuser/назва_репозиторію/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 600 app:app

[Install]
WantedBy=multi-user.target
```

Збережіть: `Ctrl+O`, `Enter`, `Ctrl+X`

### 7.2. Запуск service

```bash
# Перезавантажити systemd
sudo systemctl daemon-reload

# Запустити service
sudo systemctl start flask-app

# Перевірити статус
sudo systemctl status flask-app

# Увімкнути автозапуск при старті системи
sudo systemctl enable flask-app
```

### 7.3. Перевірка логів

```bash
# Переглянути логи додатку
sudo journalctl -u flask-app -f

# Переглянути останні 100 рядків
sudo journalctl -u flask-app -n 100
```

---

## Крок 8: Перевірка працездатності

### 8.1. Перевірка з VM

```bash
# Перевірити локально
curl http://localhost:8000/users

# Перевірити через Nginx
curl http://localhost/users
```

### 8.2. Перевірка з вашого локального ПК

```bash
# Замініть на ваш Public IP
curl http://20.23.45.67/users

# Перевірити Swagger (відкрийте в браузері)
http://20.23.45.67/api/docs/
```

### 8.3. Тестування всіх endpoints через Swagger

1. Відкрийте в браузері: `http://ваш_public_ip/api/docs/`
2. Ви побачите інтерактивну документацію
3. Спробуйте кожен endpoint:
   - **GET /users** - отримати всіх користувачів
   - **POST /users** - створити користувача
   - **GET /categories** - отримати категорії
   - **GET /properties** - отримати властивості

### 8.4. Тестування через curl

```bash
# GET запит
curl http://ваш_public_ip/users

# POST запит (створити користувача)
curl -X POST http://ваш_public_ip/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Тестовий Користувач","email":"test@example.com"}'

# GET користувача за ID
curl http://ваш_public_ip/users/1

# PUT запит (оновити користувача)
curl -X PUT http://ваш_public_ip/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Оновлене Імя","email":"updated@example.com"}'

# DELETE запит (видалити користувача)
curl -X DELETE http://ваш_public_ip/users/1
```

---

## Додаткові налаштування

### Налаштування HTTPS (SSL сертифікат)

#### Варіант 1: Let's Encrypt (безкоштовно)

Якщо у вас є доменне ім'я:

```bash
# Встановити Certbot
sudo apt install -y certbot python3-certbot-nginx

# Отримати SSL сертифікат
sudo certbot --nginx -d ваш_домен.com

# Автоматичне оновлення
sudo certbot renew --dry-run
```

#### Варіант 2: Самопідписаний сертифікат (для тестування)

```bash
# Створити самопідписаний сертифікат
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt

# Оновити Nginx конфігурацію
sudo nano /etc/nginx/sites-available/flask-app
```

Додайте HTTPS блок:

```nginx
server {
    listen 443 ssl;
    server_name ваш_ip;

    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name ваш_ip;
    return 301 https://$server_name$request_uri;
}
```

```bash
sudo systemctl restart nginx
```

### Налаштування Firewall (UFW)

```bash
# Увімкнути UFW
sudo ufw enable

# Дозволити SSH (ВАЖЛИВО!)
sudo ufw allow ssh

# Дозволити HTTP
sudo ufw allow http

# Дозволити HTTPS
sudo ufw allow https

# Перевірити статус
sudo ufw status
```

### Моніторинг та логи

```bash
# Логи додатку
sudo journalctl -u flask-app -f

# Логи Nginx (access)
sudo tail -f /var/log/nginx/access.log

# Логи Nginx (error)
sudo tail -f /var/log/nginx/error.log

# Використання ресурсів
htop
```

### Оновлення додатку

```bash
# Підключіться до VM
ssh -i myapp-vm-key.pem azureuser@ваш_public_ip

# Перейдіть в директорію проекту
cd ~/назва_репозиторію

# Отримайте останні зміни з GitHub
git pull origin main

# Активуйте віртуальне середовище
source venv/bin/activate

# Встановіть нові залежності (якщо є)
pip install -r requirements.txt

# Перезапустіть service
sudo systemctl restart flask-app

# Перевірте статус
sudo systemctl status flask-app
```

### Backup бази даних

```bash
# Встановіть MySQL client (якщо ще не встановлено)
sudo apt install -y mysql-client

# Створіть backup
mysqldump -h myapp-mysql-server.mysql.database.azure.com \
  -u dbadmin -p database_lab1_eer > backup_$(date +%Y%m%d).sql

# Відновлення з backup
mysql -h myapp-mysql-server.mysql.database.azure.com \
  -u dbadmin -p database_lab1_eer < backup_20240101.sql
```

---

## 🔍 Перевірка для здачі лабораторної

**Перевірте наступне:**

✅ **Код на GitHub:**

- Репозиторій публічний або викладач має доступ
- Всі файли закомічені

✅ **Azure MySQL:**

- База даних створена і працює
- З'єднання працює

✅ **Azure VM:**

- Віртуальна машина запущена
- Public IP доступний
- SSH підключення працює

✅ **Додаток працює:**

- Flask додаток запущений як systemd service
- Nginx налаштований як reverse proxy
- URL працює: `http://ваш_public_ip/api/docs/`

✅ **REST API працює:**

- GET /users повертає дані
- POST /users створює користувача
- GET /categories працює
- GET /properties працює
- Всі CRUD операції працюють

✅ **Тестування з локального ПК:**

- curl запити працюють
- Swagger UI доступний з браузера
- Відповіді приходять у JSON форматі

---

## 🆘 Вирішення проблем

### Проблема: "Connection refused" при підключенні по SSH

**Рішення:**

1. Перевірте Network Security Group в Azure Portal
2. Переконайтесь що порт 22 відкритий
3. Перевірте правильність IP адреси

### Проблема: Додаток не запускається

**Рішення:**

```bash
# Перевірте логи
sudo journalctl -u flask-app -n 100

# Перевірте синтаксис Python
source venv/bin/activate
python app.py

# Перевірте права доступу
ls -la /home/azureuser/назва_репозиторію
```

### Проблема: "502 Bad Gateway" від Nginx

**Рішення:**

```bash
# Перевірте чи працює Flask додаток
sudo systemctl status flask-app

# Перевірте чи слухає gunicorn на правильному порті
sudo netstat -tulpn | grep 8000

# Перезапустіть сервіси
sudo systemctl restart flask-app
sudo systemctl restart nginx
```

### Проблема: "Can't connect to MySQL server"

**Рішення:**

1. Перевірте firewall rules в Azure MySQL
2. Перевірте правильність DB_HOST в .env
3. Перевірте з VM:

```bash
mysql -h myapp-mysql-server.mysql.database.azure.com -u dbadmin -p
```

### Проблема: Swagger не відображається

**Рішення:**

1. Перевірте логи Nginx
2. Очистіть кеш браузера
3. Перевірте URL: `/api/docs/` (з слешем в кінці)
4. Перевірте що flasgger встановлений: `pip list | grep flasgger`

---

## 💰 Вартість

**Орієнтовна вартість на місяць:**

- **VM Standard_B1s**: ~$7-10/міс (730 годин)
- **Azure MySQL Burstable B1ms**: ~$15-20/міс
- **Public IP**: ~$3/міс
- **Storage**: ~$1-2/міс

**Загалом: ~$26-35/міс**

**Для студентів:**

- Azure for Students: $100 безкоштовних кредитів
- Після здачі лабораторної видаліть ресурси!

```bash
# Видалити всю resource group
az group delete --name myapp-vm-rg --yes --no-wait
```

---

## 📚 Корисні посилання

- Azure Portal: https://portal.azure.com
- Azure CLI: https://docs.microsoft.com/cli/azure/
- Azure VMs: https://docs.microsoft.com/azure/virtual-machines/
- Nginx Documentation: https://nginx.org/en/docs/
- Gunicorn Documentation: https://docs.gunicorn.org/
- Systemd Documentation: https://www.freedesktop.org/software/systemd/man/

---

## 📝 Корисні команди для демонстрації

При здачі лабораторної можете показати:

```bash
# 1. Підключення до VM
ssh -i myapp-vm-key.pem azureuser@ваш_public_ip

# 2. Статус сервісів
sudo systemctl status flask-app
sudo systemctl status nginx

# 3. Процеси
ps aux | grep gunicorn

# 4. Мережеві підключення
sudo netstat -tulpn | grep -E '(80|8000)'

# 5. Тестування з VM
curl http://localhost/users

# 6. Перегляд логів в реальному часі
sudo journalctl -u flask-app -f
```

---

**Успіхів з деплоєм на Azure VM! 🚀**
