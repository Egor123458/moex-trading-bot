.PHONY: help deploy update restart logs status stop start install

help:
	@echo "Доступные команды:"
	@echo "  make install    - Установка зависимостей"
	@echo "  make deploy     - Развертывание на ВМ"
	@echo "  make update     - Обновление кода и зависимостей"
	@echo "  make start      - Запуск сервиса"
	@echo "  make stop       - Остановка сервиса"
	@echo "  make restart    - Перезапуск сервиса"
	@echo "  make status     - Статус сервиса"
	@echo "  make logs       - Просмотр логов"

install:
	pip install -r requirements.txt

deploy:
	@echo "Развертывание на ВМ..."
	@echo "Выполните на ВМ: sudo ./deploy/deploy.sh"

update:
	@echo "Обновление..."
	@echo "Выполните на ВМ: sudo ./deploy/update.sh"

start:
	sudo systemctl start moex-trading-bot

stop:
	sudo systemctl stop moex-trading-bot

restart:
	sudo systemctl restart moex-trading-bot

status:
	sudo systemctl status moex-trading-bot

logs:
	sudo journalctl -u moex-trading-bot -f
