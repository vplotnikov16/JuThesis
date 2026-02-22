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
    # Текущие затраты по времени
    w = sum(inp.t_i[i] for i in h)

    # TODO Начальный вектор x должен быть tuple сразу
    x = [0] * inp.m
    for i in h:
        x[i - 1] = 1
    x = tuple(x)

    # Множество уже покрытых функций
    covered = set()
    for i in h:
        covered |= inp.J_i[i]

    remain = inp.T - w

    # Жадное дополнение
    while True:
        # Если времени не осталось, то заканчиваем жадное дополнение
        if remain <= 0:
            break

        # Вычисляем дельты для всех невыбранных тестов
        deltas = {}
        for i in sorted(inp.I):
            if x[i - 1] == 0:
                # сколько новых функций добавит тест i относительно текущего покрытия
                new_funcs = inp.J_i[i].difference(covered)
                delta = len(new_funcs)
                # флаг "помещается ли тест в оставшееся время"
                time_ok = inp.t_i[i] <= remain
                deltas[i] = (delta, time_ok)
            else:
                # i - уже выбранный тест
                pass

        candidates = {}
        for i, (delta, time_ok) in deltas.items():
            if delta > 0 and time_ok:
                rho = delta / inp.t_i[i]
                candidates[i] = (delta, rho)

        if not candidates:
            # Кандидатов нет, прекращаем жадное дополнение
            break

        best_i: int | None = None
        best_rho: float | None = None
        for i in sorted(candidates):
            delta, rho = candidates[i]
            if best_rho is None or rho > best_rho:
                best_rho = rho
                best_i = i

        # Окончательная проверка
        if inp.t_i[best_i] > remain:
            break

        # Выставляет тест best_i как выбранный
        x = tuple(x[i] if i != (best_i - 1) else 1 for i in range(len(x)))
        # Обновляем затраты по времени
        w = w + inp.t_i[best_i]
        remain = inp.T - w
        covered |= inp.J_i[best_i]

    y = tuple(1 if j in covered else 0 for j in sorted(inp.J))
    return SolverOutput(x=x, y=y)


def solve(inp: SolverInput) -> SolverOutput:
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
        if best is None or best.f > result.f:
            best = result

    return best
