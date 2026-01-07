"""Менеджер статуса бота для обмена данными между процессами"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

STATUS_FILE = Path("data/bot_status.json")


class BotStatusManager:
    """Управление статусом бота (для обмена между main.py и telegram_bot)"""
    
    @staticmethod
    def update_status(data: Dict):
        """Обновить статус бота"""
        status = BotStatusManager.get_status()
        status.update(data)
        status['last_update'] = datetime.now().isoformat()
        
        # Создание директории если нет
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def get_status() -> Dict:
        """Получить текущий статус"""
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Статус по умолчанию
        return {
            'trading_enabled': True,
            'sandbox_capital': 1000000.0,
            'live_capital': 1000000.0,
            'sandbox_profit': 0.0,
            'live_profit': 0.0,
            'sandbox_positions': [],
            'live_positions': [],
            'model_status': 'ready',
            'last_update': datetime.now().isoformat()
        }
    
    @staticmethod
    def update_sandbox_capital(capital: float):
        """Обновить капитал sandbox"""
        BotStatusManager.update_status({'sandbox_capital': capital})
    
    @staticmethod
    def update_live_capital(capital: float):
        """Обновить капитал live"""
        BotStatusManager.update_status({'live_capital': capital})
    
    @staticmethod
    def update_sandbox_positions(positions: list):
        """Обновить позиции sandbox"""
        BotStatusManager.update_status({'sandbox_positions': positions})
    
    @staticmethod
    def update_live_positions(positions: list):
        """Обновить позиции live"""
        BotStatusManager.update_status({'live_positions': positions})

