"""Telegram бот с меню для управления торговым ботом"""

import sys
import logging
from typing import Optional
from datetime import datetime
from pathlib import Path
import json

# Добавляем корневую папку в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("python-telegram-bot не установлен. Установите: pip install python-telegram-bot")

try:
    from config.settings import settings
except ImportError:
    # Fallback если импорт не работает
    import os
    from dotenv import load_dotenv
    load_dotenv()
    settings = type('Settings', (), {
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN', ''),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID', ''),
        'trading': type('Trading', (), {'INITIAL_CAPITAL': float(os.getenv('INITIAL_CAPITAL', 1000000))})(),
        'MODE': os.getenv('MODE', 'paper_trading')
    })()

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
        
        # Импорт менеджера статуса
        try:
            from src.monitoring.bot_status_manager import BotStatusManager
            self.status_manager = BotStatusManager
        except ImportError:
            self.status_manager = None
        
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
        """Формирование текста статуса с информацией о двух моделях"""
        trading_status = "✅ Активна" if self.trading_enabled else "❌ Выключена"
        model_status = "✅ Готова"
        
        # Получение информации о капитале из файла статуса
        if self.status_manager:
            bot_status = self.status_manager.get_status()
            self.trading_enabled = bot_status.get('trading_enabled', True)
            sandbox_capital = bot_status.get('sandbox_capital', settings.trading.INITIAL_CAPITAL)
            live_capital = bot_status.get('live_capital', settings.trading.INITIAL_CAPITAL)
            sandbox_profit = bot_status.get('sandbox_profit', 0.0)
            live_profit = bot_status.get('live_profit', 0.0)
        else:
            sandbox_capital = settings.trading.INITIAL_CAPITAL
            live_capital = settings.trading.INITIAL_CAPITAL
            sandbox_profit = 0.0
            live_profit = 0.0
        
        # Определение режима работы
        mode_text = ""
        if settings.MODE == 'dual_mode':
            mode_text = "🔄 Dual Mode (Sandbox + Live)"
        elif settings.MODE == 'paper_trading':
            mode_text = "🧪 Paper Trading (Sandbox)"
        elif settings.MODE == 'live_trading':
            mode_text = "💰 Live Trading"
        
        status = f"""
⚡ <b>Торговля</b> {trading_status}

📊 <b>Статус бота</b> ({datetime.now().strftime('%d.%m.%Y %H:%M')})

{mode_text}

<b>🧪 SANDBOX (Тестирование):</b>
💰 Капитал: {sandbox_capital:,.0f} ₽
📈 Прибыль: {sandbox_profit:+.2f}%
🤖 Модель: {model_status}

<b>💰 LIVE (Реальная торговля):</b>
💰 Капитал: {live_capital:,.0f} ₽
📈 Прибыль: {live_profit:+.2f}%
🤖 Модель: {model_status}
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
            if self.status_manager:
                self.status_manager.update_status({'trading_enabled': False})
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
        # Получение информации из файла статуса
        if self.status_manager:
            bot_status = self.status_manager.get_status()
            sandbox_positions = bot_status.get('sandbox_positions', [])
            live_positions = bot_status.get('live_positions', [])
            sandbox_capital = bot_status.get('sandbox_capital', 0)
            live_capital = bot_status.get('live_capital', 0)
        else:
            sandbox_positions = []
            live_positions = []
            sandbox_capital = 0
            live_capital = 0
        
        portfolio_text = f"""
📊 <b>Портфель</b>

<b>🧪 SANDBOX:</b>
"""
        if sandbox_positions:
            for pos in sandbox_positions[:5]:  # Показываем первые 5
                portfolio_text += f"• {pos.get('ticker', 'N/A')}: {pos.get('quantity', 0)} лотов\n"
        else:
            portfolio_text += "Нет открытых позиций\n"
        
        portfolio_text += f"Общая стоимость: {sandbox_capital:,.0f} ₽\n\n"
        portfolio_text += f"<b>💰 LIVE:</b>\n"
        
        if live_positions:
            for pos in live_positions[:5]:
                portfolio_text += f"• {pos.get('ticker', 'N/A')}: {pos.get('quantity', 0)} лотов\n"
        else:
            portfolio_text += "Нет открытых позиций\n"
        
        portfolio_text += f"Общая стоимость: {live_capital:,.0f} ₽"
        
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
