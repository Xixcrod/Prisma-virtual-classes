from apps.core.models import Acceso
from django.shortcuts import get_object_or_404, redirect

def panel_solicitudes(request):
    # Obtenemos los datos cruzando las relaciones (Select Related mejora el rendimiento)
    # Aquí ya traemos: Estudiante, su Carrera y el Curso relacionado
    solicitudes = Acceso.objects.filter(estado='PE').select_related('estudiante__carrera', 'curso__materia')
    aceptados = Acceso.objects.filter(estado='AP').select_related('estudiante__carrera', 'curso__materia')
    
    return{
        'solicitudes': solicitudes,
        'aceptados': aceptados
    }

def gestionar_estatus(request, acceso_id, nuevo_estado):
    # 1. Buscamos el registro de acceso por su ID (UUID)
    acceso = get_object_or_404(Acceso, id=acceso_id)
    
    # 2. Actualizamos el estado ('AP' para aceptado, 'RE' para rechazado)
    acceso.estado = nuevo_estado
    acceso.save()
    
    # 3. Redirigimos de vuelta al panel
    return redirect('aceptar_rechazar_solicitud')