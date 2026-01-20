"""Вспомогательные функции"""
from datetime import datetime
import re

def get_current_datetime():
    """Возвращает текущую дату и время в разных форматах"""
    return {
        'formatted': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'iso': datetime.now().isoformat()
    }

def extract_emails(text):
    """Извлекает email из текста с помощью регулярного выражения"""
    if not text:
        return []
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def print_statistics(title, stats_dict):
    """Красиво печатает статистику"""
    print(f"\n📊 {title}:")
    for key, value in stats_dict.items():
        print(f"   - {key}: {value}")