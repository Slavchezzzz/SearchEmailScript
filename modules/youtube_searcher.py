"""Поиск видео на YouTube с улучшенной обработкой ошибок"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time

TIMEOUT = 20  # Увеличим таймаут для надежности

def search_youtube_videos(driver, hashtag, max_videos=5):
    """Поиск видео по хештегу с обработкой всплывающих окон и ожиданием"""
    try:
        print("🌐 Открываю YouTube...")
        driver.get("https://www.youtube.com")
        time.sleep(3)

        # === 1. Закрываем возможные всплывающие окна (cookie, логин и т.д.) ===
        try:
            # Попытка найти и закрыть диалог cookie (селекторы могут меняться)
            cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Accept') or contains(text(), 'Accept') or contains(text(), 'Принять')]")
            if cookie_buttons:
                cookie_buttons[0].click()
                print("🍪 Закрыто окно cookie")
                time.sleep(1)
        except:
            pass  # Если окна нет, просто продолжаем

        # === 2. Ожидание появления и активации поисковой строки ===
        print("🔍 Ожидаю появления поисковой строки...")

        # Используем WebDriverWait с проверкой на кликабельность
        search_box = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.NAME, "search_query"))
        )

        # Дополнительная проверка: убедимся, что поле действительно активно
        # Иногда помогает прокрутка к элементу
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_box)
        time.sleep(0.5)

        print(f"📝 Ввожу хештег: {hashtag}")
        search_box.clear()
        search_box.click()  # Явный клик перед вводом
        search_box.send_keys(hashtag)
        search_box.send_keys(Keys.RETURN)
        print("✅ Поисковый запрос отправлен")

        # === 3. Ожидание загрузки результатов ===
        print("⏳ Жду загрузки результатов...")
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
        )
        time.sleep(2)  # Дополнительная пауза для полной отрисовки

        # === 4. Сбор ссылок на видео ===
        video_data = []
        videos = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")

        print(f"📊 Всего видео на странице: {len(videos)}")
        print(f"🎯 Будет взято: {max_videos} видео")

        for video in videos[:max_videos]:
            try:
                # Прокрутка к каждому видео для гарантии, что оно в зоне видимости
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", video)
                time.sleep(0.3)

                link_element = video.find_element(By.CSS_SELECTOR, "#video-title")
                video_url = link_element.get_attribute("href")
                video_title = link_element.get_attribute("title")

                if video_url:
                    video_data.append({
                        'url': video_url,
                        'title': video_title
                    })
                    print(f"✅ Добавлено: {video_title[:50]}...")
            except Exception as e:
                print(f"⚠️ Ошибка при парсинге видео: {e}")
                continue

        print(f"✅ Итого найдено видео: {len(video_data)}")
        return video_data

    except TimeoutException:
        print("❌ Таймаут: Не удалось найти поисковую строку или результаты.")
        # Попробуем сделать скриншот для отладки (если нужно)
        # driver.save_screenshot("debug_timeout.png")
        return []
    except Exception as e:
        print(f"❌ Ошибка поиска видео: {e}")
        return []