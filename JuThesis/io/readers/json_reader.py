import json
from pathlib import Path
from typing import Union

from pydantic import ValidationError

from JuThesis.io.readers.reader_abc import BaseReader, ProtocolReadError
from JuThesis.protocols.models import ProtocolInput


class JsonReader(BaseReader):
    @staticmethod
    def read(filepath: Union[str, Path]) -> ProtocolInput:
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Input file not found: {filepath}")

        # Чтение файла
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ProtocolReadError(
                f"Invalid JSON format in {filepath}:\n"
                f"  Line {e.lineno}, column {e.colno}: {e.msg}"
            )
        except Exception as e:
            raise ProtocolReadError(f"Error reading file {filepath}: {e}")

        # Валидация через Pydantic
        try:
            protocol_input = ProtocolInput(**data)
        except ValidationError as e:
            # Форматирование ошибок валидации для читаемости
            errors = []
            for error in e.errors():
                loc = " -> ".join(str(l) for l in error['loc'])
                msg = error['msg']
                errors.append(f"  {loc}: {msg}")

            raise ValidationError(
                f"Validation failed for {filepath}:\n" + "\n".join(errors)
            )

        return protocol_input
