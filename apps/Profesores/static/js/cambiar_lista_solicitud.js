document.addEventListener('DOMContentLoaded', () => {
    const btnPendientes = document.getElementById('tab-pendientes');
    const btnAceptados = document.getElementById('tab-aceptados');
    const filasPendientes = document.querySelectorAll('.row-pendiente');
    const filasAceptados = document.querySelectorAll('.row-aceptado');

    if (btnPendientes && btnAceptados) {
        btnPendientes.addEventListener('click', () => {
            // Switch de botones
            btnPendientes.classList.add('active');
            btnAceptados.classList.remove('active');
            // Mostrar/Ocultar filas
            filasPendientes.forEach(f => f.style.display = '');
            filasAceptados.forEach(f => f.style.display = 'none');
        });

        btnAceptados.addEventListener('click', () => {
            // Switch de botones
            btnAceptados.classList.add('active');
            btnPendientes.classList.remove('active');
            // Mostrar/Ocultar filas
            filasAceptados.forEach(f => f.style.display = '');
            filasPendientes.forEach(f => f.style.display = 'none');
        });
    }
});