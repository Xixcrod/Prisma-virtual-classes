document.addEventListener('DOMContentLoaded', function() {
    const notifDropdown = document.getElementById('notifDropdown');
    const badge = document.getElementById('notif-badge');

    if (notifDropdown) {
        notifDropdown.addEventListener('shown.bs.dropdown', function () {
            // Leemos los datos que Django inyectó en el HTML
            const urlLeidas = notifDropdown.getAttribute('data-url');
            const token = notifDropdown.getAttribute('data-csrf');

            // 1. Ocultar el badge visualmente
            if (badge) {
                badge.style.display = 'none';
            }

            // 2. Enviar la petición POST
            fetch(urlLeidas, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': token, // Ahora 'token' tiene el valor real
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                console.log("Notificaciones actualizadas con éxito");
            })
            .catch(error => {
                console.error('Hubo un problema:', error);
                // Si falla, podrías volver a mostrar el badge:
                // if (badge) badge.style.display = 'block';
            });
        });
    }
});