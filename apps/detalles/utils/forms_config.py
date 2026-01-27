from dataclasses import dataclass, field
from typing import Type, Optional, Set
from django import forms


# Clase predeterminada para guardar de forma estática e inmutable las configuraciones de formularios.
@dataclass
class FormConfig:
    form_class: Type[forms.BaseForm]
    is_create: bool = False
    prefix: Optional[str] = None
    roles: Set[str] = field(default_factory=set)
