from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os
import re
import json
from datetime import datetime

def setup_driver():
    """Настройка браузера"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        
        # РАСКОММЕНТИРУЙТЕ ДЛЯ ОКНА БРАУЗЕРА:
        options.add_argument("--start-maximized")
        
        driver_path = os.path.join(os.path.dirname(__file__), 'drivers', 'chromedriver.exe')
        
        if not os.path.exists(driver_path):
            print("❌ ChromeDriver не найден!")
            print("📥 Скачайте с: https://chromedriver.chromium.org/")
            return None
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Браузер запущен")
        return driver
        
    except Exception as e:
        print(f"❌ Ошибка запуска браузера: {e}")
        return None

def load_checked_urls():
    """Загружает список уже проверенных URL из файла"""
    checked_urls_file = "checked_urls.json"
    checked_urls = set()
    
    if os.path.exists(checked_urls_file):
        try:
            with open(checked_urls_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                checked_urls = set(data.get('checked_urls', []))
            print(f"📁 Загружено проверенных URL: {len(checked_urls)}")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки checked_urls: {e}")
    
    return checked_urls

def save_checked_urls(checked_urls):
    """Сохраняет список проверенных URL в файл"""
    checked_urls_file = "checked_urls.json"
    try:
        data = {
            'checked_urls': list(checked_urls),
            'last_update': datetime.now().isoformat(),
            'total_checked': len(checked_urls)
        }
        with open(checked_urls_file, 'w', encoding='utf-8') as f:
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

def search_youtube_videos(driver, hashtag):
    """Поиск видео по хештегу"""
    try:
        print("🌐 Открываю YouTube...")
        driver.get("https://www.youtube.com")
        time.sleep(3)
        
        print("🔍 Нахожу поисковую строку...")
        search_box = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.NAME, "search_query"))
        )
        
        print(f"📝 Ввожу хештег: {hashtag}")
        search_box.clear()
        search_box.send_keys(hashtag)
        search_box.send_keys(Keys.RETURN)
        
        print("⏳ Жду результаты поиска...")
        time.sleep(5)
        
        # Собираем ссылки на видео - ЛИМИТ 5 ВИДЕО
        video_data = []
        videos = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")[:5]
        
        for video in videos:
            try:
                link_element = video.find_element(By.CSS_SELECTOR, "#video-title")
                video_url = link_element.get_attribute("href")
                video_title = link_element.get_attribute("title")
                
                if video_url:
                    video_data.append({
                        'url': video_url,
                        'title': video_title
                    })
            except:
                continue
        
        print(f"✅ Найдено видео: {len(video_data)}")
        return video_data
        
    except Exception as e:
        print(f"❌ Ошибка поиска видео: {e}")
        return []

def expand_description_element(driver):
    """Раскрывает описание видео"""
    try:
        print("📖 Пытаюсь раскрыть описание...")
        
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        
        # 🔥 ПРАВИЛЬНЫЙ СЕЛЕКТОР ДЛЯ КНОПКИ "ЕЩЕ"
        try:
            expand_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-button#expand"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", expand_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", expand_button)
            print("✅ Кнопка 'Еще' нажата")
            time.sleep(2)
            return True
        except:
            pass
        
        # Альтернативные способы поиска кнопки
        try:
            expand_buttons = driver.find_elements(By.CSS_SELECTOR, "tp-yt-paper-button")
            for button in expand_buttons:
                if "еще" in button.text.lower() or "more" in button.text.lower():
                    driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", button)
                    print("✅ Кнопка 'Еще' нажата (альтернативный способ)")
                    time.sleep(2)
                    return True
        except:
            pass
        
        print("❌ Не удалось найти кнопку 'Еще'")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка при раскрытии описания: {e}")
        return False

def get_description_text(driver):
    """Получает текст описания после раскрытия"""
    try:
        print("🔍 Получаю текст описания...")
        time.sleep(3)
        
        description_selectors = [
            "#description",
            "ytd-text-inline-expander",
            ".ytd-video-secondary-info-renderer",
            "ytd-video-description-renderer"
        ]
        
        for selector in description_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text
                    if text and len(text.strip()) > 10:
                        print(f"📄 Найден текст описания: {len(text)} символов")
                        return text
            except:
                continue
        
        # Если не нашли в селекторах
        try:
            body_text = driver.find_element(By.TAG_NAME, 'body').text
            if body_text and len(body_text) > 100:
                print(f"📄 Использую общий текст страницы: {len(body_text)} символов")
                return body_text
        except:
            pass
        
        print("❌ Не удалось получить текст описания")
        return ""
        
    except Exception as e:
        print(f"❌ Ошибка получения текста: {e}")
        return ""

def find_email_in_description(driver):
    """Ищет email в описании видео"""
    try:
        print("🔎 Ищу email в описании...")
        
        description_expanded = expand_description_element(driver)
        
        if not description_expanded:
            print("⚠️ Не удалось раскрыть описание, пробую искать в доступном тексте...")
        
        description_text = get_description_text(driver)
        
        if not description_text:
            print("❌ Не удалось получить текст описания")
            return None
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, description_text)
        
        if emails:
            found_email = emails[0]
            print(f"✅ Найден email: {found_email}")
            return found_email
        else:
            print("❌ Email в описании не найден")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка поиска email: {e}")
        return None

def process_video(driver, video_info, checked_urls):
    """Обрабатывает одно видео и ищет email"""
    try:
        print(f"\n🎬 Обрабатываю видео: {video_info['title'][:50]}...")
        print(f"🔗 Ссылка: {video_info['url']}")
        
        driver.get(video_info['url'])
        time.sleep(4)
        
        email = find_email_in_description(driver)
        
        # 🔥 ДОБАВЛЯЕМ URL В ПРОВЕРЕННЫЕ ВНЕ ЗАВИСИМОСТИ ОТ РЕЗУЛЬТАТА
        checked_urls.add(video_info['url'])
        
        return {
            'video_url': video_info['url'],
            'video_title': video_info['title'],
            'email': email,
            'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'checked_date': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Ошибка обработки видео: {e}")
        # Даже при ошибке отмечаем URL как проверенный
        checked_urls.add(video_info['url'])
        return None

def save_to_excel(new_data, filename="youtube_emails.xlsx"):
    """Сохраняет данные в Excel файл"""
    try:
        # Фильтруем записи с email
        valid_data = [item for item in new_data if item and item['email'] is not None]
        
        if not valid_data:
            print("ℹ️ Нет email для сохранения")
            return 0
        
        df_new = pd.DataFrame(valid_data)
        
        # Проверяем существующий файл
        if os.path.exists(filename):
            df_existing = pd.read_excel(filename)
            
            # Проверяем уникальность
            existing_emails = set(df_existing['email'].dropna().astype(str))
            existing_urls = set(df_existing['video_url'].astype(str))
            
            # Фильтруем новые данные
            mask = ~(
                df_new['email'].isin(existing_emails) | 
                df_new['video_url'].isin(existing_urls)
            )
            df_new_unique = df_new[mask]
            
            if df_new_unique.empty:
                print("ℹ️ Все email уже есть в файле")
                return 0
            
            df_combined = pd.concat([df_existing, df_new_unique], ignore_index=True)
        else:
            df_combined = df_new
        
        # Сохраняем в Excel
        df_combined.to_excel(filename, index=False, engine='openpyxl')
        saved_count = len(df_new) if not os.path.exists(filename) else len(df_new_unique)
        print(f"💾 Сохранено в {filename}: {saved_count} записей")
        
        return saved_count
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return 0

def main():
    """Главная функция программы"""
    print("=" * 70)
    print("🎯 ПАРСЕР EMAIL С YOUTUBE - С СИСТЕМОЙ ОТСЛЕЖИВАНИЯ URL")
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
        if all_results:
            saved_count = save_to_excel(all_results)
        else:
            saved_count = 0
        
        # 🔥 СОХРАНЯЕМ ОБНОВЛЕННЫЙ СПИСОК ПРОВЕРЕННЫХ URL
        save_checked_urls(checked_urls)
        
        print(f"\n🎉 РАБОТА ЗАВЕРШЕНА!")
        print(f"📊 Статистика:")
        print(f"   - Найдено видео: {len(video_data)}")
        print(f"   - Новых для проверки: {len(new_videos)}")
        print(f"   - Найдено email: {len([r for r in all_results if r['email']])}")
        print(f"   - Сохранено записей: {saved_count}")
        print(f"   - Всего проверено URL: {len(checked_urls)}")
        print(f"📁 Файлы:")
        print(f"   - Email: youtube_emails.xlsx")
        print(f"   - Проверенные URL: checked_urls.json")
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Браузер закрыт")

if __name__ == "__main__":
    main()