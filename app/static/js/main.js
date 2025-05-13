// Main JavaScript file for general use across the application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize navbar functionality
    initializeNavbar();

    // Initialize other functionality
    initializeConfirmButtons();
    initializeFlashMessages();
    initializeTooltips();
    handleFileInputs();
});

function initializeNavbar() {
    // Get all navbar elements
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const navLeft = document.querySelector('.nav-left');
    const dataMenu = document.querySelector('.data-menu');
    const userProfile = document.querySelector('.user-profile');

    // Hamburger menu toggle
    if (hamburgerMenu && navLeft) {
        hamburgerMenu.addEventListener('click', function(e) {
            e.stopPropagation();
            navLeft.classList.toggle('open');
        });
    }

    // Data dropdown toggle
    if (dataMenu) {
        const dataDropdown = dataMenu.querySelector('.data-dropdown');
        if (dataDropdown) {
            dataMenu.addEventListener('click', function(e) {
                e.stopPropagation();

                // Close other dropdowns
                const allDropdowns = document.querySelectorAll('.dropdown-menu.open');
                allDropdowns.forEach(dropdown => {
                    if (dropdown !== dataDropdown) {
                        dropdown.classList.remove('open');
                    }
                });

                // Toggle this dropdown
                dataDropdown.classList.toggle('open');
            });
        }
    }

    // User profile dropdown toggle
    if (userProfile) {
        const rightDropdown = userProfile.querySelector('.right-dropdown');
        if (rightDropdown) {
            userProfile.addEventListener('click', function(e) {
                e.stopPropagation();

                // Close other dropdowns
                const allDropdowns = document.querySelectorAll('.dropdown-menu.open');
                allDropdowns.forEach(dropdown => {
                    if (dropdown !== rightDropdown) {
                        dropdown.classList.remove('open');
                    }
                });

                // Toggle this dropdown
                rightDropdown.classList.toggle('open');
            });
        }
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        // Close all dropdowns if clicking outside
        if (!e.target.closest('.nav-left') && !e.target.closest('.data-menu') && !e.target.closest('.user-profile')) {
            const allDropdowns = document.querySelectorAll('.dropdown-menu.open');
            allDropdowns.forEach(dropdown => {
                dropdown.classList.remove('open');
            });

            if (navLeft) {
                navLeft.classList.remove('open');
            }
        }
    });

    // Prevent dropdown links from closing the dropdown
    const dropdownLinks = document.querySelectorAll('.dropdown-menu a');
    dropdownLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
}

function initializeConfirmButtons() {
    const confirmBtns = document.querySelectorAll('[data-confirm]');
    confirmBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.classList.add('fade');
            setTimeout(() => {
                flash.remove();
            }, 500);
        }, 5000);
    });
}

function initializeTooltips() {
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Function to handle file input styling
function handleFileInputs() {
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'No file chosen';
            const fileNameDisplay = this.nextElementSibling;

            if (fileNameDisplay && fileNameDisplay.classList.contains('custom-file-label')) {
                fileNameDisplay.textContent = fileName;
            }
        });
    });
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Export functions for use in other files if needed
window.formatDate = formatDate;