
import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar, QMessageBox, QTabWidget,
    QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from core_parser import ParserCore

class ParserThread(QThread):
    """Поток для запуска парсера"""
    update_signal = pyqtSignal(dict)
    
    def __init__(self, hashtag, max_videos):
        super().__init__()
        self.hashtag = hashtag
        self.max_videos = max_videos
        self.parser = ParserCore(gui_callback=self.handle_update)
        
    def handle_update(self, data):
        """Обработка обновлений от парсера"""
        self.update_signal.emit(data)
    
    def run(self):
        self.parser.start_parsing(self.hashtag, self.max_videos)
    
    def stop(self):
        self.parser.stop_parsing()

class MainWindow(QMainWindow):
    """Главное окно программы"""
    
    def __init__(self):
        super().__init__()
        self.parser_thread = None
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("YouTube Email Parser")
        self.setGeometry(100, 100, 1000, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        
        # === Верхняя панель ===
        top_group = QGroupBox("Параметры поиска")
        top_layout = QGridLayout()
        
        # Хештег
        top_layout.addWidget(QLabel("Хештег:"), 0, 0)
        self.hashtag_input = QLineEdit()
        self.hashtag_input.setPlaceholderText("Например: #python")
        self.hashtag_input.setText("#")
        top_layout.addWidget(self.hashtag_input, 0, 1)
        
        # Количество видео
        top_layout.addWidget(QLabel("Макс. видео:"), 0, 2)
        self.max_videos_spin = QSpinBox()
        self.max_videos_spin.setRange(1, 9999)
        self.max_videos_spin.setValue(5)
        top_layout.addWidget(self.max_videos_spin, 0, 3)
        
        # Кнопки
        self.start_btn = QPushButton("🚀 Старт")
        self.start_btn.clicked.connect(self.start_parsing)
        top_layout.addWidget(self.start_btn, 0, 4)
        
        self.stop_btn = QPushButton("⏹️ Стоп")
        self.stop_btn.clicked.connect(self.stop_parsing)
        self.stop_btn.setEnabled(False)
        top_layout.addWidget(self.stop_btn, 0, 5)
        
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)
        
        # === Прогресс ===
        progress_group = QGroupBox("Прогресс")
        progress_layout = QVBoxLayout()
        
        self.status_label = QLabel("Готов к работе")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # === Вкладки ===
        tabs = QTabWidget()
        
        # Вкладка с результатами
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Название видео", "Email", "Дата"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        results_layout.addWidget(self.results_table)
        
        tabs.addTab(results_tab, "📧 Найденные email")
        
        # Вкладка с логами
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Consolas', monospace;
            }
        """)
        logs_layout.addWidget(self.logs_text)
        
        tabs.addTab(logs_tab, "📝 Логи")
        
        layout.addWidget(tabs)
        
        # === Нижняя панель ===
        bottom_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🧹 Очистить логи")
        self.clear_btn.clicked.connect(self.clear_logs)
        bottom_layout.addWidget(self.clear_btn)
        
        self.open_folder_btn = QPushButton("📁 Открыть папку с данными")
        self.open_folder_btn.clicked.connect(self.open_data_folder)
        bottom_layout.addWidget(self.open_folder_btn)
        
        bottom_layout.addStretch()
        
        self.stats_label = QLabel("Найдено: 0")
        self.stats_label.setStyleSheet("font-weight: bold;")
        bottom_layout.addWidget(self.stats_label)
        
        layout.addLayout(bottom_layout)
        
        # Приветственное сообщение
        self.log_message("🎯 YouTube Email Parser запущен")
        self.log_message("💡 Введите хештег и нажмите 'Старт'")
        
    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_text.append(f"[{timestamp}] {message}")
        # Автопрокрутка
        cursor = self.logs_text.textCursor()
        cursor.movePosition(cursor.End)
        self.logs_text.setTextCursor(cursor)
    
    def clear_logs(self):
        """Очистка логов"""
        self.logs_text.clear()
        self.log_message("🧹 Логи очищены")
    
    def open_data_folder(self):
        """Открытие папки с данными"""
        folder_path = os.path.join(os.path.dirname(__file__), 'data')
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        if os.name == 'nt':  # Windows
            os.startfile(folder_path)
        
        self.log_message(f"📁 Открыта папка: {folder_path}")
    
    def start_parsing(self):
        """Запуск парсера"""
        hashtag = self.hashtag_input.text().strip()
        if not hashtag or hashtag == "#":
            QMessageBox.warning(self, "Ошибка", "Введите хештег!")
            return
        
        max_videos = self.max_videos_spin.value()
        
        # Очищаем таблицу
        self.results_table.setRowCount(0)
        
        # Обновляем UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Запуск...")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        self.log_message(f"🚀 Запуск с хештегом: {hashtag}")
        self.log_message(f"📊 Максимум видео: {max_videos}")
        
        # Создаем и запускаем поток
        self.parser_thread = ParserThread(hashtag, max_videos)
        self.parser_thread.update_signal.connect(self.handle_update)
        self.parser_thread.start()
    
    def stop_parsing(self):
        if self.parser_thread and self.parser_thread.isRunning():
            self.stop_btn.setEnabled(False)  # Отключаем кнопку стоп
            self.status_label.setText("Останавливается...")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        
            # Отправляем сигнал остановки
            self.parser_thread.stop()
        
            # Ждем немного и обновляем UI
            QTimer.singleShot(1000, self._check_thread_stopped)

    def _check_thread_stopped(self):
        if not self.parser_thread or not self.parser_thread.isRunning():
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Остановлено")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.log_message("✅ Парсер успешно остановлен")
    
    def handle_update(self, data):
        """Обработка обновлений от парсера"""
        msg_type = data.get('type', '')
        
        if msg_type == 'progress':
            self.progress_bar.setValue(data.get('value', 0))
            self.status_label.setText(data.get('status', ''))
            
        elif msg_type == 'log':
            self.log_message(data.get('message', ''))
            
        elif msg_type == 'result':
            # Добавляем результат в таблицу
            result_data = data.get('data', {})
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(
                result_data.get('video_title', '')[:100]
            ))
            self.results_table.setItem(row, 1, QTableWidgetItem(
                result_data.get('email', '')
            ))
            self.results_table.setItem(row, 2, QTableWidgetItem(
                result_data.get('date', '')
            ))
            
            self.stats_label.setText(f"Найдено: {row + 1}")
            
        elif msg_type == 'error':
            QMessageBox.critical(self, "Ошибка", data.get('message', ''))
            self.log_message(f"❌ ОШИБКА: {data.get('message', '')}")
            self.log_message(f"❌ ChromeDriver не найден! Скачайте с: https://googlechromelabs.github.io/chrome-for-testing/ ❗Сохраните в: \\drivers\\chromedriver.exe")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Ошибка")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            
        elif msg_type == 'warning':
            QMessageBox.warning(self, "Предупреждение", data.get('message', ''))
            self.log_message(f"⚠️ {data.get('message', '')}")
            
        elif msg_type == 'complete':
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Завершено")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.log_message("✅ Работа завершена!")
            
            QMessageBox.information(self, "Завершено", "Парсинг успешно завершен!")

def main():
    """Точка входа"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()