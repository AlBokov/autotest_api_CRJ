from src.open_parser_yaml import OpenApiParser
from src.client import ApiClient
from src.validator_response import check_api_response
import yaml

# Программа ручнуго ввода
if __name__ == "__main__":

    
    client = ApiClient()

    parser = OpenApiParser('config/operation.yaml')

    while True:

        operation = input("Введите название операции или введите close для закрытия: \n")

        if operation == "activate":
            activate = input("Выберити тип активации: \n")
        else:
            activate = None


        if operation != 'close':

            try:
                operation_request = parser.build_request_example(operation, activate)
                print(f"=== Операция {operation} запущена ===")
                print('=== Запрос ===:')
                print((yaml.dump(operation_request, allow_unicode=True, sort_keys=False)))

                response  = client.send_request(operation_request)

                parser.old_response = response # Ответ от терминала 
                print(f"\n Ответ записан {parser.old_response} \n =======")


                print(f"\n \n === Операция {operation} завершена ===\n")
                print("Ответ: ")
                print((yaml.dump(parser.old_response, allow_unicode=True, sort_keys=False)))
                
                try:
                    receipt = response['response']['receiptData']
                    client.format_receipt(response['response']['receiptData'])
                except KeyError:
                    print("Поле receiptData не найдено в ответе")
                    print()
                    receipt = None
                    # Можно посмотреть что есть в ответе
                    if 'response' in response:
                        print(f"Доступные поля в response: {list(response['response'].keys())}")

                

                required_fields = parser.get_response_required_fields(operation)

                if check_api_response(response['response'], required_fields) == False:
                    
                    operation_request = parser.build_request_example("uploadLogs", activate)
                    print(f'Логи выгруженны из профиля')


            except ValueError as e:
                print(f'Ошибка {e}')

            except KeyError as e:
                print(f"⚠️ WARNING!!! Ошибка подключения к http://127.0.0.1:40101/api/1/ecr/transaction: HTTPConnectionPool(host=''127.0.0.1'') ")
                print(f'Скорее всего используется не тот ip или port')
                print()
        
        
        else:
            print('До новых встреч')
            break
