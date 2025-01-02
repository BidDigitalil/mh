document.addEventListener('DOMContentLoaded', function() {
    const parentsTypeSelect = document.querySelector('[name="parents_type"]');
    const fatherFields = document.getElementById('father-fields');
    const motherFields = document.getElementById('mother-fields');

    function updateParentFields() {
        const selectedValue = parentsTypeSelect.value;
        
        if (selectedValue === 'both') {
            fatherFields.style.display = 'block';
            motherFields.style.display = 'block';
        } else if (selectedValue === 'father') {
            fatherFields.style.display = 'block';
            motherFields.style.display = 'none';
            // Clear mother fields
            document.querySelectorAll('#mother-fields input').forEach(input => input.value = '');
        } else if (selectedValue === 'mother') {
            fatherFields.style.display = 'none';
            motherFields.style.display = 'block';
            // Clear father fields
            document.querySelectorAll('#father-fields input').forEach(input => input.value = '');
        }
    }

    // Initial update
    if (parentsTypeSelect) {
        updateParentFields();
        parentsTypeSelect.addEventListener('change', updateParentFields);
    }

    // הגדרת התנהגות טופס המשפחה
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // בדיקת תקינות הטופס
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('נא למלא את כל השדות החובה');
            }
        });
        
        // הוספת מאזינים לשדות הקובץ
        const fileInputs = form.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    // בדיקת גודל הקובץ (מקסימום 5MB)
                    const maxSize = 5 * 1024 * 1024; // 5MB
                    if (file.size > maxSize) {
                        alert('הקובץ גדול מדי. גודל מקסימלי הוא 5MB');
                        this.value = '';
                        return;
                    }
                    
                    // בדיקת סוג הקובץ
                    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
                    if (!allowedTypes.includes(file.type)) {
                        alert('סוג הקובץ לא נתמך. יש להעלות קובץ PDF או Word בלבד');
                        this.value = '';
                        return;
                    }
                }
            });
        });
    }
});
