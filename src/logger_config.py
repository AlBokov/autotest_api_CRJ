import logging 
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

# Создаем папку для логов, если её нет
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
ARCHIVE_DIR = LOG_DIR / "archive"
ARCHIVE_DIR.mkdir(exist_ok=True)

# Имена файлов для логов
LOG_FILE = LOG_DIR / f"autotests_{datetime.now().strftime('%Y%m%d')}.log"
ERROR_LOG_FILE = LOG_DIR / f"autotests_{datetime.now().strftime('%Y%m%d')}_error.log"

# Уровни логирования :
# DEBUG    = 10 - детальная информация для отладки
# INFO     = 20 - отчет по автотестам(общая информация)
# WARNING  = 30 - предупреждения
# ERROR    = 40 - ошибки
# CRITICAL = 50 - критические ошибки


# Настройка формата логов
LOG_FORMAT = '%(asctime)s  %(name)s - %(levelname)s: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


# Класс для настройки логирования в автотестах
class AutoTestLogger:
    
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    # Настройка логгера
    def _setup_logger(self, log_level=logging.DEBUG):

        # Создаем основной логгер
        self._logger = logging.getLogger("AutoTests")
        self._logger.setLevel(log_level)

        # Очищаем старые обработчики
        if self._logger.handlers:
            self._logger.handlers.clear()

        
        # Создаем форматтер
        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

        # 1. Обработчик для ВСЕХ логов (ротация по размеру)
        all_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE, 
            maxBytes=10_485_760,  # 10 MB
            backupCount=10,
            encoding='utf-8'
        )
        all_handler.setLevel(logging.DEBUG)
        all_handler.setFormatter(formatter)

        # 2. Обработчик только для ОШИБОК
        error_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=5_242_880,  # 5 MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

         # 3. Обработчик для консоли (во время отладки)
        console_handler = logging.StreamHandler()

        # Уровень для консоли можно менять через переменную окружения
        console_level = os.getenv('LOG_LEVEL', 'INFO')
        console_handler.setLevel(getattr(logging, console_level))
        console_handler.setFormatter(formatter)
        
        # Добавляем все обработчики
        self._logger.addHandler(all_handler)
        self._logger.addHandler(error_handler)
        self._logger.addHandler(console_handler)

    # Получить логгер
    def get_logger(self):
        return self._logger
    
    # Изменить уровень логирования на лету
    def set_level(self, level):
        self._logger.setLevel(level)
        self._logger.info(f"Уровень логирования изменен на {logging.getLevelName(level)}")


# Создаем глобальный логгер
def get_logger():
    """Удобная функция для получения логгера"""
    return AutoTestLogger().get_logger()


# Функция для изменения уровня логирования
def set_log_level(level_name):
    """
    Изменение уровня логирования
    Пример: set_log_level('DEBUG')
    """
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    if level_name.upper() in levels:
        AutoTestLogger().set_level(levels[level_name.upper()])
        return True
    else:
        get_logger().error(f"Неизвестный уровень логирования: {level_name}")
        return False