document.addEventListener('DOMContentLoaded', function() {
    const rolField = document.getElementById('id_rol');
    const constructoraField = document.getElementById('id_constructora');
    const constructoraGroup = constructoraField ? constructoraField.closest('.mb-3, .form-group, .col-md-6') : null;
    const regionSelect = document.getElementById('id_region');
    const comunaSelect = document.getElementById('id_comuna');

    function toggleConstructoraField() {
        if (rolField && constructoraGroup) {
            const selectedOption = rolField.options[rolField.selectedIndex];
            const selectedText = selectedOption ? selectedOption.text : '';
            if (selectedText.includes('Constructora') || selectedText.includes('CONSTRUCTORA')) {
                constructoraGroup.style.display = '';
            } else {
                constructoraGroup.style.display = 'none';
                constructoraField.value = '';
            }
        }
    }

    // Función para cargar comunas según región
    function loadComunas(regionId, preserveSelected = false) {
        if (!comunaSelect) return;
        
        const selectedComunaId = preserveSelected ? comunaSelect.value : null;
        
        if (regionId) {
            comunaSelect.innerHTML = '<option value="">Cargando comunas...</option>';
            comunaSelect.disabled = true;
            
            fetch(`/ajax/comunas/?region_id=${regionId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Error al cargar comunas');
                    }
                    return response.json();
                })
                .then(data => {
                    comunaSelect.innerHTML = '<option value="">Seleccionar comuna</option>';
                    if (data.comunas && data.comunas.length > 0) {
                        data.comunas.forEach(function(comuna) {
                            const option = document.createElement('option');
                            option.value = comuna.id;
                            option.textContent = comuna.nombre;
                            if (preserveSelected && selectedComunaId && comuna.id == selectedComunaId) {
                                option.selected = true;
                            }
                            comunaSelect.appendChild(option);
                        });
                    }
                    comunaSelect.disabled = false;
                })
                .catch(function(error) {
                    console.error('Error al cargar comunas:', error);
                    comunaSelect.innerHTML = '<option value="">Error al cargar comunas</option>';
                    comunaSelect.disabled = false;
                });
        } else {
            comunaSelect.innerHTML = '<option value="">Seleccionar comuna</option>';
            comunaSelect.disabled = false;
        }
    }

    // Cargar comunas al inicio si hay una región seleccionada
    if (regionSelect && comunaSelect && regionSelect.value) {
        loadComunas(regionSelect.value, true);
    }

    // Cargar comunas cuando cambia la región
    if (regionSelect) {
        regionSelect.addEventListener('change', function() {
            loadComunas(this.value, false);
        });
    }

    toggleConstructoraField();
    if (rolField) {
        rolField.addEventListener('change', toggleConstructoraField);
    }
});