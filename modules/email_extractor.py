"""Извлечение email из описания видео"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

DESCRIPTION_SELECTORS = [
    "#description",
    "ytd-text-inline-expander",
    ".ytd-video-secondary-info-renderer",
    "ytd-video-description-renderer"
]

def expand_description_element(driver):
    """Раскрывает описание видео"""
    try:
        print("📖 Пытаюсь раскрыть описание...")
        
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        
        # ПРАВИЛЬНЫЙ СЕЛЕКТОР ДЛЯ КНОПКИ "ЕЩЕ"
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
        
        # Используем селекторы
        for selector in DESCRIPTION_SELECTORS:
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

def extract_emails(text):
    """Извлекает email из текста"""
    if not text:
        return []
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def find_email_in_description(driver):
    try:
        print("🔎 Ищу email в описании...")
        expanded = expand_description_element(driver)
        print(f"📌 Описание раскрыто: {expanded}")
        
        description_text = get_description_text(driver)
        
        if not description_text:
            print("❌ Не удалось получить текст описания")
            return None
        
        # Выводим начало текста для проверки
        print(f"📄 Первые 500 символов описания:\n{description_text[:500]}")
        
        emails = extract_emails(description_text)
        
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

def process_video(driver, video_info):
    """Обрабатывает одно видео и ищет email"""
    from datetime import datetime
    
    try:
        print(f"\n🎬 Обрабатываю видео: {video_info['title'][:50]}...")
        print(f"🔗 Ссылка: {video_info['url']}")
        
        driver.get(video_info['url'])
        time.sleep(4)
        
        email = find_email_in_description(driver)
        
        return {
            'video_url': video_info['url'],
            'video_title': video_info['title'],
            'email': email,
            'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"❌ Ошибка обработки видео: {e}")
        return None