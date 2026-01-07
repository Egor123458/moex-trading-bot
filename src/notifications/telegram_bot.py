"""Telegram бот для уведомлений"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, List
import logging
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Отправка уведомлений в Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = None
        
        if bot_token and chat_id:
            self.bot = Bot(token=bot_token)
            logger.info("Telegram бот инициализирован")
        else:
            logger.warning("Telegram токен или chat_id не указаны")
    
    async def send_message(self, message: str):
        """Отправить текстовое сообщение"""
        if not self.bot:
            logger.warning("Telegram бот не настроен")
            return
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info("Сообщение отправлено в Telegram")
        except TelegramError as e:
            logger.error(f"Ошибка отправки в Telegram: {e}")
    
    async def send_signal_alert(self, signal: Dict):
        """Уведомление о торговом сигнале"""
        ticker = signal.get('ticker', 'N/A')
        price = signal.get('price', 0)
        probability = signal.get('probability', 0)
        signal_type = signal.get('signal', 'HOLD')
        
        message = f"""
🔔 <b>ТОРГОВЫЙ СИГНАЛ</b>

📊 <b>Тикер:</b> {ticker}
💰 <b>Цена:</b> {price:.2f} RUB
📈 <b>Вероятность роста:</b> {probability:.1%}
🎯 <b>Сигнал:</b> {signal_type}

⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""
        await self.send_message(message)
    
    async def send_portfolio_status(self, 
                                   total_capital: float,
                                   cash: float,
                                   invested: float,
                                   cash_growth: float,
                                   invested_growth: float,
                                   total_growth: float,
                                   positions: Optional[List[Dict]] = None):
        """Статус портфеля"""
        
        cash_emoji = "📈" if cash_growth >= 0 else "📉"
        inv_emoji = "📈" if invested_growth >= 0 else "📉"
        total_emoji = "📈" if total_growth >= 0 else "📉"
        
        message = f"""
💼 <b>СТАТУС ПОРТФЕЛЯ</b>

<b>Общий капитал:</b> {total_capital:,.0f} RUB {total_emoji} {total_growth:+.2f}%

<b>Наличные (резерв):</b> {cash:,.0f} RUB {cash_emoji} {cash_growth:+.2f}%
<b>В торговле:</b> {invested:,.0f} RUB {inv_emoji} {invested_growth:+.2f}%

<b>Соотношение:</b> {(invested/total_capital*100):.1f}% в торговле / {(cash/total_capital*100):.1f}% резерв
"""
        
        if positions:
            message += "\n<b>📊 Открытые позиции:</b>\n"
            for pos in positions:
                message += f"  • {pos['ticker']}: {pos['quantity']} шт × {pos['price']:.2f} RUB\n"
        
        message += f"\n⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        
        await self.send_message(message)
    
    async def send_startup_message(self, capital: float):
        """Уведомление о запуске бота"""
        message = f"""
🚀 <b>БОТ ЗАПУЩЕН</b>

Торговый бот MOEX AI успешно запущен!

💰 Начальный капитал: {capital:,.0f} RUB
📊 Режим: ДЕМО (без реальных сделок)
🤖 Модель: XGBoost (ROC-AUC 0.67)

Бот готов к работе! ✅
"""
        await self.send_message(message)
