import yaml
from typing import Dict, Any, Optional
from src.settings import defining_value_variable

# Класс для чтения operation.yaml
class OpenApiParser:
    def __init__(self, path: str, cardAcceptorTerminal: str = None, QrAcceptorTerminal: str = None):
        with open(path, 'r', encoding="utf-8") as file:
            self.spec = yaml.safe_load(file)

        # Получаем значение карточного тида
        if cardAcceptorTerminal is None:
            cardAcceptorTerminal = defining_value_variable('cardAcceptorTerminal')

        # Получаем значения СБП тида
        if QrAcceptorTerminal is None:
            QrAcceptorTerminal = defining_value_variable('QrAcceptorTerminal')

        self.components = self.spec['components']['schemas']
        self.paths = self.spec['paths']
        # Атрибут для сохранения предыдущего ответа.
        self.old_response = None
        self.cardAcceptorTerminal = cardAcceptorTerminal
        self.QrAcceptorTerminal = QrAcceptorTerminal

    def get_response_schema(self, operation: str, activation_type: str = None):

        for path, methods in self.paths.items():
            post = methods.get("post")
            if not post:
                continue
            print(post["responses"]["200"]["content"]["application/json"]["schema"])

            

    def get_response_schema2(self, operation: str, activation_type: str = None):
        for path, methods in self.paths.items():
            post = methods.get("post")
            if not post:
                continue
            
            try:
               # 1. Получаем пример запроса
                example_data = post["requestBody"]["content"]["application/json"]["example"]
                example_request = example_data.get("request", {})
                
                # 2. Проверяем операцию в примере запроса
                example_operation = example_request.get("operation", "").lower()
                
                if example_operation == operation.lower():
                    
                    # 3. Для activate проверяем activationType
                    if operation.lower() == "activate" and activation_type:
                        example_activation = example_request.get("activationType")
                        if example_activation != activation_type:
                            continue 
                    
                    # 4. Получаем схему ответа из responses
                    try:
                        response_schema = post["responses"]["200"]["content"]["application/json"]["schema"]
                        
                        # Может быть прямая схема или ссылка $ref
                        if "$ref" in response_schema:
                            ref = response_schema["$ref"]
                            schema_name = ref.split("/")[-1]
                            print(f"  📋 Схема ответа: {schema_name} (по ссылке)")
                            return self.components[schema_name]
                        else:
                            print(f"  📋 Схема ответа: прямая схема")
                            return response_schema
                            
                    except KeyError as e:
                        print(f"  ❌ Нет схемы ответа для {operation}: {e}")
                        continue
                        
            except KeyError as e:
                # Пропускаем endpoints без example
                continue
            except Exception as e:
                print(f"  ⚠️ Ошибка при обработке {path}: {e}")
                continue
        
        # Если ничего не нашли
        error_msg = f"Операция '{operation}'"
        if operation.lower() == "activate" and activation_type:
            error_msg += f" с типом активации '{activation_type}'"
        error_msg += " не найдена в спецификации"
        
        raise ValueError(error_msg)
        

    # Формируем запрос на основе примера из спецификации для указанной операции. 
    def build_request_example(self, operation: str, activation_type: str = None):
        
        for path, method in self.paths.items():
            post = method.get("post")
            if not post:
                continue
            
            # Проверяем наличие примера
            try:
                example_data = post["requestBody"]["content"]["application/json"]["example"]
                example_request = example_data["request"]
                    
                # Для операции activate проверяем activationType
                if operation.lower() == "activate" and activation_type:
                    if example_request.get("activationType") != activation_type:
                        continue
                
                # Проверяем соответствие операции 
                if example_request.get("operation", "").lower() == operation.lower():
                    # Создаем копию примера запроса
                    request_data = example_request.copy()

                    # Формирования запроса для возврата
                    if operation.lower() in ["refund", "customerreversal"]:
                        # Заменяем RRN and trxId
                        if self.old_response is not None:
                            request_data['referenceNumber'] = self.old_response['response']['referenceNumber']
                            request_data['trxId'] = self.old_response['response']['trxId']

                            # Формируем полный запрос в нужном формате
                            full_request = {
                            "request": request_data
                            }

                        else:
                            # Если нет сохраненного ответа
                            raise ValueError("Нет сохраненного ответа от предыдущей операции для refund")

                    # Формирование запроса печати чека 
                    if operation.lower() == "print":
                        # Заменяем trxId
                        if self.old_response is not None:
                            request_data['trxId'] = self.old_response['response']['trxId']

                            # Формируем полный запрос в нужном формате
                            full_request = {
                            "request": request_data
                            }

                        else:
                            # Если нет сохраненного ответа, можно:
                            raise ValueError("Нет сохраненного ответа от предыдущей операции для print")
                        
                    # Формирование запроса расчета преавторизации.
                    if operation.lower() == "completion":
                        # Заменяем trxId
                        if self.old_response is not None:
                            request_data['referenceNumber'] = self.old_response['response']['referenceNumber']

                            # Формируем полный запрос в нужном формате
                            full_request = {
                            "request": request_data
                            }

                        else:
                            # Если нет сохраненного ответа, можно:
                            raise ValueError("Нет сохраненного ответа от предыдущей операции для completion")

                    # Формирование запроса статус оплаты СБП. 
                    if operation.lower() in ["sbpsalestatus", "sbprefund"]:
                        # Заменяем trxId
                        if self.old_response is not None:
                            request_data['trxId'] = self.old_response['response']['trxId']
                            request_data['qrcId'] = self.old_response['response']['qrcId']
                            request_data['referenceNumber'] = self.old_response['response']['referenceNumber']

                            # Формируем полный запрос в нужном формате
                            full_request = {
                            "request": request_data
                            }

                        else:
                            # Если нет сохраненного ответа, можно:
                            raise ValueError("Нет сохраненного ответа от предыдущей операции для sbpsalestatus")
                        
                    # Меняем тид на значение из setting.txt    
                    if operation.lower() in ["sbpsale", "sbpsalestatus", "sbprefund", "sbprefundstatus"]:
                        request_data['cardAcceptorTerminal'] = self.QrAcceptorTerminal
                    else: 
                        request_data['cardAcceptorTerminal'] = self.cardAcceptorTerminal
                    
                    # Формируем полный запрос в нужном формате
                    full_request = {
                        "request": request_data
                    }

                    return full_request
                
            except (KeyError, TypeError) as e:
                # Пропускаем эндпоинты без примера
                continue



        
        # Если ничего не нашли
        error_msg = f"Операция '{operation}"
        if operation.lower == "activate" and activation_type:
            error_msg += f" с типом '{activation_type}'"
        error_msg += " не найдена в спецификации"

        raise ValueError(error_msg)
    
    def get_operation(self, operation: str) -> Dict[str, Any]:
        path = f"/{operation}"
        return self.spec["paths"][path]["post"]
    
    def resolve_ref(self, ref: str) -> Dict[str, Any]:
        path = ref.replace("#/", "").split("/")
        node = self.spec
        for p in path:
            node = node[p]
        return node
    
    def get_response_required_fields(self, operation: str) -> set:
        op = self.get_operation(operation)
        response_schema_ref = (
            op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        )
        schema = self.resolve_ref(response_schema_ref)
        required = []
        for part in schema.get("allOf", []):
            if "$ref" in part:
                ref_schema = self.resolve_ref(part["$ref"])
                required.extend(ref_schema.get("required", []))
            else:
                required.extend(part.get("required", []))
        return set(required)
