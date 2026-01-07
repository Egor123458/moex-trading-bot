"""Анализ тональности финансовых новостей"""

import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Анализ тональности новостей"""
    
    def __init__(self):
        # Словарь позитивных/негативных слов для финансовых новостей (русский)
        self.positive_words = {
            'рост', 'прибыль', 'увеличение', 'повышение', 'успех', 
            'достижение', 'развитие', 'улучшение', 'позитив', 'подъем',
            'дивиденды', 'выручка', 'инвестиции', 'расширение'
        }
        
        self.negative_words = {
            'падение', 'убыток', 'снижение', 'кризис', 'проблема',
            'риск', 'угроза', 'спад', 'дефицит', 'потеря', 'долг',
            'санкции', 'штраф', 'банкротство', 'сокращение'
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Анализ тональности текста
        
        Args:
            text: Текст новости
        
        Returns:
            Dict {'sentiment': 'positive'|'negative'|'neutral', 'score': float, 'confidence': float}
        """
        if not text:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        # Приводим к нижнему регистру
        text_lower = text.lower()
        
        # Токенизация (упрощенная)
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Подсчет позитивных/негативных слов
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        # Расчет score
        score = (positive_count - negative_count) / len(words)
        confidence = total_count / len(words)
        
        # Определение тональности
        if score > 0.01:
            sentiment = 'positive'
        elif score < -0.01:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def analyze_news_batch(self, news_list: List[Dict]) -> Dict:
        """
        Анализ пакета новостей
        
        Args:
            news_list: Список новостей
        
        Returns:
            Агрегированный sentiment
        """
        if not news_list:
            return {'overall_sentiment': 'neutral', 'average_score': 0.0}
        
        sentiments = []
        scores = []
        
        for news in news_list:
            text = f"{news.get('title', '')} {news.get('text', '')}"
            result = self.analyze_sentiment(text)
            sentiments.append(result['sentiment'])
            scores.append(result['score'])
        
        # Агрегация
        avg_score = sum(scores) / len(scores)
        
        positive_count = sentiments.count('positive')
        negative_count = sentiments.count('negative')
        
        if positive_count > negative_count:
            overall = 'positive'
        elif negative_count > positive_count:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'overall_sentiment': overall,
            'average_score': avg_score,
            'positive_news': positive_count,
            'negative_news': negative_count,
            'neutral_news': len(sentiments) - positive_count - negative_count,
            'total_news': len(sentiments)
        }
