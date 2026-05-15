const grupoSelect = document.getElementById("grupo_id");
const semigrupoSelect = document.getElementById("semigrupo_id");

if (grupoSelect && semigrupoSelect) {
    const opcionesSemigrupo = Array.from(semigrupoSelect.options);

    function filtrarSemigrupos() {
        const grupoSeleccionado = grupoSelect.value;

        semigrupoSelect.innerHTML = "";

        const semigruposFiltrados = opcionesSemigrupo.filter(function(opcion) {
            return opcion.dataset.grupo === grupoSeleccionado;
        });

        semigruposFiltrados.forEach(function(opcion) {
            semigrupoSelect.appendChild(opcion.cloneNode(true));
        });

        if (semigrupoSelect.options.length > 0) {
            semigrupoSelect.selectedIndex = 0;
        }
    }

    grupoSelect.addEventListener("change", filtrarSemigrupos);

    filtrarSemigrupos();
}