"""Отслеживание проверенных URL"""
import json
import os
from datetime import datetime

# Путь к файлу с историей
CHECKED_URLS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'checked_urls.json')

def get_current_datetime():
    """Возвращает текущую дату и время"""
    return {
        'formatted': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'iso': datetime.now().isoformat()
    }

def load_checked_urls():
    """Загружает список уже проверенных URL из файла (история всех запусков)"""
    checked_urls = set()
    
    if os.path.exists(CHECKED_URLS_FILE):
        try:
            with open(CHECKED_URLS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                checked_urls = set(data.get('checked_urls', []))
            print(f"📁 Загружена история: {len(checked_urls)} видео уже обработано")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки истории: {e}")
    else:
        print("📁 История отсутствует, будет создана новая")
    
    return checked_urls

def save_checked_urls(checked_urls):
    """Сохраняет обновленную историю всех обработанных видео"""
    try:
        # Создаем папку data если её нет
        os.makedirs(os.path.dirname(CHECKED_URLS_FILE), exist_ok=True)
        
        data = {
            'checked_urls': list(checked_urls),
            'last_update': get_current_datetime()['iso'],
            'total_checked': len(checked_urls)
        }
        
        with open(CHECKED_URLS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 История обновлена: теперь {len(checked_urls)} видео в истории")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сохранения истории: {e}")
        return False

def filter_new_videos(video_data, checked_urls):
    """Фильтрует видео, оставляя только те, которых нет в истории"""
    new_videos = []
    already_processed = []
    
    for video in video_data:
        if video['url'] in checked_urls:
            already_processed.append(video)
        else:
            new_videos.append(video)
    
    print(f"\n📊 Фильтрация по истории:")
    print(f"   - Всего найдено видео: {len(video_data)}")
    print(f"   - Уже в истории: {len(already_processed)}")
    print(f"   - Новых для обработки: {len(new_videos)}")
    
    if already_processed:
        print(f"\n⏭️ Пропущенные видео (уже в истории):")
        for i, video in enumerate(already_processed[:3], 1):
            print(f"   {i}. {video['title'][:50]}...")
        if len(already_processed) > 3:
            print(f"   ... и еще {len(already_processed) - 3}")
    
    return new_videos

def is_video_processed(url, checked_urls):
    """Проверяет, было ли видео уже обработано в предыдущих запусках"""
    return url in checked_urls

def add_to_history(url, checked_urls):
    """Добавляет видео в историю обработанных"""
    checked_urls.add(url)
    return checked_urls

def get_history_stats(checked_urls):
    """Возвращает статистику по истории"""
    return {
        'total': len(checked_urls),
        'sample': list(checked_urls)[:5]  # Первые 5 для примера
    }