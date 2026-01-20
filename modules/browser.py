"""Управление браузером"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

def setup_driver():
    """Настройка браузера"""
    try:
        from utils.config import CHROME_OPTIONS
        
        options = webdriver.ChromeOptions()
        
        # Добавляем опции из конфига
        for option in CHROME_OPTIONS:
            if option:  # Пропускаем пустые строки
                options.add_argument(option)
        
        # Путь к драйверу
        drivers_dir = os.path.join(os.path.dirname(__file__), '..', 'drivers')
        driver_path = os.path.join(drivers_dir, 'chromedriver.exe')
        
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