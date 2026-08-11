document.addEventListener('DOMContentLoaded', function() {
    const addRowBtn = document.getElementById('add-item-row-btn');
    if (!addRowBtn) return;

    addRowBtn.addEventListener('click', function() {
        const totalFormsInput = document.getElementById('id_items-TOTAL_FORMS');
        if (!totalFormsInput) return;

        let currentFormCount = parseInt(totalFormsInput.value);

        const templateRow = document.querySelector('#empty-form-template tbody tr').cloneNode(true);

        templateRow.querySelectorAll('input, select').forEach(function(input) {
            input.name = input.name.replace(/__prefix__/g, currentFormCount);
            input.id = input.id.replace(/__prefix__/g, currentFormCount);

            if (input.type === 'checkbox') {
                input.checked = true;
            } else if (input.type === 'number') {
                if (input.name.includes('quantity')) input.value = "1";
                else input.value = "0.01";
            } else {
                input.value = "";
            }
        });

        const removeBtn = templateRow.querySelector('.js-remove-unsaved-row');
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                templateRow.remove();

                let ongoingCount = parseInt(totalFormsInput.value);
                totalFormsInput.value = ongoingCount - 1;
            });
        }

        const tableBody = document.querySelector('table tbody');
        if (tableBody) {
            tableBody.appendChild(templateRow);
        }

        totalFormsInput.value = currentFormCount + 1;
    });
});
