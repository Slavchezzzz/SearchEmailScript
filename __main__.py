"""Главный файл программы"""
import time
from modules.browser import setup_driver
from modules.url_tracker import load_checked_urls, save_checked_urls, filter_new_videos, is_video_processed, add_to_history
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
    
    # Загружаем уже проверенные URL из файла (история всех запусков)
    checked_urls = load_checked_urls()
    print(f"📁 Всего в истории: {len(checked_urls)} видео уже обработано в предыдущих запусках")
    
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
        
        print(f"\n🔍 Этап 2: Проверка истории предыдущих запусков...")
        
        # Фильтруем видео - оставляем только те, которых НЕТ в истории
        new_videos = filter_new_videos(video_data, checked_urls)
        
        if not new_videos:
            print("\n🎯 Все найденные видео уже были обработаны в предыдущих запусках!")
            print("💡 Попробуйте другой хештег")
            
            stats = {
                "Всего найдено": len(video_data),
                "Всего в истории": len(checked_urls)
            }
            print_statistics("Статистика", stats)
            return
        
        print(f"\n📹 Этап 3: Анализ {len(new_videos)} новых видео")
        all_results = []
        
        for i, video_info in enumerate(new_videos, 1):
            print(f"\n{'='*50}")
            print(f"🎬 Видео {i} из {len(new_videos)}")
            print(f"{'='*50}")
            
            # Обрабатываем видео
            result = process_video(driver, video_info)
            if result:
                all_results.append(result)
                # Добавляем URL в историю после успешной обработки
                add_to_history(video_info['url'], checked_urls)
                print(f"✅ URL добавлен в историю обработанных видео")
            
            time.sleep(2)
        
        print(f"\n💾 Этап 4: Сохранение результатов...")
        
        # Сохраняем email в Excel
        saved_count = 0
        if all_results:
            saved_count = save_to_excel(all_results)
        
        # Сохраняем ОБНОВЛЕННУЮ историю всех обработанных видео
        save_checked_urls(checked_urls)
        
        # Выводим статистику
        print(f"\n🎉 РАБОТА ЗАВЕРШЕНА!")
        
        stats = {
            "Найдено видео в этом поиске": len(video_data),
            "Обработано новых видео": len(new_videos),
            "Найдено email": len([r for r in all_results if r and r.get('email')]),
            "Сохранено записей": saved_count,
            "Всего в истории (после обновления)": len(checked_urls)
        }
        print_statistics("ФИНАЛЬНАЯ СТАТИСТИКА", stats)
        
        print(f"\n📁 Файлы:")
        print(f"   - Email: data/youtube_emails.xlsx")
        print(f"   - История просмотренных видео: data/checked_urls.json")
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Браузер закрыт")

if __name__ == "__main__":
    main()