"""Управление браузером"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

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
        
        # Путь к драйверу
        driver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drivers', 'chromedriver.exe')
        
        if not os.path.exists(driver_path):
            print("❌ ChromeDriver не найден!")
            print("📥 Скачайте с: https://chromedriver.chromium.org/")
            print(f"💾 Сохраните в: {driver_path}")
            return None
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Браузер запущен")
        return driver
        
    except Exception as e:
        print(f"❌ Ошибка запуска браузера: {e}")
        return None