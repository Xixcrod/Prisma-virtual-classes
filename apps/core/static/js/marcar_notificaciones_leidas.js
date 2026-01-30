document.addEventListener('DOMContentLoaded', function() {
    const notifDropdown = document.getElementById('notifDropdown');
    const badge = document.getElementById('notif-badge');

    if (notifDropdown) {
        notifDropdown.addEventListener('shown.bs.dropdown', function () {
            // 1. Ocultar el badge visualmente de inmediato para mejorar la experiencia
            if (badge) {
                badge.style.display = 'none';
            }

            // 2. Enviar petición al servidor para marcar como leídas en la BD
            fetch('{% url "marcar_leidas" %}', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status !== 'ok') {
                    console.error('Error al marcar notificaciones');
                }
            });
        });
    }
});