from itertools import combinations
from typing import Generator

from JuThesis.core.models import SolverInput, SolverOutput, TestSet


def get_start_coverage_generator(tests: TestSet, k: int = 2) -> Generator[TestSet, None, None]:
    """
    Генератор начальных покрытий H.

    :param tests: множество всех тестов, из которых должны строиться начальные покрытия
    :param k: максимальная мощность начальных покрытий
    :return: генератор всевозможных комбинаций начальных покрытий множества tests
    """
    # Рассматриваем начальные покрытия разной мощности
    for curr_k in range(0, k + 1):
        # Получив начальное покрытия, возвращаем его
        for start_coverage in combinations(sorted(tests), curr_k):
            yield set(start_coverage)


def _solve_impl(inp: SolverInput, h: TestSet) -> SolverOutput:
    """
    Жадное дополнение начального покрытия h до финального решения.

    :param inp: входные данные задачи
    :param h: начальное покрытие (подмножество тестов)
    :return: решение с выбранными тестами и покрытыми функциями
    """
    # Текущие затраты по времени
    w = sum(inp.t_i[i] for i in h)

    # Начальный вектор выбора тестов
    # Индексация: x[i-1] соответствует тесту i из I
    x = [1 if i in h else 0 for i in range(1, inp.m + 1)]

    # Множество уже покрытых функций
    covered = set()
    for i in h:
        covered |= inp.J_i[i]

    remain = inp.T - w

    # Жадное дополнение
    while remain > 0:
        # Вычисляем дельты и плотности для всех невыбранных тестов
        candidates = {}
        for i in inp.I:
            # Рассматриваем еще не выбранный тест
            if x[i - 1] == 0:
                # Сколько новых функций добавит тест i
                new_funcs = inp.J_i[i] - covered
                delta = len(new_funcs)

                # Проверяем, что тест добавляет функции и помещается по времени
                if delta > 0 and inp.t_i[i] <= remain:
                    # Плотность покрытия
                    rho = delta / inp.t_i[i]
                    candidates[i] = rho

        if not candidates:
            # Кандидатов нет, прекращаем жадное дополнение
            break

        # Выбираем тест с максимальной плотностью
        best_i = max(candidates, key=candidates.get)

        # Окончательная проверка
        if inp.t_i[best_i] > remain:
            break

        # Обновляем состояние
        x[best_i - 1] = 1
        w += inp.t_i[best_i]
        remain = inp.T - w
        covered |= inp.J_i[best_i]

    x = tuple(x)
    # y[j-1] соответствует функции j из J
    y = tuple(1 if j in covered else 0 for j in range(1, inp.n + 1))
    return SolverOutput(x=x, y=y)


def solve(inp: SolverInput) -> SolverOutput:
    """
    Решает задачу оптимизации тестового покрытия.

    Перебирает все начальные покрытия H мощности <= K,
    для каждого выполняет жадное дополнение и выбирает лучшее решение.

    :param inp: входные данные задачи
    :return: лучшее найденное решение
    """
    # Перебор начальных покрытиый
    start_cov_generator = get_start_coverage_generator(inp.I, inp.K)
    best: SolverOutput | None = None

    for h_index, h in enumerate(start_cov_generator):
        # Затраты по времени начального покрытия
        w = sum(inp.t_i[i] for i in h)

        # Если начальное покрытие уже не подходит по бюджету времени, то
        # переходим к рассмотрению следующего начального покрытия
        if w > inp.T:
            continue

        result = _solve_impl(inp, h)

        # Выбираем решение с наибольшим значением целевой функции
        if best is None or result.f > best.f:
            best = result

    # Если не нашлось никакого решения, то возвращаем пустое
    if best is None:
        x = tuple(0 for _ in range(inp.m))
        y = tuple(0 for _ in range(inp.n))
        best = SolverOutput(x=x, y=y)

    return best
