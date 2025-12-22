from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.

# Usuarios generico

class Usuario(AbstractUser):
    id = models.UUIDField(
        primary_key=True,   # Lo convierte en el identificador principal
        default=uuid.uuid4,  # Genera un código aleatorio automáticamente
        editable=False      # Impide que se pueda modificar manualmente
    )

    # Incluyendo: first_name, last_name, password, email, date_joined if_superuser
    telefono = models.CharField(max_length=11)
    cedula = models.CharField(max_length=8, unique=True)

    # Esto le dice a Django: "Usa la cédula para el login en lugar del username"
    USERNAME_FIELD = 'cedula'

    # Estos campos se pedirán obligatoriamente al crear un superusuario por consola (createsuperuser)
    # Nota: 'username' pasa a ser un campo secundario, pero Django lo requiere por defecto en AbstractUser
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'email']

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' - ' + self.cedula


# Carreras
class Carrera(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    nombre = models.CharField(max_length=75, unique=True)
    cantidad_semestres = models.IntegerField()

    def __str__(self):
        return self.nombre


# Estudiantes
class Estudiante(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.first_name + ' ' + self.usuario.last_name


# Profesores
class Profesor(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.usuario.first_name + ' ' + self.usuario.last_name


# Materias de las carreras
class Materia(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    nombre = models.CharField(max_length=75)
    semestre = models.IntegerField()
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


# Cursos (Es una instancia de materia que el profesor si puede modificar)
class Curso(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='images/cursos/', blank=True, null=True)

    def __str__(self):
        return self.materia.nombre + ' - ' + self.profesor.usuario.first_name + ' ' + self.profesor.usuario.last_name


# Temas (Son las agrupaciones de videos dentro del curso)
class Tema(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=75)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='images/temas/', blank=True, null=True)

    def __str__(self):
        return self.titulo


# Videos
class Video(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=75)
    resumen = models.TextField()
    duracion = models.CharField(max_length=8)
    url_video = models.FileField(upload_to='videos/')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


# Videos favoritos
class Favorito(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    class Meta:
        # Evita duplicados (el mismo estudiante no puede dar like al mismo video 2 veces)
        unique_together = ('estudiante', 'video')

    def __str__(self):
        return self.estudiante.usuario.first_name + ' ' + self.estudiante.usuario.last_name + ' - ' + self.video.titulo


# Accesos de los estudiantes al curso del profesor
class Acceso(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    class Meta:
        # IMPORTANTE: Un estudiante solo debe tener un registro de acceso por curso
        unique_together = ('estudiante', 'curso')

    # Selector de permiso de acceso
    PERMISOS = [
        ('PE', 'Pendiente'),
        ('AP', 'Aprobado'),
        ('RE', 'Rechazado'),
    ]
    estado = models.CharField(max_length=2, choices=PERMISOS)

    def __str__(self):
        return self.estudiante.usuario.first_name + ' ' + self.estudiante.usuario.last_name + ' - ' + self.curso.materia.nombre


# Notifiaciones que es una bandeja de mensajes
class Notificacion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    emisor = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='notificaciones_enviadas')
    receptor = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='notificaciones_recibidas')
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.emisor.first_name + ' ' + self.emisor.last_name + ' - ' + self.receptor.first_name + ' ' + self.receptor.last_name
