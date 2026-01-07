"""Telegram бот с меню для управления торговым ботом"""

import logging
from typing import Optional
from datetime import datetime
import json

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("python-telegram-bot не установлен. Установите: pip install python-telegram-bot")

from config.settings import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram бот с меню управления"""
    
    def __init__(self, token: str, chat_id: str):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("Установите: pip install python-telegram-bot")
        
        self.token = token
        self.chat_id = chat_id
        self.application = None
        self.trading_enabled = True
        self.bot_status = {}
        
        logger.info("TelegramBot инициализирован")
    
    def start(self):
        """Запуск бота"""
        if not self.token:
            logger.warning("Telegram токен не указан")
            return
        
        self.application = Application.builder().token(self.token).build()
        
        # Обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("trading", self.trading_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
        
        # Обработчик callback кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Запуск
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Telegram бот запущен")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await self.send_main_menu(update.message.chat_id)
    
    async def send_main_menu(self, chat_id: int):
        """Отправка главного меню"""
        # Статус бота
        status_text = self.get_status_text()
        
        # Кнопки навигации
        keyboard = [
            [
                InlineKeyboardButton("📊 Портфель", callback_data="portfolio"),
                InlineKeyboardButton("📈 Статус", callback_data="status")
            ],
            [
                InlineKeyboardButton("🤖 Обучение модели", callback_data="train"),
                InlineKeyboardButton("💰 Торговля", callback_data="trading")
            ],
            [
                InlineKeyboardButton("⛔ Выключить торги", callback_data="disable_trading")
            ],
            [
                InlineKeyboardButton("🔄 Обновить", callback_data="refresh"),
                InlineKeyboardButton("🛑 СТОП", callback_data="stop")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=status_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    def get_status_text(self) -> str:
        """Формирование текста статуса"""
        trading_status = "✅ Активна" if self.trading_enabled else "❌ Выключена"
        model_status = "✅ Готова"  # TODO: проверка модели
        capital = settings.trading.INITIAL_CAPITAL
        profit = 0.0  # TODO: расчет прибыли
        
        status = f"""
⚡ <b>Торговля</b> {trading_status}

📊 <b>Статус бота</b> ({datetime.now().strftime('%d.%m.%Y %H:%M')})

💰 <b>Торговля:</b> {trading_status}
🤖 <b>Модель:</b> {model_status}
💵 <b>Капитал:</b> {capital:,.0f} ₽
📈 <b>Прибыль:</b> {profit:+.2f}%
        """.strip()
        
        return status
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "portfolio":
            await self.portfolio_command(query.message, context)
        elif data == "status":
            await self.status_command(query.message, context)
        elif data == "trading":
            await self.trading_command(query.message, context)
        elif data == "train":
            await query.message.reply_text("🤖 Обучение модели...\n\nФункция в разработке")
        elif data == "disable_trading":
            self.trading_enabled = False
            await query.message.reply_text("⛔ Торговля выключена")
            await self.send_main_menu(query.message.chat_id)
        elif data == "refresh":
            await self.send_main_menu(query.message.chat_id)
        elif data == "stop":
            await self.stop_command(query.message, context)
    
    async def status_command(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Команда статуса"""
        status_text = self.get_status_text()
        await update.reply_text(status_text, parse_mode='HTML')
    
    async def portfolio_command(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Команда портфеля"""
        # TODO: получение реального портфеля
        portfolio_text = """
📊 <b>Портфель</b>

Позиции:
• SBER: 10 лотов
• GAZP: 5 лотов

Общая стоимость: 1,000,000 ₽
        """
        await update.reply_text(portfolio_text, parse_mode='HTML')
    
    async def trading_command(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Команда торговли"""
        trading_text = f"""
💰 <b>Торговля</b>

Статус: {'✅ Активна' if self.trading_enabled else '❌ Выключена'}
Режим: {settings.MODE}

Последние сделки:
• Нет сделок
        """
        await update.reply_text(trading_text, parse_mode='HTML')
    
    async def stop_command(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Команда остановки"""
        await update.reply_text("🛑 Остановка бота...")
        # TODO: остановка основного процесса


class TelegramNotifier:
    """Простой уведомитель (для обратной совместимости)"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """Отправить сообщение"""
        try:
            import requests
            url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Ошибка отправки в Telegram: {e}")
            return False
    
    def send_trade_alert(self, trade_info: dict):
        """Отправить уведомление о сделке"""
        message = f"""
🔔 <b>Новая сделка</b>

Тикер: {trade_info.get('ticker', 'N/A')}
Действие: {trade_info.get('action', 'N/A')}
Цена: {trade_info.get('price', 0):.2f} ₽
        """
        self.send_message(message.strip())
    
    def send_error_alert(self, error_msg: str):
        """Отправить уведомление об ошибке"""
        message = f"⚠️ <b>ОШИБКА</b>\n\n{error_msg}"
        self.send_message(message)
