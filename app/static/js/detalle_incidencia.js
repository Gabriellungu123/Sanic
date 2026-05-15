const estadosConComentario = ["Pendiente", "Resuelta", "Cerrado", "Cancelado"];

const selectEstado = document.getElementById("estado");
const campoComentarioCambio = document.getElementById("campo-comentario-cambio");
const textareaComentarioCambio = document.getElementById("comentario-cambio");
const avisoComentario = document.getElementById("aviso-comentario");

function actualizarComentarioCambio() {
    if (!selectEstado || !campoComentarioCambio || !textareaComentarioCambio || !avisoComentario) {
        return;
    }

    const estadoSeleccionado = selectEstado.value;
    const necesitaComentario = estadosConComentario.includes(estadoSeleccionado);

    if (necesitaComentario) {
        campoComentarioCambio.style.display = "flex";
        avisoComentario.style.display = "block";
        textareaComentarioCambio.required = true;
    } else {
        campoComentarioCambio.style.display = "none";
        avisoComentario.style.display = "none";
        textareaComentarioCambio.required = false;
        textareaComentarioCambio.value = "";
    }
}

if (selectEstado) {
    selectEstado.addEventListener("change", actualizarComentarioCambio);
    actualizarComentarioCambio();
}

const grupoGestion = document.getElementById("grupo_id");
const semigrupoGestion = document.getElementById("semigrupo_id");
const tecnicoGestion = document.getElementById("tecnico_id");

if (grupoGestion && semigrupoGestion) {
    const opcionesSemigrupoGestion = Array.from(semigrupoGestion.options);

    function filtrarSemigruposGestion() {
        const grupoSeleccionado = grupoGestion.value;

        semigrupoGestion.innerHTML = "";

        const semigruposFiltrados = opcionesSemigrupoGestion.filter(function(opcion) {
            return opcion.dataset.grupo === grupoSeleccionado;
        });

        semigruposFiltrados.forEach(function(opcion) {
            semigrupoGestion.appendChild(opcion.cloneNode(true));
        });

        if (semigrupoGestion.options.length > 0) {
            semigrupoGestion.selectedIndex = 0;
        }
    }

    grupoGestion.addEventListener("change", filtrarSemigruposGestion);
}

if (grupoGestion && tecnicoGestion) {
    const opcionesTecnicoGestion = Array.from(tecnicoGestion.options);

    function filtrarTecnicosGestion() {
        const grupoSeleccionado = grupoGestion.value;

        tecnicoGestion.innerHTML = "";

        opcionesTecnicoGestion.forEach(function(opcion) {
            if (opcion.value === "" || opcion.dataset.grupo === grupoSeleccionado) {
                tecnicoGestion.appendChild(opcion.cloneNode(true));
            }
        });
    }

    grupoGestion.addEventListener("change", filtrarTecnicosGestion);
}