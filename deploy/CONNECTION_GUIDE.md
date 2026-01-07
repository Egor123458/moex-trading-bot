# 🔐 Руководство по подключению к ВМ

## Проблема: Ключ не найден

Если у вас нет файла ключа `moex-trading-vm-0x5ulVyq.pem`, используйте один из вариантов ниже.

## Вариант 1: Веб-консоль VK Cloud (самый простой)

1. Зайдите в панель управления VK Cloud: https://msk.cloud.vk.com
2. Найдите ВМ `moex-trading-vm` (ID: b7a6c8b9-e68a-4f6f-b646-90f656a784c7)
3. Нажмите "Подключиться" → "Веб-консоль"
4. Войдите с пользователем `ubuntu` (пароль должен быть указан при создании ВМ)

## Вариант 2: Создание нового SSH ключа

### Шаг 1: Создайте ключ

**В PowerShell:**
```powershell
# Создание директории для ключей (если нет)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.ssh"

# Создание ключа
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\moex-trading-vm-key" -N '""'
```

**В Git Bash или WSL:**
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/moex-trading-vm-key -N ""
```

### Шаг 2: Получите публичный ключ

**PowerShell:**
```powershell
Get-Content "$env:USERPROFILE\.ssh\moex-trading-vm-key.pub"
```

**Git Bash/WSL:**
```bash
cat ~/.ssh/moex-trading-vm-key.pub
```

Скопируйте весь вывод (начинается с `ssh-rsa ...`)

### Шаг 3: Добавьте ключ на ВМ

**Через веб-консоль VK Cloud:**
1. Зайдите в панель управления
2. Найдите вашу ВМ
3. В настройках добавьте публичный ключ

**Или через веб-консоль на ВМ:**
```bash
# Войдите через веб-консоль, затем:
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# Вставьте ваш публичный ключ, сохраните (Ctrl+O, Enter, Ctrl+X)
chmod 600 ~/.ssh/authorized_keys
```

### Шаг 4: Подключитесь

**PowerShell:**
```powershell
ssh -i "$env:USERPROFILE\.ssh\moex-trading-vm-key" ubuntu@89.208.197.34
```

**Git Bash/WSL:**
```bash
ssh -i ~/.ssh/moex-trading-vm-key ubuntu@89.208.197.34
```

## Вариант 3: Поиск существующего ключа

Ключ мог быть сохранен в разных местах:

### Проверьте эти папки:

```powershell
# Загрузки
Get-ChildItem "$env:USERPROFILE\Downloads" -Filter "*.pem" -Recurse

# Рабочий стол
Get-ChildItem "$env:USERPROFILE\Desktop" -Filter "*.pem" -Recurse

# Документы
Get-ChildItem "$env:USERPROFILE\Documents" -Filter "*.pem" -Recurse

# .ssh папка
Get-ChildItem "$env:USERPROFILE\.ssh" -Filter "*.pem" -ErrorAction SilentlyContinue
```

### Или поиск по всему диску (может быть долго):

```powershell
Get-ChildItem C:\ -Filter "*moex*" -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.Extension -eq ".pem"}
```

## Вариант 4: Скачать ключ из VK Cloud

1. Зайдите в панель управления VK Cloud
2. Перейдите в раздел "Ключевые пары" или "SSH Keys"
3. Найдите ключ `moex-trading-vm-0x5ulVyq`
4. Скачайте приватный ключ (если доступно)

## После подключения

После успешного подключения выполните:

```bash
# Получение root прав
sudo bash

# Затем запустите развертывание
cd /tmp
git clone https://github.com/Egor123458/moex-trading-bot.git
cd moex-trading-bot
chmod +x deploy/quick_start.sh
./deploy/quick_start.sh
```

## Устранение проблем

### Ошибка "Permission denied"

Исправьте права на ключ:
```powershell
# Windows (если используете WSL/Git Bash)
icacls "путь\к\ключу.pem" /inheritance:r
icacls "путь\к\ключу.pem" /grant:r "%username%:R"
```

Или в Git Bash:
```bash
chmod 400 путь/к/ключу.pem
```

### Ошибка "Host key verification failed"

```powershell
ssh-keygen -R 89.208.197.34
```

### Проверка доступности ВМ

```powershell
Test-NetConnection -ComputerName 89.208.197.34 -Port 22
```

Или:
```bash
ping 89.208.197.34
telnet 89.208.197.34 22
```

