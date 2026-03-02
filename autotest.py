from src.open_parser_yaml import OpenApiParser
from src.client import ApiClient
from src.validator_response import check_api_response
from src.settings import defining_value_variable, reading_list_of_operations
from src.logger_config import get_logger, set_log_level
import yaml
import time

# Получаем логгер
logger = get_logger()


if __name__ == "__main__":

    logger.info("=== СТАРТ АВТОТЕСТОВ ===\n")

    number_iterations_autotests = int(defining_value_variable('number_iterations_autotests')) + 1

    test_scenario = reading_list_of_operations()
    test_scenario_log = ' → '.join(test_scenario)
    logger.info(f'Тестовый сценарий: {test_scenario_log}')
    logger.info(f'Количество итераций: {number_iterations_autotests - 1}')

    iterations = 1

    url = '192.168.1.39'
    
    client = ApiClient(url)
    logger.info(f'Инициализирован клиент для {url}')

    parser = OpenApiParser('config/operation.yaml')
    logger.info(f'Документация успешно считана')
    logger.info(f'=== ЗАПУСК СЦЕНАРИЯ ТЕСТИРОВАНИЯ ===')


    while iterations < number_iterations_autotests:
        logger.info(f'=== ИТЕРАЦИЯ {iterations} СТАРТ ===')

        for operation in test_scenario:
            logger.info(f'\nОПЕРАЦИЯ - {operation} ЗАПУЩЕНА')

            if operation == "activate":
                activate = input("Выберити тип активации: \n")
            else:
                activate = None

            try:
                operation_request = parser.build_request_example(operation, activate)

                logger.info(yaml.dump(operation_request, allow_unicode=True, sort_keys=False))

                response  = client.send_request(operation_request)

                parser.old_response = response # Ответ от терминала 

                logger.info(f'Получен ответ.')
                logger.info((yaml.dump(parser.old_response, allow_unicode=True, sort_keys=False)))

                client.format_receipt(response['response']['receiptData'])

                required_fields = parser.get_response_required_fields(operation)

                ckeck = check_api_response(response['response'], required_fields)
                if ckeck == False:
                    operation_request = parser.build_request_example("uploadLogs", activate)
                    logger.info(f'Из-за ошибки были выгружены логи с терминала. Сохранение логов не реализовано, поэтому нужно ручками выгрузить логи из ТМС:(')
                    logger.info(f'Поправка, операция выгрузка логов не работает, так, иди и выгружай логи сам ¯\(°_o)/¯ )')

                logger.info(f'ОПЕРАЦИЯ - {operation} ЗАВЕРШЕНА\n')

                if operation == 'closebatch':
                    time.sleep(40)
                
                if operation != 'closebatch':
                    time.sleep(10)

            except ValueError as e:
                print(f'ОшибкЧто то пошли не так, повторите (╬ Ò﹏Ó){e}')
                logger.error(f'ОшибкЧто то пошли не так, повторите (╬ Ò﹏Ó) {e}')

            

        logger.info(f'=== ИТЕРАЦИЯ {iterations} ФИНИШ ===')
        logger.info('=' * 60)
        

        iterations += 1

        print("=" * 60)






