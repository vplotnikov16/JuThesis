from abc import abstractmethod, ABC
from pathlib import Path
from typing import Union

from JuThesis.protocols.models import ProtocolOutput


class ProtocolWriteError(Exception):
    """ Базовая ошибка записи протокола """
    pass


class BaseWriter(ABC):
    @staticmethod
    @abstractmethod
    def write(
            out: ProtocolOutput,
            filepath: Union[str, Path],
            indent: int = 2,
            ensure_ascii: bool = False) -> None:
        """
        Записывает выходной протокол в файл

        :param out: объект ProtocolOutput с выходными данными для записи
        :param filepath: путь к файлу для записи
        :param indent: количество пробелов для отступа (по умолчанию 2)
        :param ensure_ascii: если True, все не-ASCII символы экранируются
        :raises ProtocolWriteError: если произошла ошибка при записи
        """
        raise NotImplementedError
