from dataclasses import dataclass
from django.db import models
from typing import Type


# Clase construtora de configuraciones de acceso a archivos multimedia con estructura sólida.
@dataclass
class MediaConfig:
    model: Type[models.Model]
    file_field: str
    alias: str
