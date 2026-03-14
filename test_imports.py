import sys
import os

print("=" * 50)
print("ПРОВЕРКА ИМПОРТОВ")
print("=" * 50)

# Текущая директория
print(f"\n📁 Текущая папка: {os.getcwd()}")
print(f"📁 Файлы в папке: {[f for f in os.listdir('.') if f.endswith('.py')]}")

# Проверка папок
print("\n📁 Проверка структуры:")
folders = ['modules', 'utils']
for folder in folders:
    if os.path.exists(folder):
        print(f"✅ Папка {folder} найдена")
        py_files = [f for f in os.listdir(folder) if f.endswith('.py')]
        print(f"   Файлы: {py_files}")
    else:
        print(f"❌ Папка {folder} НЕ найдена!")

# Добавляем текущую папку в путь
sys.path.insert(0, os.getcwd())

# Проверка импортов
print("\n📦 Проверка импортов модулей:")

modules_to_check = [
    ('modules.browser', 'browser'),
    ('modules.url_tracker', 'url_tracker'),
    ('modules.youtube_searcher', 'youtube_searcher'),
    ('modules.email_extractor', 'email_extractor'),
    ('modules.data_saver', 'data_saver'),
    ('utils.helpers', 'helpers')
]

for module_path, module_name in modules_to_check:
    try:
        __import__(module_path)
        print(f"✅ {module_path} - OK")
    except ImportError as e:
        print(f"❌ {module_path} - Ошибка: {e}")

# Проверка PyQt5
print("\n🎨 Проверка PyQt5:")
try:
    from PyQt5.QtWidgets import QApplication
    print("✅ PyQt5.QtWidgets - OK")
    from PyQt5.QtCore import Qt
    print("✅ PyQt5.QtCore - OK")
except ImportError as e:
    print(f"❌ PyQt5 - Ошибка: {e}")

print("\n" + "=" * 50)
print("Нажмите Enter для выхода...")
input()