from apps.core.models import Carrera, Materia

# 1. Crear o recuperar las carreras
sistemas, _ = Carrera.objects.get_or_create(nombre="Ing en Sistemas", cantidad_semestres=9)
naval, _ = Carrera.objects.get_or_create(nombre="Ing Naval", cantidad_semestres=9)

# 2. Materias para Ing en sistemas
Materia.objects.get_or_create(nombre="Seminario", carrera=sistemas, semestre=1)
Materia.objects.get_or_create(nombre="Matemáticas I", carrera=sistemas, semestre=1)
Materia.objects.get_or_create(nombre="Matemáticas II", carrera=sistemas, semestre=2)
Materia.objects.get_or_create(nombre="Cálculo numérico", carrera=sistemas, semestre=3)

# 3. Materias para Ing naval
#Menos idea de que dan en ing naval
Materia.objects.get_or_create(nombre="Introducción a la Ing Naval", carrera=naval, semestre=1)
Materia.objects.get_or_create(nombre="Dibujo Técnico", carrera=naval, semestre=1)
Materia.objects.get_or_create(nombre="Dibujo técnico II", carrera=naval, semestre=2)
Materia.objects.get_or_create(nombre="Barquitos", carrera=naval, semestre=3)

print("Carreras y materias de ingeniería cargadas")