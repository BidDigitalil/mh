document.addEventListener('DOMContentLoaded', function() {
    const familyStatusSelect = document.getElementById('id_family_status');
    const parentSection = document.querySelector('.form-row[data-section="parent-details"]');
    const parentConsentSection = document.querySelector('.form-row[data-section="parent-consent"]');

    function updateParentFields() {
        const selectedStatus = familyStatusSelect.value;
        const parentNameLabel = document.querySelector('label[for="id_primary_parent_name"]');
        const parentPhoneLabel = document.querySelector('label[for="id_primary_parent_phone"]');
        const parentEmailLabel = document.querySelector('label[for="id_primary_parent_email"]');

        // Reset labels
        parentNameLabel.textContent = 'שם ההורה';
        parentPhoneLabel.textContent = 'טלפון ההורה';
        parentEmailLabel.textContent = 'דוא"ל ההורה';

        // Update labels and visibility based on family status
        switch(selectedStatus) {
            case 'divorced':
                parentNameLabel.textContent = 'שם ההורה המשמורן';
                parentPhoneLabel.textContent = 'טלפון ההורה המשמורן';
                parentEmailLabel.textContent = 'דוא"ל ההורה המשמורן';
                parentSection.style.display = 'block';
                parentConsentSection.style.display = 'block';
                break;
            case 'single_parent':
                parentNameLabel.textContent = 'שם ההורה היחידני';
                parentPhoneLabel.textContent = 'טלפון ההורה היחידני';
                parentEmailLabel.textContent = 'דוא"ל ההורה היחידני';
                parentSection.style.display = 'block';
                parentConsentSection.style.display = 'none';
                break;
            case 'widowed':
                parentNameLabel.textContent = 'שם ההורה השכול';
                parentPhoneLabel.textContent = 'טלפון ההורה השכול';
                parentEmailLabel.textContent = 'דוא"ל ההורה השכול';
                parentSection.style.display = 'block';
                parentConsentSection.style.display = 'none';
                break;
            case 'intact':
            case 'other':
            default:
                parentSection.style.display = 'none';
                parentConsentSection.style.display = 'none';
                break;
        }
    }

    // Initial setup
    if (familyStatusSelect) {
        familyStatusSelect.addEventListener('change', updateParentFields);
        updateParentFields(); // Set initial state
    }

    // Form validation
    const familyForm = document.querySelector('form');
    if (familyForm) {
        familyForm.addEventListener('submit', function(event) {
            const selectedStatus = familyStatusSelect.value;
            const primaryParentName = document.getElementById('id_primary_parent_name');
            const primaryParentPhone = document.getElementById('id_primary_parent_phone');
            const primaryParentConsentForm = document.getElementById('id_primary_parent_consent_form');

            // Validate for specific statuses
            if (['divorced', 'single_parent', 'widowed'].includes(selectedStatus)) {
                if (!primaryParentName.value.trim()) {
                    event.preventDefault();
                    alert('אנא הזן שם הורה');
                    primaryParentName.focus();
                    return;
                }

                if (!primaryParentPhone.value.trim()) {
                    event.preventDefault();
                    alert('אנא הזן טלפון הורה');
                    primaryParentPhone.focus();
                    return;
                }

                // Additional validation for divorced families
                if (selectedStatus === 'divorced' && !primaryParentConsentForm.files.length) {
                    event.preventDefault();
                    alert('אנא העלה טופס הסכמה עבור משפחות גרושות');
                    primaryParentConsentForm.focus();
                    return;
                }
            }
        });
    }
});
