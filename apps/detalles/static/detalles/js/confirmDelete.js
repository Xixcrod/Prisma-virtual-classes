// Función para mostrar mensaje y buscar la confirmación del usuario para eliminar el elemento (tema o vídeo) de la BD.
function abrirModalEliminar(url, titulo) {
  const modal = document.getElementById('modalConfirm');
  const spanTitulo = document.getElementById('modalTitulo');
  const form = document.getElementById('EliminarForm');
  spanTitulo.textContent = titulo;
  if (!modal || !form || !spanTitulo) {
    console.error('No se encontraron elementos del modal');
    return;
  }
  form.action = url;
  modal.showModal();
}
