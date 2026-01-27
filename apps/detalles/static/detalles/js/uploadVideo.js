// Función que recoge el Id para seleccionar un elemento y devolverlo
const $ = (id) => document.getElementById(id);
// Selección del input de vídeo para cambiarle su texto de contenido (label)
$('id_create_video_form-url_video').onchange = (e) => {
  const file = e.target.files[0];
  $('video-label').textContent = file
    ? `${file.name}`
    : 'Cliquea para seleccionar un vídeo';
};
// Selección del formulario una vez se le haga submit para mostrar el overlay
$('uploadVideoForm').onsubmit = function (e) {
  // Validaciones por si le falta algún dato por recibir
  if (
    !$('id_create_video_form-url_video').files.length ||
    !$('id_create_video_form-titulo').value.trim() ||
    !$('id_create_video_form-resumen').value.trim()
  )
    return true;
  // Mostrar el overlay y cambiar el texto del botón.
  const overlay = $('uploadOverlay');
  overlay.style.display = 'flex';
  overlay.classList.add('active');
  const btn_upload = $('btn-upload-video');
  btn_upload.textContent = 'Enviando...';
  setTimeout(() => {
    btn_upload.disabled = true;
  }, 100);
  return true;
};
