function updateSelectors() {
    const radios = document.getElementsByName('rol');
    const carreraGroup = document.getElementById('carrera-group');
    const carreraSelect = document.getElementById('carrera');
    const labelProfesor = document.getElementById('label-profesor');
    const labelEstudiante = document.getElementById('label-estudiante');

    let selected = 'estudiante';
    for (const r of radios) {
        if (r.checked) {
            selected = r.value;
            break;
        }
    }

    // Actualizar estilos de texto activo
    if (selected === 'profesor') {
        if (labelProfesor) labelProfesor.classList.add('active');
        if (labelEstudiante) labelEstudiante.classList.remove('active');

        // Ocultar carrera (Profesores no tienen carrera en registro inicial)
        if (carreraGroup) carreraGroup.style.display = 'none';
        if (carreraSelect) carreraSelect.required = false;
    } else {
        if (labelEstudiante) labelEstudiante.classList.add('active');
        if (labelProfesor) labelProfesor.classList.remove('active');

        // Mostrar carrera
        if (carreraGroup) carreraGroup.style.display = 'block';
        if (carreraSelect) carreraSelect.required = true;
    }
}

// Ejecutar al inicio
document.addEventListener('DOMContentLoaded', updateSelectors);
