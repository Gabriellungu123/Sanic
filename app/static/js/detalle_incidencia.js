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
        const valorActual = semigrupoGestion.value;

        semigrupoGestion.innerHTML = "";

        const opcionVaciaOriginal = opcionesSemigrupoGestion.find(function(opcion) {
            return opcion.value === "";
        });

        if (opcionVaciaOriginal) {
            semigrupoGestion.appendChild(opcionVaciaOriginal.cloneNode(true));
        }

        opcionesSemigrupoGestion.forEach(function(opcion) {
            if (opcion.value !== "" && opcion.dataset.grupo === grupoSeleccionado) {
                semigrupoGestion.appendChild(opcion.cloneNode(true));
            }
        });

        const existeValorActual = Array.from(semigrupoGestion.options).some(function(opcion) {
            return opcion.value === valorActual;
        });

        if (existeValorActual) {
            semigrupoGestion.value = valorActual;
        } else {
            semigrupoGestion.value = "";
        }
    }

    grupoGestion.addEventListener("change", filtrarSemigruposGestion);
    filtrarSemigruposGestion();
}

if (grupoGestion && tecnicoGestion) {
    const opcionesTecnicoGestion = Array.from(tecnicoGestion.options);

    function filtrarTecnicosGestion() {
        const grupoSeleccionado = grupoGestion.value;
        const valorActual = tecnicoGestion.value;

        tecnicoGestion.innerHTML = "";

        opcionesTecnicoGestion.forEach(function(opcion) {
            if (opcion.value === "" || opcion.dataset.grupo === grupoSeleccionado) {
                tecnicoGestion.appendChild(opcion.cloneNode(true));
            }
        });

        const existeValorActual = Array.from(tecnicoGestion.options).some(function(opcion) {
            return opcion.value === valorActual;
        });

        if (existeValorActual) {
            tecnicoGestion.value = valorActual;
        } else {
            tecnicoGestion.value = "";
        }
    }

    grupoGestion.addEventListener("change", filtrarTecnicosGestion);
    filtrarTecnicosGestion();
}