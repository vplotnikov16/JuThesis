from abc import abstractmethod, ABC
from pathlib import Path
from typing import Union

from JuThesis.protocols.models import ProtocolInput


class ProtocolReadError(Exception):
    """ Ошибка чтения протокола """
    pass


class BaseReader(ABC):
    @staticmethod
    @abstractmethod
    def read(filepath: Union[str, Path]) -> ProtocolInput:
        """
        Читает входной файл протокола
        :param filepath: путь к входному файлу
        :return: входные данные в формате протокола
        :raises FileNotFoundError: если файл не найден
        :raises ProtocolReadError: если файл не является валидным JSON
        :raises ValidationError: если данные не соответствуют схеме протокола
        """
        raise NotImplementedError
