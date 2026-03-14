#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import traceback

def main():
    print("=" * 60)
    print("ЗАПУСК ПРОГРАММЫ")
    print("=" * 60)
    
    try:
        print("1. Импортируем main_gui...")
        import main_gui
        print("✅ main_gui импортирован")
        
        print("2. Запускаем main_gui.main()...")
        if hasattr(main_gui, 'main'):
            main_gui.main()
        elif hasattr(main_gui, 'run'):
            main_gui.run()
        else:
            print("❌ В main_gui нет функции main() или run()")
            
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        print("\n📋 Детали ошибки:")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Программа завершена. Нажмите Enter для выхода...")
    input()

if __name__ == "__main__":
    main()