"""Отслеживание проверенных URL"""
import json
import os
from utils.config import CHECKED_URLS_FILE
from utils.helpers import get_current_datetime

def load_checked_urls():
    """Загружает список уже проверенных URL из файла"""
    checked_urls = set()
    
    if os.path.exists(CHECKED_URLS_FILE):
        try:
            with open(CHECKED_URLS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                checked_urls = set(data.get('checked_urls', []))
            print(f"📁 Загружено проверенных URL: {len(checked_urls)}")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки checked_urls: {e}")
    
    return checked_urls

def save_checked_urls(checked_urls):
    """Сохраняет список проверенных URL в файл"""
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
        
        print(f"💾 Сохранено проверенных URL: {len(checked_urls)}")
        
    except Exception as e:
        print(f"❌ Ошибка сохранения checked_urls: {e}")

def filter_new_videos(video_data, checked_urls):
    """Фильтрует только новые видео, которые еще не проверялись"""
    new_videos = []
    already_checked = []
    
    for video in video_data:
        if video['url'] in checked_urls:
            already_checked.append(video)
        else:
            new_videos.append(video)
    
    print(f"📊 Фильтрация видео:")
    print(f"   - Всего найдено: {len(video_data)}")
    print(f"   - Уже проверено: {len(already_checked)}")
    print(f"   - Новых для проверки: {len(new_videos)}")
    
    return new_videos