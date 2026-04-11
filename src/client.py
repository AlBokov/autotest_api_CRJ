import requests
from typing import Dict, Any, Optional
import json
from src.settings import defining_value_variable
from src.logger_config import get_logger

# создаем логгер
logger = get_logger()

# Класс для отправки запросов на терминал
class ApiClient:

    def __init__(self, ip_address: str = None, timeout: int = None, port: str = None):
        
        # Получаем значения из настроек, если они не переданы
        if ip_address is None:
            ip_address = defining_value_variable('ip_terminal')
        
        if port is None:
            port = defining_value_variable('port')
        
        if timeout is None:
            timeout = int(defining_value_variable('TO'))

        # Формируем базовый URL с фиксированным портом и эндпоинтом
        self.base_url = f"http://{ip_address}:{port}/api/1/ecr/transaction"
        self.timeout = timeout

        # Сохраняем последний ответ для возможности использования его полей
        self.last_response: Optional[Dict[str, Any]] = None

    # Отправляет POST запрос на терминал
    def send_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:

        # Формируем заголовки запроса
        headers = {
            "Content-Type": "application/json",
            "Connection": "close",  
        }

        try:
            # Отправляем POST запрос
            response = requests.post(
                self.base_url,
                json=request_data,
                headers=headers,
                timeout=self.timeout
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Парсим JSON ответ
            try:
                response_data = response.json()
            except ValueError:
                # Если ответ не в JSON формате
                response_data = {"error": "Неверный формат ответа", "raw": response.text}
            
            # Сохраняем ответ для последующего использования
            self.last_response = response_data
            
            return response_data
            
        except requests.exceptions.Timeout:
            error_msg = f"Таймаут запроса (превышено {self.timeout} секунд)"
            return {"error": error_msg}
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Ошибка подключения к {self.base_url}: {str(e)}"
            return {"error": error_msg}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка при выполнении запроса: {str(e)}"
            return {"error": error_msg}

    def _get_field_from_response(self, field_name: str) -> Optional[str]:
        """
        Внутренний метод для получения поля из последнего ответа
        
        Args:
            field_name: Имя поля (trxId, referenceNumber, qrcId)
            
        Returns:
            Значение поля в виде строки или None, если поле не найдено
        """
        if not self.last_response:
            return None
        
        # Проверяем разные возможные расположения поля
        if isinstance(self.last_response, dict):
            # Прямое поле на верхнем уровне
            if field_name in self.last_response:
                return str(self.last_response[field_name])
            
            # Поле внутри response
            if "response" in self.last_response and isinstance(self.last_response["response"], dict):
                if field_name in self.last_response["response"]:
                    return str(self.last_response["response"][field_name])

        
        return None

    def print_readable_response(self, response_data: Dict[str, Any] = None) -> None:
        """
        Красиво выводит ответ в консоль
        
        Args:
            response_data: Данные ответа (если не указаны, используется last_response)
        """
        
        # Используем переданные данные или last_response
        data = response_data or self.last_response
        
        if not data:
            logger.info("Нет данных для вывода")
            return
        
        logger.info("=" * 60)
        logger.info("ОТВЕТ ОТ ТЕРМИНАЛА:")
        logger.info("=" * 60)
        
        # Проверяем структуру ответа
        if isinstance(data, dict):
            if "response" in data:
                resp_data = data["response"]
                
                # Выводим основные поля
                important_fields = [
                    ("Операция", "operation"),
                    ("Код ответа", "responseCode"),
                    ("Описание", "responseDescription"),
                    ("trxId", "trxId"),
                    ("referenceNumber", "referenceNumber"),
                    ("Авторизационный код", "authorisationCode"),
                    ("UID", "uid"),
                    ("Дата/время", "transactionDateTime"),
                    ("Терминал", "cardAcceptorTerminal"),
                    ("ИНН", "inn"),
                    ("Способ оплаты", "paymentMethod"),
                ]
                
                for label, field in important_fields:
                    if field in resp_data:
                        print(f"{label:20}: {resp_data[field]}")
                
                # Если есть чек, выводим его
                if "receiptData" in resp_data:
                    logger.info("\n" + "=" * 40)
                    logger.info("ЧЕК:")
                    logger.info("=" * 40)
                    logger.info(resp_data["receiptData"])
            else:
                # Если структура другая, выводим весь ответ
                logger.info(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            logger.info(data)
        
        logger.info("=" * 60)


    def format_receipt(self, receipt_data: str) -> str:
        if not receipt_data:
            return "Чек отсутствует"
        
        # Пробуем разные способы декодирования
        try:
            # Способ 1: Если это байты
            if isinstance(receipt_data, bytes):
                text = receipt_data.decode('cp1251')
            else:
                # Способ 2: Если это строка с escape последовательностями
                text = receipt_data.encode().decode('unicode_escape')
                
                # Способ 3: Пробуем перекодировать из cp1251
                try:
                    text = text.encode('latin1').decode('cp1251')
                except:
                    pass
        except:
            text = receipt_data
        
        # Заменяем управляющие символы
        replacements = {
            '\\r\\n': '\n',
            '\\r': '\n',
            '\\n': '\n',
            '\\t': '    ',
            '\r\n': '\n',
            '\r': '\n',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Разбиваем на строки и чистим
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:  # Если строка не пустая
                lines.append(line)
        
        return '\n'.join(lines)

        