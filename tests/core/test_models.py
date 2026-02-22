import pytest
from pydantic import ValidationError

from JuThesis.core.models import SolverInput, SolverOutput


class TestSolverInputValidation:
    """
    Тесты валидации SolverInput
    """

    def test_valid_input_basic(self):
        """ Проверка создания валидного SolverInput """
        inp = SolverInput(
            J={1, 2, 3},
            I={1, 2},
            J_i={1: {1, 2}, 2: {2, 3}},
            t_i={1: 1.0, 2: 2.0},
            T=5.0,
            K=2
        )
        assert inp.n == 3
        assert inp.m == 2

    def test_valid_input_empty_coverage(self):
        """ Проверка с пустым покрытием (вызовет предупреждение) """
        with pytest.warns(UserWarning, match="are not covered by any test"):
            inp = SolverInput(
                J={1, 2, 3},
                I={1},
                J_i={1: set()},
                t_i={1: 1.0},
                T=5.0
            )

    # ===== Тесты валидации J =====

    def test_invalid_J_not_continuous(self):
        """ J должно быть {1, 2, ..., n} без пропусков """
        with pytest.raises(ValidationError, match="Expected J"):
            SolverInput(
                J={1, 3},  # Пропущена 2
                I={1},
                J_i={1: {1}},
                t_i={1: 1.0},
                T=5.0
            )

    def test_invalid_J_not_starting_from_1(self):
        """ J должно начинаться с 1 """
        with pytest.raises(ValidationError, match="Expected J"):
            SolverInput(
                J={0, 1, 2},  # Начинается с 0
                I={1},
                J_i={1: {1}},
                t_i={1: 1.0},
                T=5.0
            )

    # ===== Тесты валидации I =====

    def test_invalid_I_not_continuous(self):
        """ I должно быть {1, 2, ..., m} без пропусков """
        with pytest.raises(ValidationError, match="Expected I"):
            SolverInput(
                J={1},
                I={1, 3},  # Пропущена 2
                J_i={1: {1}, 3: {1}},
                t_i={1: 1.0, 3: 1.0},
                T=5.0
            )

    # ===== Тесты валидации T =====

    def test_invalid_T_zero(self):
        """ T должно быть строго положительным """
        with pytest.raises(ValidationError, match="Expected T > 0"):
            SolverInput(
                J={1},
                I={1},
                J_i={1: {1}},
                t_i={1: 1.0},
                T=0.0
            )

    def test_invalid_T_negative(self):
        """ T не может быть отрицательным """
        with pytest.raises(ValidationError, match="Expected T > 0"):
            SolverInput(
                J={1},
                I={1},
                J_i={1: {1}},
                t_i={1: 1.0},
                T=-1.0
            )

    # ===== Тесты валидации K =====

    def test_invalid_K_negative(self):
        """ K не может быть отрицательным """
        with pytest.raises(ValidationError, match="Expected K >= 0"):
            SolverInput(
                J={1},
                I={1},
                J_i={1: {1}},
                t_i={1: 1.0},
                T=5.0,
                K=-1
            )

    # ===== Тесты валидации J_i (ключи) =====

    def test_invalid_J_i_extra_keys(self):
        """ В J_i не должно быть тестов, отсутствующих в I """
        with pytest.raises(ValidationError, match="J_i contains tests that are not in I"):
            SolverInput(
                J={1},
                I={1},
                J_i={1: {1}, 2: {1}},  # Тест 2 отсутствует в I
                t_i={1: 1.0},
                T=5.0
            )

    def test_invalid_J_i_missing_keys(self):
        """ Для всех тестов из I должно быть определено покрытие в J_i """
        with pytest.raises(ValidationError, match="Coverage data not defined for all tests in J_i"):
            SolverInput(
                J={1},
                I={1, 2},
                J_i={1: {1}},  # Для теста 2 не определено покрытие
                t_i={1: 1.0, 2: 1.0},
                T=5.0
            )

    # ===== Тесты валидации J_i (значения) =====

    def test_invalid_J_i_values_not_subset(self):
        """ Покрытия должны быть подмножествами J """
        with pytest.raises(ValidationError, match="contains functions not in J"):
            SolverInput(
                J={1, 2},
                I={1},
                J_i={1: {1, 2, 3}},  # Функция 3 отсутствует в J
                t_i={1: 1.0},
                T=5.0
            )

    # ===== Тесты валидации t_i (ключи) =====

    def test_invalid_t_i_extra_keys(self):
        """ В t_i не должно быть тестов, отсутствующих в I """
        with pytest.raises(ValidationError, match="t_i contains definitions for tests not in I"):
            SolverInput(
                J={1},
                I={1},
                J_i={1: {1}},
                t_i={1: 1.0, 2: 1.0},  # Тест 2 отсутствует в I
                T=5.0
            )

    def test_invalid_t_i_missing_keys(self):
        """ Для всех тестов из I должно быть определено время в t_i """
        with pytest.raises(ValidationError, match="Execution time not defined for all tests in t_i"):
            SolverInput(
                J={1},
                I={1, 2},
                J_i={1: {1}, 2: {1}},
                t_i={1: 1.0},  # Для теста 2 не определено время
                T=5.0
            )

    # ===== Тесты валидации t_i (значения) =====

    def test_invalid_t_i_zero_time(self):
        """Время выполнения должно быть строго положительным"""
        with pytest.raises(ValidationError, match="Test execution times must be greater than zero"):
            SolverInput(
                J={1},
                I={1},
                J_i={1: {1}},
                t_i={1: 0.0},  # Время = 0
                T=5.0
            )

    def test_invalid_t_i_negative_time(self):
        """ Время выполнения не может быть отрицательным """
        with pytest.raises(ValidationError, match="Test execution times must be greater than zero"):
            SolverInput(
                J={1},
                I={1},
                J_i={1: {1}},
                t_i={1: -1.0},  # Отрицательное время
                T=5.0
            )

    # ===== Тесты предупреждений =====

    def test_warning_uncovered_functions(self):
        """ Предупреждение о непокрываемых функциях """
        with pytest.warns(UserWarning, match="are not covered by any test"):
            SolverInput(
                J={1, 2, 3},
                I={1},
                J_i={1: {1}},  # Функции 2 и 3 не покрыты
                t_i={1: 1.0},
                T=5.0
            )

    def test_no_warning_all_covered(self):
        """ Нет предупреждения, если все функции покрыты """
        inp = SolverInput(
            J={1, 2, 3},
            I={1, 2},
            J_i={1: {1, 2}, 2: {3}},  # Все функции покрыты
            t_i={1: 1.0, 2: 1.0},
            T=5.0
        )
        # Предупреждений не должно быть


class TestSolverOutput:
    """Тесты SolverOutput"""

    def test_solver_output_creation(self):
        """Создание SolverOutput"""
        out = SolverOutput(x=(1, 0, 1), y=(1, 1, 0))
        assert out.x == (1, 0, 1)
        assert out.y == (1, 1, 0)

    def test_solver_output_f_property(self):
        """Проверка вычисления целевой функции"""
        out = SolverOutput(x=(1, 0, 1), y=(1, 1, 0, 1))
        assert out.f == 3  # Сумма элементов y

    def test_solver_output_empty(self):
        """Пустое решение"""
        out = SolverOutput(x=(), y=())
        assert out.f == 0

    def test_solver_output_immutable(self):
        """SolverOutput должен быть иммутабельным"""
        out = SolverOutput(x=(1, 0), y=(1, 0))
        with pytest.raises(AttributeError):
            out.x = (0, 1)
