def roles_usuario(request):
    """
    Este diccionario estará disponible en todos los templates.
    """
    if request.user.is_authenticated:
        return {
            'es_admin': request.user.is_superuser,
            'es_profesor': hasattr(request.user, 'profesor'),
            'es_estudiante': hasattr(request.user, 'estudiante'),
        }
    # Si el usuario no está logueado, todo es falso
    return {
        'es_admin': False,
        'es_profesor': False,
        'es_estudiante': False,
    }