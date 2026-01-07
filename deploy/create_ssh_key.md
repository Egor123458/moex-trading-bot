# Создание нового SSH ключа

## 1. Создание ключа на Windows

```powershell
# В PowerShell
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\moex-trading-vm-key" -N '""'
```

Или в Git Bash / WSL:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/moex-trading-vm-key -N ""
```

## 2. Получение публичного ключа

```powershell
# Windows PowerShell
Get-Content "$env:USERPROFILE\.ssh\moex-trading-vm-key.pub"
```

Или:
```bash
cat ~/.ssh/moex-trading-vm-key.pub
```

## 3. Добавление ключа на ВМ

### Вариант A: Через панель VK Cloud
1. Зайдите в панель управления VK Cloud
2. Найдите вашу ВМ `moex-trading-vm`
3. Добавьте публичный ключ в настройки ВМ

### Вариант B: Если есть доступ к другой ВМ или root доступ
Подключитесь к ВМ другим способом и добавьте ключ:
```bash
# На ВМ
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ВАШ_ПУБЛИЧНЫЙ_КЛЮЧ" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 4. Подключение с новым ключом

```powershell
ssh -i "$env:USERPROFILE\.ssh\moex-trading-vm-key" ubuntu@89.208.197.34
```

