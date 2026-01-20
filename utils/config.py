"""Конфигурационные настройки"""

# Пути к файлам
CHECKED_URLS_FILE = "data/checked_urls.json"
RESULTS_FILE = "data/youtube_emails.xlsx"

# Настройки поиска
MAX_VIDEOS = 5
TIMEOUT = 15

# Настройки браузера
CHROME_OPTIONS = [
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--log-level=3",
    "--start-maximized"  # Раскомментируйте для окна браузера
]

# Селекторы для поиска
DESCRIPTION_SELECTORS = [
    "#description",
    "ytd-text-inline-expander",
    ".ytd-video-secondary-info-renderer",
    "ytd-video-description-renderer"
]