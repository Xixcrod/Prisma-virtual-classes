document.addEventListener('DOMContentLoaded', function () {
    // Auto-ocultar mensajes de alerta después de 4 segundos
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            });
        }, 4000);
    }

    // Modal para añadir carrera
    const modal = document.getElementById("careerModal");
    const btn = document.getElementById("btnOpenCareerModal");
    const span = document.querySelector("#careerModal .close-modal");

    // Modal para eliminar carrera
    const deleteModal = document.getElementById("deleteCareerModal");
    const deleteBtn = document.getElementById("btnOpenDeleteCareerModal");
    const deleteSpan = document.querySelector("#deleteCareerModal .close-modal");

    // Modal para añadir materia
    const subjectModal = document.getElementById("subjectModal");
    const btnSubject = document.getElementById("btnOpenSubjectModal");
    const spanSubject = document.querySelector("#subjectModal .close-modal");

    // Modal para eliminar materia
    const deleteSubjectModal = document.getElementById("deleteSubjectModal");
    const btnDeleteSubject = document.getElementById("btnOpenDeleteSubjectModal");
    const spanDeleteSubject = document.querySelector("#deleteSubjectModal .close-modal");

    // Modal para editar carrera
    const editModal = document.getElementById("editCareerModal");
    const editSpan = document.querySelector("#editCareerModal .close-modal");
    const editButtons = document.querySelectorAll(".open-edit-career-modal");
    const editForm = document.getElementById("editCareerForm");

    // Modal para editar materia
    const editSubjectModal = document.getElementById("editSubjectModal");
    const editSubjectSpan = document.querySelector("#editSubjectModal .close-modal");
    const editSubjectButtons = document.querySelectorAll(".open-edit-subject-modal");
    const editSubjectForm = document.getElementById("editSubjectForm");

    // Añadir carrera: Mostrar modal al hacer clic en el botón
    if (btn) {
        btn.onclick = function () {
            modal.style.display = "flex"; // Usamos flex para centrar gracias al CSS existente
        }
    }

    // Cierra el modal al hacer click en X
    if (span) {
        span.onclick = function () {
            modal.style.display = "none";
        }
    }

    // Eliminar carrera: Mostrar modal
    if (deleteBtn) {
        deleteBtn.onclick = function () {
            deleteModal.style.display = "flex";
        }
    }

    // Eliminar carrera: Cerrar modal
    if (deleteSpan) {
        deleteSpan.onclick = function () {
            deleteModal.style.display = "none";
        }
    }

    // Añadir materia: Mostrar modal al hacer clic en el botón
    if (btnSubject) {
        btnSubject.onclick = function () {
            subjectModal.style.display = "flex";
        }
    }

    // Añadir materia: Cerrar modal
    if (spanSubject) {
        spanSubject.onclick = function () {
            subjectModal.style.display = "none";
        }
    }

    // Eliminar materia: Mostrar modal
    if (btnDeleteSubject) {
        btnDeleteSubject.onclick = function () {
            deleteSubjectModal.style.display = "flex";
        }
    }

    // Eliminar materia: Cerrar modal
    if (spanDeleteSubject) {
        spanDeleteSubject.onclick = function () {
            deleteSubjectModal.style.display = "none";
        }
    }

    // Editar carrera: Configurar todos los botones de edición
    if (editButtons) {
        editButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                // Obtiene datos del botón usando atributos data-*
                const nombre = this.getAttribute('data-nombre');
                const semestres = this.getAttribute('data-semestres');
                const url = this.getAttribute('data-url'); //url para enviar al formulario.

                // Llena los campos del formulario con los datos obtenidos
                document.getElementById('editCareerName').value = nombre;
                document.getElementById('editCareerSemesters').value = semestres;
                editForm.action = url; // Actualiza la acción del formulario

                // Muestra el modal
                editModal.style.display = "flex";
            });
        });
    }
    // Editar materia: Configurar, hace la misma funcion que el modal pasado asi que no hace falta especificar
    if (editSubjectButtons) {
        editSubjectButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                const nombre = this.getAttribute('data-nombre');
                const semestre = this.getAttribute('data-semestre');
                const carreraId = this.getAttribute('data-carrera');
                const url = this.getAttribute('data-url');

                document.getElementById('editSubjectName').value = nombre;
                document.getElementById('editSubjectSemester').value = semestre;
                document.getElementById('editSubjectCareer').value = carreraId;
                editSubjectForm.action = url;

                editSubjectModal.style.display = "flex";
            });
        });
    }

    if (editSpan) {
        editSpan.onclick = function () {
            editModal.style.display = "none";
        }
    }

    if (editSubjectSpan) {
        editSubjectSpan.onclick = function () {
            editSubjectModal.style.display = "none";
        }
    }

    // Cerrar modales al hacer click afuera de ellos
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
        if (event.target == deleteModal) {
            deleteModal.style.display = "none";
        }
        if (event.target == subjectModal) {
            subjectModal.style.display = "none";
        }
        if (event.target == deleteSubjectModal) {
            deleteSubjectModal.style.display = "none";
        }
        if (event.target == editModal) {
            editModal.style.display = "none";
        }
        if (event.target == editSubjectModal) {
            editSubjectModal.style.display = "none";
        }
    }

    // Validación de formularios

    // Validación del formulario de añadir carrera
    const addCareerForm = document.getElementById('addCareerForm');
    const addSubjectForm = document.getElementById('addSubjectForm');

    if (addCareerForm) {
        addCareerForm.addEventListener('submit', function (e) {
            // Previene el envío si hay errores 
            const nombre = document.getElementById('careerName').value.trim();
            const semestres = document.getElementById('careerSemesters').value;
            if (!nombre || !semestres) {
                e.preventDefault(); // Detiene el envío del formulario
                alert('Por favor complete todos los campos de la carrera');
                return false; // Devuelve falso para detener la acción por defecto
            }
            return true;  // Permite el envío
        });
    }

    // Validación del formulario de añadir materia
    if (addSubjectForm) {
        addSubjectForm.addEventListener('submit', function (e) {
            const carreraSelect = document.getElementById('subjectCareer');
            const nombreInput = document.getElementById('subjectName');
            const semestreInput = document.getElementById('subjectSemester');

            const carrera = carreraSelect.value;
            const nombre = nombreInput.value.trim();
            const semestre = semestreInput.value;

            if (!carrera) {
                e.preventDefault();
                alert('Por favor seleccione una carrera');
                return false;
            }
            if (!nombre) {
                e.preventDefault();
                alert('Por favor ingrese el nombre de la materia');
                return false;
            }
            if (!semestre) {
                e.preventDefault();
                alert('Por favor ingrese el semestre');
                return false;
            }

            // Validar que el semestre esté dentro del rango de la carrera
            const selectedOption = carreraSelect.options[carreraSelect.selectedIndex];
            const maxSemestres = parseInt(selectedOption.getAttribute('data-semestres'));

            if (maxSemestres && parseInt(semestre) > maxSemestres) {
                e.preventDefault();
                alert(`La carrera seleccionada solo tiene ${maxSemestres} semestres.`);
                return false;
            }

            return true;
        });
    }

    // Lógica para eliminar carrera
    const deleteCareerForm = document.getElementById('deleteCareerForm');
    if (deleteCareerForm) {
        deleteCareerForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Evita el envío normal del formulario
            // Obtiene la opción seleccionada en el select
            const select = document.getElementById('deleteCareerSelect');
            const selectedOption = select.options[select.selectedIndex];
            const url = selectedOption.getAttribute('data-url'); // URL de eliminación

            // Pide confirmación al admin
            if (url && confirm('¿Está completamente seguro? Esta acción no se puede deshacer.')) {
                window.location.href = url;  // Redirige a la URL de eliminación
            }
        });
    }

    // Lógica para eliminar materia, la misma funcion en el modal anterior
    const deleteSubjectForm = document.getElementById('deleteSubjectForm');
    if (deleteSubjectForm) {
        deleteSubjectForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const select = document.getElementById('deleteSubjectSelect');
            const selectedOption = select.options[select.selectedIndex];
            const url = selectedOption.getAttribute('data-url');

            if (url && confirm('¿Está seguro de eliminar esta materia?')) {
                window.location.href = url;
            }
        });
    }
});
