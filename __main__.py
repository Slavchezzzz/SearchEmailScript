"""Главный файл программы"""
import time
from modules.browser import setup_driver
from modules.url_tracker import load_checked_urls, save_checked_urls, filter_new_videos
from modules.youtube_searcher import search_youtube_videos
from modules.email_extractor import process_video
from modules.data_saver import save_to_excel
from utils.helpers import print_statistics

def main():
    """Главная функция программы"""
    print("=" * 70)
    print("🎯 ПАРСЕР EMAIL С YOUTUBE - МОДУЛЬНАЯ ВЕРСИЯ")
    print("📊 Лимит: 5 видео | Отслеживание проверенных URL")
    print("=" * 70)
    
    # Загружаем уже проверенные URL
    checked_urls = load_checked_urls()
    
    hashtag = input("Введите хештег (например: #ragetypebeat): ").strip()
    if not hashtag:
        print("❌ Хештег не может быть пустым!")
        return
    
    driver = setup_driver()
    if not driver:
        return
    
    try:
        print(f"\n🔍 Этап 1: Поиск видео с хештегом: {hashtag}")
        video_data = search_youtube_videos(driver, hashtag)
        
        if not video_data:
            print("❌ Видео не найдены!")
            return
        
        print(f"\n🔍 Этап 2: Фильтрация новых видео...")
        new_videos = filter_new_videos(video_data, checked_urls)
        
        if not new_videos:
            print("🎯 Все найденные видео уже проверены ранее!")
            print("💡 Попробуйте другой хештег")
            return
        
        print(f"\n📹 Этап 3: Анализ {len(new_videos)} новых видео")
        all_results = []
        
        for i, video_info in enumerate(new_videos, 1):
            print(f"\n{'='*50}")
            print(f"🎬 Видео {i} из {len(new_videos)}")
            print(f"{'='*50}")
            result = process_video(driver, video_info, checked_urls)
            if result:
                all_results.append(result)
            time.sleep(2)
        
        print(f"\n💾 Этап 4: Сохранение результатов...")
        
        # Сохраняем email в Excel
        saved_count = 0
        if all_results:
            saved_count = save_to_excel(all_results)
        
        # Сохраняем обновленный список проверенных URL
        save_checked_urls(checked_urls)
        
        # Выводим статистику
        print(f"\n🎉 РАБОТА ЗАВЕРШЕНА!")
        
        stats = {
            "Найдено видео": len(video_data),
            "Новых для проверки": len(new_videos),
            "Найдено email": len([r for r in all_results if r['email']]),
            "Сохранено записей": saved_count,
            "Всего проверено URL": len(checked_urls)
        }
        print_statistics("Статистика", stats)
        
        print(f"\n📁 Файлы:")
        print(f"   - Email: data/youtube_emails.xlsx")
        print(f"   - Проверенные URL: data/checked_urls.json")
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Браузер закрыт")

if __name__ == "__main__":
    main()