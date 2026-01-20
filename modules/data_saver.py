"""Сохранение данных в Excel"""
import pandas as pd
import os
from utils.config import RESULTS_FILE

def save_to_excel(new_data):
    """Сохраняет данные в Excel файл"""
    try:
        # Фильтруем записи с email
        valid_data = [item for item in new_data if item and item['email'] is not None]
        
        if not valid_data:
            print("ℹ️ Нет email для сохранения")
            return 0
        
        df_new = pd.DataFrame(valid_data)
        
        # Проверяем существующий файл
        if os.path.exists(RESULTS_FILE):
            try:
                df_existing = pd.read_excel(RESULTS_FILE)
                
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
                saved_count = len(df_new_unique)
                
            except Exception as e:
                print(f"⚠️ Ошибка чтения существующего файла, создаю новый: {e}")
                df_combined = df_new
                saved_count = len(df_new)
        else:
            df_combined = df_new
            saved_count = len(df_new)
        
        # Создаем папку data если её нет
        os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
        
        # Сохраняем в Excel
        df_combined.to_excel(RESULTS_FILE, index=False, engine='openpyxl')
        print(f"💾 Сохранено в {RESULTS_FILE}: {saved_count} записей")
        
        # Показываем структуру сохраненных данных
        print(f"📋 Структура файла:")
        print(f"   - Столбцы: {list(df_combined.columns)}")
        print(f"   - Всего записей: {len(df_combined)}")
        
        return saved_count
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return 0