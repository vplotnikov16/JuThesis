from dataclasses import dataclass
from typing import Set, Dict, Tuple

Function_or_Method = int
FunctionsSet = Set[Function_or_Method]

Test = int
TestSet = Set[Test]


@dataclass(frozen=True)
class SolverInput:
    """
    Входные параметры для решателя
    """
    # Конечное множество функций/методов, которые требуется покрыть тестированием
    J: FunctionsSet
    # Конечное множество доступных тестов
    I: TestSet
    # Покрытия тестов
    J_i: Dict[Test, FunctionsSet]
    # Время выполнения тестов
    t_i: Dict[Test, int]
    # Бюджет времени тестирования
    T: int
    # Максимальная мощность стартового набора тестов H
    K: int = 2

    @property
    def n(self) -> int:
        """
        Количество функций/методов, которые требуется покрыть тестированием
        (Мощность множества J)
        """
        return len(self.J)

    @property
    def m(self) -> int:
        """
        Количество доступных тестов
        (Мощность множества I)
        """
        return len(self.I)


@dataclass(frozen=True)
class SolverOutput:
    """
    Результат работы решателя
    """
    # Вектор "какие тесты выбраны"
    x: Tuple[Test]
    # Вектор "какие функции покрыты"
    y: Tuple[Function_or_Method]

    @property
    def f(self):
        """
        Целевая функция
        :return: количество покрытых функций
        """
        return sum(self.y)
