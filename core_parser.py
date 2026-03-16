"""Ядро парсера для работы с GUI"""
import threading
import time
from datetime import datetime
from modules.browser import setup_driver
from modules.url_tracker import load_checked_urls, save_checked_urls, filter_new_videos, add_to_history
from modules.youtube_searcher import search_youtube_videos
from modules.email_extractor import process_video
from modules.data_saver import save_to_excel

class ParserCore:
    """Класс-обертка для работы парсера в GUI"""
    
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.is_running = False
        self.stop_requested = False
        self.checked_urls = set()
        self.all_results = []  # Сохраняем все найденные результаты
        self.driver = None
        
    def update_gui(self, data):
        """Отправка данных в GUI"""
        if self.gui_callback:
            self.gui_callback(data)
    
    def start_parsing(self, hashtag, max_videos=5):
        """Запуск парсера в отдельном потоке"""
        if self.is_running:
            self.update_gui({'type': 'warning', 'message': 'Парсер уже запущен'})
            return
        
        self.stop_requested = False
        self.all_results = []  # Очищаем результаты
        thread = threading.Thread(target=self._parse_thread, args=(hashtag, max_videos))
        thread.daemon = True
        thread.start()
    
    def stop_parsing(self):
        """Остановка парсера"""
        self.stop_requested = True
        self.update_gui({'type': 'log', 'message': '⏹️ Останавливаю парсер...'})
        
        # Немедленно сохраняем уже найденные результаты
        self._save_current_results()
    
    def _save_current_results(self):
        """Сохраняет текущие результаты при остановке"""
        if self.all_results:
            try:
                saved_count = save_to_excel(self.all_results)
                save_checked_urls(self.checked_urls)
                self.update_gui({
                    'type': 'log',
                    'message': f"💾 При остановке сохранено {saved_count} новых email"
                })
            except Exception as e:
                self.update_gui({'type': 'error', 'message': f'Ошибка сохранения: {str(e)}'})
    
    def _parse_thread(self, hashtag, max_videos):
        """Поток выполнения парсера"""
        self.is_running = True
        self.driver = None
        
        try:
            # Шаг 1: Загрузка истории
            self.update_gui({'type': 'progress', 'value': 10, 'status': 'Загрузка истории...'})
            self.checked_urls = load_checked_urls()
            self.update_gui({'type': 'log', 'message': f"📁 Загружено {len(self.checked_urls)} видео в истории"})
            
            if self.stop_requested:
                self._save_current_results()
                return
            
            # Шаг 2: Запуск браузера
            self.update_gui({'type': 'progress', 'value': 20, 'status': 'Запуск браузера...'})
            self.driver = setup_driver()
            if not self.driver:
                self.update_gui({'type': 'error', 'message': 'Не удалось запустить браузер'})
                return
            
            self.update_gui({'type': 'log', 'message': "✅ Браузер запущен"})
            
            if self.stop_requested:
                self._save_current_results()
                return
            
            # Шаг 3: Поиск видео
            self.update_gui({'type': 'progress', 'value': 30, 'status': f'Поиск видео...'})
            video_data = search_youtube_videos(self.driver, hashtag, max_videos)
            
            if not video_data:
                self.update_gui({'type': 'error', 'message': 'Видео не найдены'})
                return
            
            self.update_gui({'type': 'log', 'message': f"🔍 Найдено видео: {len(video_data)}"})
            
            if self.stop_requested:
                self._save_current_results()
                return
            
            # Шаг 4: Фильтрация новых видео
            self.update_gui({'type': 'progress', 'value': 40, 'status': 'Фильтрация новых видео...'})
            new_videos = filter_new_videos(video_data, self.checked_urls)
            
            if not new_videos:
                self.update_gui({'type': 'warning', 'message': 'Все видео уже были проверены ранее!'})
                return
            
            self.update_gui({'type': 'log', 'message': f"🆕 Новых видео для обработки: {len(new_videos)}"})
            
            # Шаг 5: Обработка видео
            total = len(new_videos)
            processed_count = 0
            found_count = 0
            
            for i, video_info in enumerate(new_videos, 1):
                if self.stop_requested:
                    self.update_gui({'type': 'log', 'message': '⏹️ Парсинг остановлен пользователем'})
                    # Сохраняем то, что уже нашли
                    self._save_current_results()
                    break
                
                progress = 40 + int((i / total) * 50)
                self.update_gui({
                    'type': 'progress',
                    'value': progress,
                    'status': f'Видео {i} из {total}'
                })
                
                self.update_gui({
                    'type': 'log',
                    'message': f"\n🎬 [{i}/{total}] {video_info['title'][:60]}..."
                })
                
                result = process_video(self.driver, video_info)
                
                if result and result.get('email'):
                    self.all_results.append(result)
                    add_to_history(video_info['url'], self.checked_urls)
                    found_count += 1
                    
                    self.update_gui({
                        'type': 'result',
                        'data': {
                            'video_title': video_info['title'],
                            'email': result['email'],
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
                        }
                    })
                    
                    self.update_gui({'type': 'log', 'message': f"✅ Найден email: {result['email']}"})
                else:
                    add_to_history(video_info['url'], self.checked_urls)
                    self.update_gui({'type': 'log', 'message': "❌ Email не найден"})
                
                processed_count += 1
                
                # Каждые 5 видео показываем промежуточную статистику
                if processed_count % 5 == 0:
                    self.update_gui({
                        'type': 'log',
                        'message': f"📊 Промежуточно: обработано {processed_count}, найдено {found_count}"
                    })
                
                time.sleep(2)
            
            if self.stop_requested:
                return
            
            # Шаг 6: Сохранение результатов
            self.update_gui({'type': 'progress', 'value': 95, 'status': 'Сохранение результатов...'})
            
            saved_count = 0
            if self.all_results:
                saved_count = save_to_excel(self.all_results)
                self.update_gui({'type': 'log', 'message': f"💾 Сохранено email: {saved_count}"})
            else:
                self.update_gui({'type': 'log', 'message': "📧 Email не найдены"})
            
            save_checked_urls(self.checked_urls)
            
            # Финальное сообщение
            self.update_gui({'type': 'complete'})
            
            self.update_gui({
                'type': 'log',
                'message': f"\n🎉 СТАТИСТИКА:"
            })
            self.update_gui({'type': 'log', 'message': f"   • Всего видео: {len(video_data)}"})
            self.update_gui({'type': 'log', 'message': f"   • Обработано новых: {len(new_videos)}"})
            self.update_gui({'type': 'log', 'message': f"   • Найдено email: {len(self.all_results)}"})
            self.update_gui({'type': 'log', 'message': f"   • Сохранено: {saved_count}"})
            
        except Exception as e:
            self.update_gui({'type': 'error', 'message': f'Ошибка: {str(e)}'})
            
        finally:
            if self.driver:
                self.driver.quit()
                self.update_gui({'type': 'log', 'message': "🔒 Браузер закрыт"})
            
            self.is_running = False