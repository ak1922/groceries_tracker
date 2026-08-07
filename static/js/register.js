document.addEventListener("DOMContentLoaded", function() {
    const roleField = document.querySelector("select[name='role']");
    const familyWrapper = document.getElementById("div_id_new_family_name");

    function toggleFamilyInput() {
        if (roleField && familyWrapper) {
            // If they choose Head of Family (HEAD), show the input box; otherwise, hide it
            familyWrapper.style.display = (roleField.value === 'HEAD') ? 'block' : 'none';
        }
    }

    if (roleField) {
        roleField.addEventListener('change', toggleFamilyInput);
        toggleFamilyInput(); // Execute immediately on form load initialization
    }
});
