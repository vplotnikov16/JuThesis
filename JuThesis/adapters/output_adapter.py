from typing import List, Set

from JuThesis.adapters.input_adapter import InputAdapter
from JuThesis.core.models import SolverOutput
from JuThesis.protocols.models import ProtocolOutput, SelectedTestInfo, ProtocolInput


class OutputAdapter:
    """
    Адаптер для преобразования SolverOutput в ProtocolOutput.

    Использует маппинги из InputAdapter для обратного преобразования
    целочисленных ID в строковые имена.
    """

    @staticmethod
    def adapt(
            solver_output: SolverOutput,
            input_adapter: InputAdapter,
            protocol_input: ProtocolInput
    ) -> ProtocolOutput:
        """
        Преобразует SolverOutput в ProtocolOutput.

        :param solver_output: результат работы решателя
        :param input_adapter: адаптер с маппингами для обратного преобразования
        :param protocol_input: исходные входные данные из протокола
        :return: результат в формате протокола
        """
        # Извлекаем выбранные тесты (где x[i-1] == 1)
        selected_test_ids: List[int] = [
            i for i, selected in enumerate(solver_output.x, start=1)
            if selected == 1
        ]

        # Извлекаем покрытые функции (где y[j-1] == 1)
        covered_function_ids: Set[int] = {
            j for j, covered in enumerate(solver_output.y, start=1)
            if covered == 1
        }

        # Формируем список выбранных тестов с фактическим покрытием
        selected_tests: List[SelectedTestInfo] = []
        total_time = 0.0

        for test_id in selected_test_ids:
            test_name = input_adapter.get_test_name(test_id)
            test_info = protocol_input.available_tests[test_name]

            # Определяем, какие функции этот тест фактически покрывает
            # (пересечение покрытия теста с общим покрытием решения)
            test_coverage_ids = {
                input_adapter.get_function_id(func_name)
                for func_name in test_info.covered_functions
            }

            actually_covered_ids = test_coverage_ids & covered_function_ids

            # Преобразуем ID обратно в имена
            actually_covered_names = [
                input_adapter.get_function_name(func_id)
                for func_id in sorted(actually_covered_ids)
            ]

            selected_tests.append(
                SelectedTestInfo(
                    test=test_name,
                    functions=actually_covered_names
                )
            )

            # Добавляем время выполнения
            total_time += test_info.time

        return ProtocolOutput(
            tests=selected_tests,
            total_execution_time=total_time,  # округляем для читаемости
            total_functions_covered=len(covered_function_ids)
        )
