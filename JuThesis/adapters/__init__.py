"""
Адаптеры для работы с протоколом ввода/вывода.

Предоставляют преобразование между форматом протокола (строковые имена) и форматом решателя
"""

from JuThesis.adapters.input_adapter import InputAdapter
from JuThesis.adapters.output_adapter import OutputAdapter
from JuThesis.core import solver
from JuThesis.protocols.models import ProtocolInput, ProtocolOutput


def solve_with_protocol(protocol_input: ProtocolInput) -> ProtocolOutput:
    """
    Решает задачу оптимизации тестового покрытия, используя протокол.

    Единая точка входа для работы с JuThesis через протокол.
    Выполняет последовательность:
    1. Преобразование ProtocolInput в SolverInput (через InputAdapter)
    2. Решение задачи через solver.solve
    3. Преобразование SolverOutput в ProtocolOutput (через OutputAdapter)

    :param protocol_input: входные данные в формате протокола
    :return: результат в формате протокола
    """
    # Преобразование ProtocolInput в SolverInput
    inp_adapter = InputAdapter()
    solver_input = inp_adapter.adapt(protocol_input)

    # Решение задачи
    solver_output = solver.solve(solver_input)

    # Преобразование SolverOutput в ProtocolOutput
    protocol_output = OutputAdapter.adapt(
        solver_output=solver_output,
        input_adapter=inp_adapter,
        protocol_input=protocol_input
    )

    return protocol_output


__all__ = [
    'InputAdapter',
    'OutputAdapter',
    'solve_with_protocol',
]
