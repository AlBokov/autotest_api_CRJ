# Получаем пременные из файл setting.txt
def reading_settings():
    with open('config/setting.txt', 'r', encoding='utf-8') as setting:
        lines = setting.readlines()

        settings = {}

        for line in lines:
            line = line.strip()

            if line:
                parts = line.split('=')

                key = parts[0].strip()
                value = parts[1].strip()

                settings[key] = value

        return settings

# Выдаем конкретную переменную
def defining_value_variable(varible: str):
    settings = reading_settings()

    return settings[varible]

# Получаем список для сценария тестирования
def reading_list_of_operations():
    with open("config/list_of_operations.txt", "r", encoding='utf-8') as list_operation:
        operations = list_operation.readlines()

        test_scenario = list()

        for operation in operations:
            operation = operation.strip()
            test_scenario.append(operation)

        return test_scenario