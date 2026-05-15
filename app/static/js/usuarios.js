const rolSelect = document.getElementById("rol");
const grupoSelectUsuario = document.getElementById("grupo_id");
const semigrupoSelectUsuario = document.getElementById("semigrupo_id");
const campoGrupo = document.querySelector(".campo-grupo");
const campoSemigrupo = document.querySelector(".campo-semigrupo");

function actualizarFormularioCrearUsuario() {
    if (!rolSelect) return;

    const rol = rolSelect.value;

    if (rol === "cliente") {
        if (campoGrupo) campoGrupo.style.display = "none";
        if (campoSemigrupo) campoSemigrupo.style.display = "none";

        if (grupoSelectUsuario) grupoSelectUsuario.required = false;
        if (semigrupoSelectUsuario) semigrupoSelectUsuario.required = false;
    } else {
        if (campoGrupo) campoGrupo.style.display = "flex";
        if (campoSemigrupo) campoSemigrupo.style.display = "flex";

        if (grupoSelectUsuario) grupoSelectUsuario.required = true;
        if (semigrupoSelectUsuario) semigrupoSelectUsuario.required = true;
    }
}

function filtrarSemigruposFormularioPrincipal() {
    if (!grupoSelectUsuario || !semigrupoSelectUsuario) return;

    const grupoSeleccionado = grupoSelectUsuario.value;
    const opciones = Array.from(semigrupoSelectUsuario.options);

    opciones.forEach(function(opcion) {
        if (!opcion.value) {
            opcion.hidden = false;
            return;
        }

        opcion.hidden = opcion.dataset.grupo !== grupoSeleccionado;
    });

    if (
        semigrupoSelectUsuario.selectedOptions.length &&
        semigrupoSelectUsuario.selectedOptions[0].hidden
    ) {
        semigrupoSelectUsuario.value = "";
    }
}

if (rolSelect) {
    rolSelect.addEventListener("change", actualizarFormularioCrearUsuario);
    actualizarFormularioCrearUsuario();
}

if (grupoSelectUsuario) {
    grupoSelectUsuario.addEventListener("change", filtrarSemigruposFormularioPrincipal);
    filtrarSemigruposFormularioPrincipal();
}

document.querySelectorAll(".form-asignacion-usuario").forEach(function(formulario) {
    const grupo = formulario.querySelector(".grupo-asignacion");
    const semigrupo = formulario.querySelector(".semigrupo-asignacion");

    if (!grupo || !semigrupo) return;

    function filtrar() {
        const grupoSeleccionado = grupo.value;
        const opciones = Array.from(semigrupo.options);

        opciones.forEach(function(opcion) {
            opcion.hidden = opcion.dataset.grupo !== grupoSeleccionado;
        });

        if (
            semigrupo.selectedOptions.length &&
            semigrupo.selectedOptions[0].hidden
        ) {
            const primeraVisible = opciones.find(function(opcion) {
                return !opcion.hidden;
            });

            if (primeraVisible) {
                semigrupo.value = primeraVisible.value;
            }
        }
    }

    grupo.addEventListener("change", filtrar);
    filtrar();
});