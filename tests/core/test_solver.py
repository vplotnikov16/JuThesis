from JuThesis.core.models import SolverInput
from JuThesis.core.solver import solve, get_start_coverage_generator, _solve_impl


class TestStartCoverageGenerator:
    """
    Тесты генератора начальных покрытий
    """

    def test_generator_k0(self):
        """ K=0: только пустое множество """
        tests = {1, 2, 3}
        gen = list(get_start_coverage_generator(tests, k=0))
        assert gen == [set()]

    def test_generator_k1(self):
        """ K=1: пустое + одиночные """
        tests = {1, 2, 3}
        gen = list(get_start_coverage_generator(tests, k=1))
        expected = [set(), {1}, {2}, {3}]
        assert gen == expected

    def test_generator_k2(self):
        """ K=2: пустое + одиночные + пары """
        tests = {1, 2, 3}
        gen = list(get_start_coverage_generator(tests, k=2))
        expected = [
            set(),  # Пустое
            {1}, {2}, {3},  # Одиночные
            {1, 2}, {1, 3}, {2, 3}  # Пары
        ]
        assert gen == expected


class TestSolveImpl:
    """
    Тесты внутренней функции жадного дополнения
    """

    def test_empty_start_coverage(self):
        """ Жадное дополнение от пустого начального покрытия """
        inp = SolverInput(
            J={1, 2, 3},
            I={1, 2},
            J_i={1: {1, 2}, 2: {2, 3}},
            t_i={1: 2.0, 2: 2.0},
            T=3.0
        )
        result = _solve_impl(inp, h=set())
        # Должен выбрать один тест (оба дают плотность 1.0, выберется первый)
        assert result.f >= 2

    def test_with_initial_coverage(self):
        """ Жадное дополнение с начальным покрытием """
        inp = SolverInput(
            J={1, 2, 3},
            I={1, 2},
            J_i={1: {1, 2}, 2: {3}},
            t_i={1: 1.0, 2: 1.0},
            T=2.0
        )
        result = _solve_impl(inp, h={1})
        # h={1} покрывает {1,2}, осталось время 1.0, добавится тест 2, покрытие {1,2,3}
        assert result.f == 3
        assert result.x == (1, 1)
        assert result.y == (1, 1, 1)


class TestSolver:
    """
    Тесты основной функции solve()
    """

    # ===== Базовые тесты =====

    def test_solve_simple_case(self):
        """ Простейший случай: один тест, одна функция """
        inp = SolverInput(
            J={1},
            I={1},
            J_i={1: {1}},
            t_i={1: 1.0},
            T=2.0
        )
        result = solve(inp)
        assert result.f == 1
        assert result.x == (1,)
        assert result.y == (1,)

    def test_solve_example1(self):
        """ Пример 1 """
        inp = SolverInput(
            J={1, 2, 3, 4, 5, 6},
            I={1, 2, 3, 4},
            J_i={
                1: {1, 2},
                2: {2, 3, 4},
                3: {4, 5},
                4: {3, 6},
            },
            t_i={1: 3, 2: 4, 3: 2, 4: 3},
            T=7,
            K=2
        )
        result = solve(inp)
        # Проверяем, что решение валидное
        assert result.f >= 0
        assert result.f <= 6
        assert len(result.x) == 4
        assert len(result.y) == 6

        # Проверяем бюджет времени
        total_time = sum(inp.t_i[i] for i, selected in enumerate(result.x, 1) if selected)
        assert total_time <= inp.T

    # ===== Граничные случаи =====

    def test_solve_no_budget(self):
        """ Бюджет времени слишком мал """
        inp = SolverInput(
            J={1},
            I={1},
            J_i={1: {1}},
            t_i={1: 10.0},
            T=5.0  # Недостаточно времени
        )
        result = solve(inp)
        assert result.f == 0
        assert result.x == (0,)
        assert result.y == (0,)

    def test_solve_exact_budget(self):
        """ Бюджет времени точно совпадает """
        inp = SolverInput(
            J={1},
            I={1},
            J_i={1: {1}},
            t_i={1: 5.0},
            T=5.0
        )
        result = solve(inp)
        assert result.f == 1
        assert result.x == (1,)

    def test_solve_multiple_tests_full_coverage(self):
        """ Все функции можно покрыть в рамках бюджета """
        inp = SolverInput(
            J={1, 2, 3},
            I={1, 2, 3},
            J_i={1: {1}, 2: {2}, 3: {3}},
            t_i={1: 1.0, 2: 1.0, 3: 1.0},
            T=3.0
        )
        result = solve(inp)
        assert result.f == 3  # Полное покрытие

    def test_solve_overlapping_coverage(self):
        """ Тесты с перекрывающимся покрытием """
        inp = SolverInput(
            J={1, 2, 3},
            I={1, 2},
            J_i={1: {1, 2, 3}, 2: {1, 2}},
            t_i={1: 2.0, 2: 1.0},
            T=2.0
        )
        result = solve(inp)
        # Лучше выбрать тест 1 (покрывает все за время 2.0)
        assert result.f == 3
        assert result.x == (1, 0)

    # ===== Тесты жадного выбора по плотности =====

    def test_solve_greedy_density_selection(self):
        """Выбор теста с максимальной плотностью покрытия"""
        inp = SolverInput(
            J={1, 2, 3, 4},
            I={1, 2},
            J_i={
                1: {1, 2, 3, 4},  # Покрывает 4 функции за время 4 → плотность 1.0
                2: {1, 2},  # Покрывает 2 функции за время 1 → плотность 2.0
            },
            t_i={1: 4.0, 2: 1.0},
            T=5.0
        )
        result = solve(inp)
        # Должен сначала выбрать тест 2 (плотность выше), потом тест 1
        assert result.f == 4
        assert result.x == (1, 1)

    def test_solve_greedy_no_redundant_tests(self):
        """ Не выбираются тесты, не добавляющие покрытия """
        inp = SolverInput(
            J={1, 2},
            I={1, 2, 3},
            J_i={
                1: {1, 2},  # Покрывает все
                2: {1},  # Избыточный
                3: {2},  # Избыточный
            },
            t_i={1: 1.0, 2: 1.0, 3: 1.0},
            T=10.0  # Много времени
        )
        result = solve(inp)
        # Должен выбрать только тест 1
        assert result.f == 2
        assert result.x == (1, 0, 0)

    # ===== Тесты с начальными покрытиями =====

    def test_solve_start_coverage_improves_result(self):
        """ Начальное покрытие помогает получить лучшее решение """
        inp = SolverInput(
            J={1, 2, 3, 4},
            I={1, 2, 3},
            J_i={
                1: {1, 2},
                2: {3, 4},
                3: {1},  # Малополезный тест
            },
            t_i={1: 2.0, 2: 2.0, 3: 1.0},
            T=4.0,
            K=2  # Рассматриваем пары
        )
        result = solve(inp)
        # Ожидается полное покрытие за 4.0)
        assert result.f == 4
        assert result.x == (1, 1, 0)

    # ===== Стресс-тесты =====

    def test_solve_large_instance(self):
        """ Большая задача (производительность) """
        n, m = 20, 15
        inp = SolverInput(
            J=set(range(1, n + 1)),
            I=set(range(1, m + 1)),
            J_i={i: {i, i + 1} if i < n else {i} for i in range(1, m + 1)},
            t_i={i: 1.0 for i in range(1, m + 1)},
            T=10.0,
            K=2
        )
        result = solve(inp)
        # Проверяем только корректность результата
        assert 0 <= result.f <= n
        assert len(result.x) == m
        assert len(result.y) == n

    # ===== Тесты корректности векторов =====

    def test_solve_output_vectors_correct_length(self):
        """ Длины векторов x и y корректны """
        inp = SolverInput(
            J={1, 2, 3},
            I={1, 2},
            J_i={1: {1}, 2: {2}},
            t_i={1: 1.0, 2: 1.0},
            T=2.0
        )
        result = solve(inp)
        assert len(result.x) == inp.m  # m = 2
        assert len(result.y) == inp.n  # n = 3

    def test_solve_x_binary_values(self):
        """ Вектор x содержит только 0 и 1 """
        inp = SolverInput(
            J={1, 2},
            I={1, 2},
            J_i={1: {1}, 2: {2}},
            t_i={1: 1.0, 2: 1.0},
            T=2.0
        )
        result = solve(inp)
        assert all(x in (0, 1) for x in result.x)

    def test_solve_y_binary_values(self):
        """ Вектор y содержит только 0 и 1 """
        inp = SolverInput(
            J={1, 2},
            I={1, 2},
            J_i={1: {1}, 2: {2}},
            t_i={1: 1.0, 2: 1.0},
            T=2.0
        )
        result = solve(inp)
        assert all(y in (0, 1) for y in result.y)

    def test_solve_consistency_x_y(self):
        """ Согласованность x и y: если y[j]=1, то существует x[i]=1 с j из J_i[i] """
        inp = SolverInput(
            J={1, 2, 3},
            I={1, 2},
            J_i={1: {1, 2}, 2: {3}},
            t_i={1: 1.0, 2: 1.0},
            T=2.0
        )
        result = solve(inp)

        # Проверяем: если функция покрыта, то есть тест, который её покрывает
        for j in range(1, inp.n + 1):
            if result.y[j - 1] == 1:
                # Функция j покрыта, должен быть хотя бы один выбранный тест, покрывающий j
                covering_tests = [i for i in range(1, inp.m + 1)
                                  if result.x[i - 1] == 1 and j in inp.J_i[i]]
                assert len(covering_tests) > 0
