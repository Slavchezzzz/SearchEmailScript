"""Поиск видео на YouTube"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

TIMEOUT = 15

def search_youtube_videos(driver, hashtag, max_videos=5):
    """Поиск видео по хештегу с параметром max_videos"""
    try:
        print("🌐 Открываю YouTube...")
        driver.get("https://www.youtube.com")
        time.sleep(3)
        
        print("🔍 Нахожу поисковую строку...")
        search_box = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.NAME, "search_query"))
        )
        
        print(f"📝 Ввожу хештег: {hashtag}")
        search_box.clear()
        search_box.send_keys(hashtag)
        search_box.send_keys(Keys.RETURN)
        
        print("⏳ Жду результаты поиска...")
        time.sleep(5)
        
        # Ждем загрузки результатов
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
        )
        
        # Собираем ссылки на видео
        video_data = []
        videos = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
        
        print(f"📊 Всего видео на странице: {len(videos)}")
        print(f"🎯 Будет взято: {max_videos} видео")
        
        # Берем только нужное количество
        for video in videos[:max_videos]:
            try:
                link_element = video.find_element(By.CSS_SELECTOR, "#video-title")
                video_url = link_element.get_attribute("href")
                video_title = link_element.get_attribute("title")
                
                if video_url:
                    video_data.append({
                        'url': video_url,
                        'title': video_title
                    })
                    print(f"✅ Добавлено видео: {video_title[:50]}...")
            except Exception as e:
                print(f"⚠️ Ошибка при парсинге видео: {e}")
                continue
        
        print(f"✅ Итого найдено видео: {len(video_data)}")
        return video_data
        
    except Exception as e:
        print(f"❌ Ошибка поиска видео: {e}")
        return []