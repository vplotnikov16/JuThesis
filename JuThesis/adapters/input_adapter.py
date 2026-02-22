from typing import Dict

from JuThesis.core.models import SolverInput, FunctionsSet, TestSet, Test
from JuThesis.protocols.models import ProtocolInput


class InputAdapter:
    """
    Адаптер для преобразования ProtocolInput в SolverInput.

    Создает маппинги между строковыми именами (функций и тестов)
    и целочисленными ID, необходимыми для решателя.
    """

    def __init__(self):
        # Маппинги для обратного преобразования
        self._function_id_to_name: Dict[int, str] = {}
        self._function_name_to_id: Dict[str, int] = {}
        self._test_id_to_name: Dict[int, str] = {}
        self._test_name_to_id: Dict[str, int] = {}

    def adapt(self, protocol_input: ProtocolInput) -> SolverInput:
        """
        Преобразует ProtocolInput в SolverInput.

        :param protocol_input: входные данные в формате протокола
        :return: входные данные для ядра решателя
        """
        # Создаем отображение function_name в id (от 1 до n)
        self._function_name_to_id = {
            name: idx
            for idx, name in enumerate(protocol_input.modified_functions, start=1)
        }
        self._function_id_to_name = {
            idx: name
            for name, idx in self._function_name_to_id.items()
        }

        # Создаем отображение test_name в id (от 1 до m)
        self._test_name_to_id = {
            name: idx
            for idx, name in enumerate(protocol_input.available_tests.keys(), start=1)
        }
        self._test_id_to_name = {
            idx: name
            for name, idx in self._test_name_to_id.items()
        }

        # Множество функций {1, 2, ..., n}
        J: FunctionsSet = set(self._function_name_to_id.values())

        # Множество тестов {1, 2, ..., m}
        I: TestSet = set(self._test_name_to_id.values())

        # Покрытия тестов
        J_i: Dict[Test, FunctionsSet] = {}
        for test_name, test_info in protocol_input.available_tests.items():
            test_id = self._test_name_to_id[test_name]
            # Преобразуем имена функций в ID
            covered_function_ids = {
                self._function_name_to_id[func_name]
                for func_name in test_info.covered_functions
                if func_name in self._function_name_to_id  # фильтруем лишние
            }
            J_i[test_id] = covered_function_ids

        # Времена выполнения тестов
        t_i: Dict[Test, float] = {
            self._test_name_to_id[test_name]: test_info.time
            for test_name, test_info in protocol_input.available_tests.items()
        }

        # Бюджет времени
        T = protocol_input.time_budget

        # Максимальный размер начального покрытия
        K = protocol_input.max_initial_coverage_size

        return SolverInput(J=J, I=I, J_i=J_i, t_i=t_i, T=T, K=K)

    def get_function_name(self, function_id: int) -> str | None:
        """ Получить имя функции по ID """
        return self._function_id_to_name.get(function_id)

    def get_function_id(self, function_name: str) -> int | None:
        """ Получить ID функции по имени """
        return self._function_name_to_id.get(function_name)

    def get_test_name(self, test_id: int) -> str | None:
        """ Получить имя теста по ID """
        return self._test_id_to_name.get(test_id)

    def get_test_id(self, test_name: str) -> int:
        """ Получить ID теста по имени """
        return self._test_name_to_id.get(test_name)
