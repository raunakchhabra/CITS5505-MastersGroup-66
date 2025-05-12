// my_data.js

document.addEventListener('DOMContentLoaded', function() {
    // Function to set data type colors
    function setDataTypeColors() {
        const badges = document.querySelectorAll('.data-type-badge');
        badges.forEach(badge => {
            const dataType = badge.textContent.trim().toLowerCase();
            let colorClass = 'secondary';

            switch(dataType) {
                case 'vocabulary':
                    colorClass = 'primary';
                    break;
                case 'study_time':
                    colorClass = 'success';
                    break;
                case 'assessment':
                    colorClass = 'warning';
                    break;
                case 'other':
                    colorClass = 'info';
                    break;
            }

            // Remove any existing bg- classes
            badge.className = badge.className.replace(/bg-\w+/g, '');
            badge.classList.add(`bg-${colorClass}`);
        });
    }

    // Initialize data type colors
    setDataTypeColors();

    // Tab change handler (if needed for future functionality)
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(event) {
            // Can add tab-specific functionality here
            console.log('Switched to tab:', event.target.getAttribute('aria-controls'));
        });
    });
});