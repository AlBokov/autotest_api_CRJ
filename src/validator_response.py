from src.logger_config import get_logger, set_log_level

# Получаем логгер
logger = get_logger()

# Проверяем что в ответе есть все нужные поля. 
def check_api_response(response, required_fields):

    try:
        response_fields = set(response.keys())
        missing_fields = required_fields - response_fields
        missing_fields_no = response_fields - required_fields

        if missing_fields:
            logger.info(f"❌ Отсутствуют поля: {', '.join(missing_fields)}")
            return False
        
        elif missing_fields_no:
            logger.info(f"❌ Есть лишнее поля: {', '.join(missing_fields_no)}")
            return False
        
        else:
            logger.info("✅ Все поля присутствуют")
            return True
        
    except KeyError:
        error_msg  = f'Ответ не найден.'
        logger.info(f"ERROR: {error_msg}")
