import json
from pathlib import Path
from typing import Union

from JuThesis.io.writers.writer_abc import ProtocolWriteError, BaseWriter
from JuThesis.protocols.models import ProtocolOutput


class JsonWriter(BaseWriter):
    @staticmethod
    def write(
            out: ProtocolOutput,
            filepath: Union[str, Path],
            indent: int = 2,
            ensure_ascii: bool = False) -> None:
        filepath = Path(filepath)

        # Создаем директорию, если ее нет
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Сериализация через Pydantic
            data = out.model_dump(mode='python')

            # Запись в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

        except Exception as e:
            raise ProtocolWriteError(f"Error writing to {filepath}: {e}")
