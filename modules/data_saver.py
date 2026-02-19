"""Сохранение данных в Excel"""
import pandas as pd
import os

RESULTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'youtube_emails.xlsx')

def save_to_excel(new_data):
    try:
        print(f"📥 В save_to_excel получено {len(new_data)} записей")
        
        # Фильтруем записи с email
        valid_data = [item for item in new_data if item and item.get('email') is not None]
        print(f"📧 Из них с email: {len(valid_data)}")
        
        if not valid_data:
            print("ℹ️ Нет email для сохранения")
            return 0
        
        # Выводим сами email для контроля
        for item in valid_data:
            print(f"   - {item.get('email')} - {item.get('video_title')[:30]}...")
        
        df_new = pd.DataFrame(valid_data)
        print(f"📊 DataFrame создан, форма: {df_new.shape}")
        
        os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
        
        if os.path.exists(RESULTS_FILE):
            try:
                df_existing = pd.read_excel(RESULTS_FILE)
                print(f"📂 Существующий файл содержит {len(df_existing)} записей")
                
                # Объединяем и удаляем дубликаты
                df_all = pd.concat([df_existing, df_new], ignore_index=True)
                df_all = df_all.drop_duplicates(subset=['email', 'video_url'], keep='last')
                print(f"🔍 После удаления дубликатов: {len(df_all)} записей")
                
                saved_count = len(df_all) - len(df_existing)
            except Exception as e:
                print(f"⚠️ Ошибка чтения файла: {e}, создаю новый")
                df_all = df_new
                saved_count = len(df_new)
        else:
            df_all = df_new
            saved_count = len(df_new)
            print("🆕 Файл не существовал, будет создан новый")
        
        # Сохраняем
        df_all.to_excel(RESULTS_FILE, index=False, engine='openpyxl')
        print(f"💾 Сохранено в {RESULTS_FILE}: {saved_count} новых записей")
        return saved_count
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return 0