// 1. Función para llenar los semestres
function cargarSemestres() {
    const carreraSelect = document.getElementById('carrera-select');
    const semestreSelect = document.getElementById('semestre-select');
    const carreraId = carreraSelect.value;
    if (carreraId) {
        semestreSelect.disabled = false;
        semestreSelect.innerHTML = '<option value="" disabled selected>Semestre</option>';
        for (let i = 1; i <= 10; i++) {
            semestreSelect.innerHTML += `<option value="${i}">Semestre ${i}</option>`;
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const carreraSelect = document.getElementById('carrera-select');
    const semestreSelect = document.getElementById('semestre-select');
    const materiasContainer = document.getElementById('materias-container');

    let materiasActuales = [];
    const materiasDataElement = document.getElementById('materias-data');
    if (materiasDataElement) {
        materiasActuales = JSON.parse(materiasDataElement.textContent);
    }

    // Evento manual cuando el usuario cambia la carrera
    if (carreraSelect) {
        carreraSelect.addEventListener('change', cargarSemestres);

        // Ejecutar automáticamente al cargar la página si ya hay una carrera elegida
        if (carreraSelect.value) {
            cargarSemestres();
        }
    }

    // 4. Lógica para buscar materias vía AJAX al elegir semestre
    if (semestreSelect) {
        semestreSelect.addEventListener('change', function () {
            const carreraId = carreraSelect.value;
            const semestre = this.value;

            materiasContainer.innerHTML = '<p class="text-center">Buscando materias...</p>';

            fetch(`/adminuser/obtener-materias/${carreraId}/${semestre}/`)
                .then(response => response.json())
                .then(data => {
                    materiasContainer.innerHTML = '';
                    if (data.length === 0) {
                        materiasContainer.innerHTML = '<p class="text-center">No hay materias en este semestre.</p>';
                    } else {
                        data.forEach(m => {
                            const isChecked = materiasActuales.includes(m.id);
                            const selectedClass = isChecked ? 'selected' : '';

                            const item = document.createElement('div');
                            item.className = `materia-item ${selectedClass}`;
                            item.innerHTML = `
                                <input type="checkbox" name="materias_ids" value="${m.id}" id="m-${m.id}" ${isChecked ? 'checked' : ''}>
                                <label for="m-${m.id}">${m.nombre}</label>
                            `;

                            // Alternar selección al hacer clic en el ítem
                            item.addEventListener('click', function (e) {
                                const checkbox = this.querySelector('input');
                                if (e.target !== checkbox) {
                                    checkbox.checked = !checkbox.checked;
                                }
                                this.classList.toggle('selected', checkbox.checked);
                            });

                            materiasContainer.appendChild(item);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    materiasContainer.innerHTML = '<p class="text-center text-danger">Error de conexión.</p>';
                });
        });
    }
});
