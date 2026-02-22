import warnings
from typing import Set, Dict, Tuple

from pydantic import BaseModel, field_validator, model_validator
from pydantic.dataclasses import dataclass as pydantic_dataclass

Function_or_Method = int
FunctionsSet = Set[Function_or_Method]

Test = int
TestSet = Set[Test]


class SolverInput(BaseModel):
    """
    Входные параметры для решателя.

    J = {1, 2, ..., n} - функции нумеруются с 1 до n
    I = {1, 2, ..., m} - тесты нумеруются с 1 до m
    """
    # Конечное множество функций/методов, которые требуется покрыть тестированием
    J: FunctionsSet
    # Конечное множество доступных тестов
    I: TestSet
    # Покрытия тестов
    J_i: Dict[Test, FunctionsSet]
    # Время выполнения тестов
    t_i: Dict[Test, float]
    # Бюджет времени тестирования
    T: float
    # Максимальная мощность стартового набора тестов H
    K: int = 2

    model_config = {
        'frozen': True,
        # Нужно для работы с set
        "arbitrary_types_allowed": True,
    }

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

    @field_validator('J')
    @classmethod
    def validate_J_continuous(cls, v: FunctionsSet) -> FunctionsSet:
        """
        Проверка, что J = {1, 2, ..., n}
        :param v: исходный J
        :return: при успешной валидации возвращает v (исходный J)
        :raises ValueError: в случае, если J не соответствует требованию
        """

        n = len(v)
        expected = set(range(1, n + 1))
        if v != expected:
            raise ValueError(f"Expected J={{1, 2, ..., {n}}}, got: {v}.")
        return v

    @field_validator('I')
    @classmethod
    def validate_I_continuous(cls, v: TestSet) -> TestSet:
        """
        Проверка, что I = {1, 2, ..., m}
        :param v: исходный I
        :return: при успешной валидации возвращает v (исходный I)
        :raises ValueError: в случае, если I не соответствует требованию
        """

        m = len(v)
        expected = set(range(1, m + 1))
        if v != expected:
            raise ValueError(f"Expected I={{1, 2, ..., {m}}}, got: {v}.")
        return v

    @field_validator('T')
    @classmethod
    def validate_T_positive(cls, v: float) -> float:
        """
        Проверка, что бюджет времени положительный
        :param v: исходный T
        :return: при успешной валидации возвращает v (исходный T)
        :raises ValueError: в случае, если T <= 0
        """
        if v <= 0:
            raise ValueError(f"Expected T > 0, got: {v}.")
        return v

    @field_validator('K')
    @classmethod
    def validate_k_non_negative(cls, v: int) -> int:
        """
        Проверка, что K - неотрицательное число
        :param v: исходный K
        :return: при успешной валидации возвращает v (исходный K)
        :raises ValueError: в случае K < 0
        """
        if v < 0:
            raise ValueError(f"Expected K >= 0, got: {v}.")
        return v

    @model_validator(mode='after')
    def validate_J_i_keys(self):
        """
        Проверка корректности ключей J_i:
        - все ключи J_i должны быть в I
        - для всех тестов из I должно быть определено покрытие
        """
        # все ключи J_i должны быть в I
        extra_keys = set(self.J_i.keys()) - self.I
        if extra_keys:
            raise ValueError(f"J_i contains tests that are not in I: {extra_keys}")

        # для всех тестов из I должно быть определено покрытие
        missing_keys = self.I - set(self.J_i.keys())
        if missing_keys:
            raise ValueError(
                f"Coverage data not defined for all tests in J_i: {missing_keys}"
            )

        return self

    @model_validator(mode='after')
    def validate_J_i_values(self):
        """
        Проверка, что все покрытия являются подмножествами J
        """
        for test_id, coverage in self.J_i.items():
            if not coverage.issubset(self.J):
                extra_funcs = coverage - self.J
                raise ValueError(
                    f"Coverage of test {test_id} contains functions not in J: {extra_funcs}"
                )
        return self

    @model_validator(mode='after')
    def validate_t_i_keys(self):
        """
        Проверка корректности ключей t_i:
        - все ключи t_i должны быть в I
        - для всех тестов из I должно быть определено время
        """
        # все ключи t_i должны быть в I
        extra_keys = set(self.t_i.keys()) - self.I
        if extra_keys:
            raise ValueError(
                f"t_i contains definitions for tests not in I: {extra_keys}"
            )

        # для всех тестов из I должно быть определено время
        missing_keys = self.I - set(self.t_i.keys())
        if missing_keys:
            raise ValueError(
                f"Execution time not defined for all tests in t_i: {missing_keys}"
            )

        return self

    @model_validator(mode='after')
    def validate_t_i_positive(self):
        """
        Проверка, что все времена выполнения положительные
        """
        non_positive = {test_id: time for test_id, time in self.t_i.items() if time <= 0}
        if non_positive:
            raise ValueError(
                f"Test execution times must be greater than zero, invalid values: {non_positive}"
            )
        return self

    @model_validator(mode='after')
    def warn_uncovered_functions(self):
        """
        Предупреждение о непокрываемых функциях
        """
        all_covered = set().union(*self.J_i.values()) if self.J_i else set()
        uncovered = self.J - all_covered

        if uncovered:
            warnings.warn(
                f"Warning!!! There are functions/methods in J that are not covered by any test: {uncovered}",
                UserWarning,
                stacklevel=2
            )

        return self


@pydantic_dataclass(frozen=True)
class SolverOutput:
    """
    Результат работы решателя
    """
    # Вектор "какие тесты выбраны"
    x: Tuple[Test] | Tuple[Test, ...]
    # Вектор "какие функции покрыты"
    y: Tuple[Function_or_Method] | Tuple[Function_or_Method, ...]

    @property
    def f(self):
        """
        Целевая функция
        :return: количество покрытых функций
        """
        return sum(self.y)
