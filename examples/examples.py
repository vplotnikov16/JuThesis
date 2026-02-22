def example1():
    """
    Использование решателя напрямую
    """
    from JuThesis.core import solver
    from JuThesis.core.models import SolverInput

    inp = SolverInput(
        # Конечное множество функций/методов, которые требуется покрыть тестированием
        J={1, 2, 3, 4, 5, 6},
        # Конечное множество доступных тестов
        I={1, 2, 3, 4},
        # Покрытия тестов
        J_i={
            1: {1, 2},
            2: {2, 3, 4},
            3: {4, 5},
            4: {3, 6},
        },
        # Время выполнения тестов
        t_i={
            1: 3,
            2: 4,
            3: 2,
            4: 3,
        },
        # Бюджет времени тестирования
        T=7,
        # Максимальная мощность стартового набора тестов H
        K=2
    )

    out = solver.solve(inp)
    print(out)


def example2():
    """
    Решение задачи через протоколы входа/выхода
    """
    from JuThesis.adapters import solve_with_protocol
    from JuThesis.protocols.models import ProtocolInput, TestInfo

    # Создаем входные данные
    protocol_input = ProtocolInput(
        modified_functions=[
            "func1",
            "func2",
            "func3",
            "func4",
            "func5",
            "func6",
        ],
        available_tests={
            "test1": TestInfo(
                time=3.0,
                covered_functions=["func1", "func2", "funcA"],
            ),
            "test2": TestInfo(
                time=4.0,
                covered_functions=["func2", "func3", "func4", "funcB"]
            ),
            "test3": TestInfo(
                time=2.0,
                covered_functions=["func4", "func5", "funcC"]
            ),
            "test4": TestInfo(
                time=3.0,
                covered_functions=["func3", "func6", "funcD"]
            ),
        },
        time_budget=7.0,
        max_initial_coverage_size=2
    )

    # Решаем задачу
    result = solve_with_protocol(protocol_input)

    # Выводим результат
    print(f"Selected tests:     {len(result.tests)}")
    print(f"Covered functions:  {result.total_functions_covered}")
    print(f"Total time:         {result.total_execution_time}")
    for test_info in result.tests:
        print(f"  - {test_info.test}: {test_info.functions}")


def example3():
    """
    Чтение данных из файла json и запись в output.json (вместе с выводом в консоль)
    """
    from JuThesis.adapters import solve_with_protocol
    from JuThesis.io.readers.json_reader import JsonReader
    from JuThesis.io.writers.json_writer import JsonWriter

    inp = JsonReader.read("input.json")
    result = solve_with_protocol(inp)
    JsonWriter.write(result, "output.json")

    # Также выводим результат в консоль
    print(f"Selected tests:     {len(result.tests)}")
    print(f"Covered functions:  {result.total_functions_covered}")
    print(f"Total time:         {result.total_execution_time}")
    for test_info in result.tests:
        print(f"  - {test_info.test}: {test_info.functions}")


if __name__ == "__main__":
    print("Example 1")
    example1()

    print()

    print("Example 2")
    example2()

    print()

    print("Example 3")
    example3()
