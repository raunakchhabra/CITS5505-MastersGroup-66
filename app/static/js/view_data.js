// view_data.js

document.addEventListener('DOMContentLoaded', function() {
    // Function to set data type color
    function setDataTypeColor() {
        const badge = document.querySelector('.data-type-badge');
        if (badge) {
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
        }
    }

    // Initialize data type color
    setDataTypeColor();

    // Handle JSON content formatting
    function formatJsonContent() {
        const jsonElements = document.querySelectorAll('.json-content');
        jsonElements.forEach(element => {
            try {
                const text = element.textContent;
                const json = JSON.parse(text);
                element.textContent = JSON.stringify(json, null, 2);
            } catch (e) {
                // If it's not valid JSON, leave it as is
                console.log('Content is not JSON, displaying as plain text');
            }
        });
    }

    formatJsonContent();

    // Modal event handlers
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(event) {
            // Can add pre-delete confirmation logic here
            console.log('Delete modal opened');
        });
    }

    const shareModal = document.getElementById('shareModal');
    if (shareModal) {
        shareModal.addEventListener('show.bs.modal', function(event) {
            // Prepare share functionality
            console.log('Share modal opened');
        });
    }

    const editModal = document.getElementById('editModal');
    if (editModal) {
        editModal.addEventListener('show.bs.modal', function(event) {
            // Prepare edit functionality
            console.log('Edit modal opened');
        });
    }
});