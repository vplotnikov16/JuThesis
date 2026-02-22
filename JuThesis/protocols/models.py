from pathlib import Path
from typing import List, Dict, Type

from pydantic import BaseModel

INPUT_PROTOCOL_VERSION = "1.0.0"
OUTPUT_PROTOCOL_VERSION = "1.0.0"


class TestInfo(BaseModel):
    """ Информация о тесте """
    # Время выполнения теста в секундах
    time: float
    # Список покрываемых функций
    covered_functions: List[str]


class ProtocolInput(BaseModel):
    """ Входной протокол """
    version: str = INPUT_PROTOCOL_VERSION
    # Уникальные имена измененных функций/методов
    modified_functions: List[str]
    # Информация о доступных тестах
    available_tests: Dict[str, TestInfo]
    # Общий бюджет времени в секундах
    time_budget: float
    # Максимальный размер начального покрытия (K)
    max_initial_coverage_size: int


class SelectedTestInfo(BaseModel):
    """ Информация о выбранном тесте """
    # Название теста
    test: str
    # Фактически покрываемые функции
    functions: List[str]


class ProtocolOutput(BaseModel):
    """ Выходной протокол """
    version: str = OUTPUT_PROTOCOL_VERSION
    # Выбранные тесты
    tests: List[SelectedTestInfo]
    # Суммарное время выполнения
    total_execution_time: float
    # Количество покрытых функций
    total_functions_covered: int


def _generate_schema_impl(
        model_type: Type[ProtocolInput | ProtocolOutput],
        version: str,
        indent: int = 2,
        schemas_dir: Path = Path(__file__).parent / "schemas"):
    schema = model_type.model_json_schema()
    schema_name = f"{model_type.__name__}_v{version}.json"

    # Создаем директорию, если ее нет
    schemas_dir.mkdir(parents=True, exist_ok=True)

    import json
    with open(schemas_dir / schema_name, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=indent, ensure_ascii=False)

    print(f"Generated schema: {schemas_dir / schema_name}")


def generate_schemas(indent: int = 2):
    """ Генерация JSON Schema из моделей Pydantic """

    # Схема входного файла
    _generate_schema_impl(ProtocolInput, INPUT_PROTOCOL_VERSION, indent)
    # Схема выходного файла
    _generate_schema_impl(ProtocolOutput, OUTPUT_PROTOCOL_VERSION, indent)


if __name__ == '__main__':
    generate_schemas(indent=2)
