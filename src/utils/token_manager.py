"""Менеджер для работы с несколькими токенами Tinkoff"""

import random
import logging
from typing import List, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class TokenManager:
    """Управление несколькими токенами Tinkoff с ротацией и балансировкой"""
    
    def __init__(self, tokens: Optional[List[str]] = None):
        """
        Args:
            tokens: Список токенов. Если None, берется из settings
        """
        self.tokens = tokens or settings.api.get_all_tokens()
        self.current_index = 0
        self.failed_tokens = set()  # Токены, которые не работают
        
        if not self.tokens:
            logger.warning("Список токенов пуст!")
        else:
            logger.info(f"Инициализирован TokenManager с {len(self.tokens)} токенами")
    
    def get_token(self, strategy: str = 'round_robin') -> Optional[str]:
        """
        Получить токен по выбранной стратегии
        
        Args:
            strategy: 'round_robin' - по кругу, 'random' - случайный, 'first' - первый
        
        Returns:
            Токен или None если нет доступных
        """
        available_tokens = [t for i, t in enumerate(self.tokens) 
                          if i not in self.failed_tokens]
        
        if not available_tokens:
            logger.error("Нет доступных токенов!")
            # Сброс failed_tokens если все токены не работают
            self.failed_tokens.clear()
            available_tokens = self.tokens
        
        if not available_tokens:
            return None
        
        if strategy == 'round_robin':
            token = available_tokens[self.current_index % len(available_tokens)]
            self.current_index = (self.current_index + 1) % len(available_tokens)
            return token
        
        elif strategy == 'random':
            return random.choice(available_tokens)
        
        elif strategy == 'first':
            return available_tokens[0]
        
        else:
            return available_tokens[0]
    
    def mark_token_failed(self, token: str):
        """Пометить токен как неработающий"""
        try:
            index = self.tokens.index(token)
            self.failed_tokens.add(index)
            logger.warning(f"Токен #{index} помечен как неработающий")
        except ValueError:
            pass
    
    def mark_token_working(self, token: str):
        """Пометить токен как работающий"""
        try:
            index = self.tokens.index(token)
            self.failed_tokens.discard(index)
            logger.info(f"Токен #{index} восстановлен")
        except ValueError:
            pass
    
    def get_all_tokens(self) -> List[str]:
        """Получить все токены"""
        return self.tokens.copy()
    
    def get_available_count(self) -> int:
        """Получить количество доступных токенов"""
        return len(self.tokens) - len(self.failed_tokens)


# Глобальный экземпляр менеджера
token_manager = TokenManager()

