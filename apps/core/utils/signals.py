from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Acceso, Notificacion


@receiver(post_save, sender=Acceso)
def crear_notificacion_acceso(sender, instance, created, **kwargs):
    # CASO 1: Estudiante solicita acceso (Se crea el registro en Pendiente)
    if created:
        Notificacion.objects.create(
            emisor=instance.estudiante.usuario,
            receptor=instance.curso.profesor.usuario,
            mensaje=f"El/la estudiante {instance.estudiante} solicita acceso al curso: {instance.curso.materia.nombre}.",
        )

    # CASO 2: Profesor cambia el estado (Aprobado/Rechazado)
    else:
        # Aquí notificamos al estudiante sobre la decisión del profesor
        # Seguridad de que se modifique solo el campo "estado".
        update_fields = kwargs.get("update_fields") or set()
        if "estado" in update_fields:
            estado_texto = dict(Acceso.PERMISOS).get(instance.estado)
            Notificacion.objects.create(
                emisor=instance.curso.profesor.usuario,
                receptor=instance.estudiante.usuario,
                mensaje=f"Tu solicitud para el curso {instance.curso.materia.nombre} ha sido cambiada a: {estado_texto}.",
            )
