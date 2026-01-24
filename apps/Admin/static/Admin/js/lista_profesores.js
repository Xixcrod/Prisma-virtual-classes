// Variables globales para el modal
const modal = document.getElementById('assignModal');
const modalTitle = document.getElementById('modalProfessorName');
const form = document.getElementById('assignForm');
const carreraSelect = document.getElementById('modalCarrera');
const semestreSelect = document.getElementById('modalSemestre');
const materiasContainer = document.getElementById('modalMateriasContainer');

// Cargar datos de asignaciones desde el servidor
let asignacionesGlobal = {};
const asignacionesDataElement = document.getElementById('asignaciones-data');
if (asignacionesDataElement) {
    asignacionesGlobal = JSON.parse(asignacionesDataElement.textContent);
}

let currentProfesorId = null;

// Función para abrir el modal
function openAssignModal(profesorId, profesorNombre) {
    modal.style.display = 'flex';
    modalTitle.textContent = profesorNombre.toUpperCase();
    currentProfesorId = profesorId;

    // Configurar la URL de acción del formulario
    const dummyUuid = "00000000-0000-0000-0000-000000000000";
    // La plantilla se obtiene del atributo data-url-template del formulario
    const urlTemplate = form.dataset.urlTemplate;
    const urlBase = urlTemplate.replace(dummyUuid, profesorId);
    form.action = urlBase;

    // Se reinician los campos de entrada
    carreraSelect.value = "";
    semestreSelect.innerHTML = '<option value="" disabled selected>Semestre</option>';
    semestreSelect.disabled = true;
    materiasContainer.innerHTML = '<p class="text-white-50 text-center" style="font-size:0.8rem; padding:10px;">Seleccione carrera y semestre</p>';
    materiasContainer.classList.remove('show');
}

function closeAssignModal(event) {
    if (event) event.preventDefault();
    modal.style.display = 'none';
    currentProfesorId = null;
}

// Lógica de Carreras/Semestres
function cargarSemestresModal() {
    const carreraId = carreraSelect.value;
    if (carreraId) {
        semestreSelect.disabled = false;
        semestreSelect.innerHTML = '<option value="" disabled selected>Semestre</option>';
        for (let i = 1; i <= 10; i++) {
            semestreSelect.innerHTML += `<option value="${i}">Semestre ${i}</option>`;
        }
    }
}

function toggleMateriasDropdown() {
    materiasContainer.classList.toggle('show');
}

function cargarMateriasModal() {
    const carreraId = carreraSelect.value;
    const semestre = semestreSelect.value;

    if (!carreraId || !semestre) return;

    materiasContainer.innerHTML = '<p class="text-center text-white" style="padding:10px;">Cargando...</p>';
    materiasContainer.classList.add('show');

    // Obtener asignaciones actuales del profesor
    const misMaterias = asignacionesGlobal[currentProfesorId] || [];

    fetch(`/adminuser/obtener-materias/${carreraId}/${semestre}/`)
        .then(response => response.json())
        .then(data => {
            materiasContainer.innerHTML = '';
            if (data.length === 0) {
                materiasContainer.innerHTML = '<p class="text-center text-white" style="padding:10px;">No hay materias.</p>';
            } else {
                data.forEach(m => {
                    const isChecked = misMaterias.includes(m.id);
                    const div = document.createElement('div');
                    div.className = 'materia-option';
                    div.innerHTML = `
                        <input type="checkbox" name="materias_ids" value="${m.id}" id="mod-m-${m.id}" ${isChecked ? 'checked' : ''}>
                        <label for="mod-m-${m.id}" style="width:100%; cursor:pointer;">${m.nombre}</label>
                    `;

                    // Asegurar que el clic funcione correctamente y cerrar al seleccionar
                    div.addEventListener('click', function (e) {
                        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'LABEL') {
                            const cb = this.querySelector('input');
                            cb.checked = !cb.checked;
                        }
                        // Cerrar el dropdown después de un breve retraso para que se vea el check
                        setTimeout(() => {
                            materiasContainer.classList.remove('show');
                        }, 150);
                    });
                    materiasContainer.appendChild(div);
                });
            }
        })
        .catch(error => {
            console.error(error);
            materiasContainer.innerHTML = '<p class="text-center text-danger">Error al cargar.</p>';
        });
}

// Cerrar modal con ESC
document.addEventListener('keydown', function (event) {
    if (event.key === "Escape") {
        closeAssignModal();
    }
});
