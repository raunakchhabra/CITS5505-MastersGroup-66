// upload_data.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initializeDropZone();
    initializeRangeInput();
    initializeFormValidation();
    initializeAutoSave();
    initializeKeyboardShortcuts();
    initializeSidebarNavigation();
    restoreFormData();
});

// Drop zone functionality
function initializeDropZone() {
    const dropZone = document.getElementById('dropZone');
    if (!dropZone) return;

    const fileInput = dropZone.querySelector('input[type="file"]');
    const submitButton = dropZone.closest('form').querySelector('button[type="submit"]');
    const fileInfo = document.getElementById('fileInfo');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    // Handle file input change
    fileInput.addEventListener('change', handleFileChange);

    // Click on drop zone to select files
    dropZone.addEventListener('click', function(e) {
        if (e.target === fileInput || e.target.tagName === 'LABEL') return;
        fileInput.click();
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        handleFileChange();
    }

    function handleFileChange() {
        const files = fileInput.files;
        if (files.length > 0) {
            const file = files[0];
            displayFileInfo(file);
            submitButton.disabled = false;
        } else {
            clearFileInfo();
            submitButton.disabled = true;
        }
    }

    function displayFileInfo(file) {
        fileInfo.innerHTML = `
            <div class="file-info-display">
                <i class="fas fa-file me-2"></i>
                <strong>${file.name}</strong>
                <span class="text-muted ms-2">(${formatFileSize(file.size)})</span>
            </div>
        `;
    }

    function clearFileInfo() {
        fileInfo.innerHTML = '';
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Range input functionality
function initializeRangeInput() {
    const rangeInputs = document.querySelectorAll('input[type="range"]');

    rangeInputs.forEach(rangeInput => {
        // Create value display
        const valueDisplay = document.createElement('span');
        valueDisplay.className = 'range-value-display ms-2';
        valueDisplay.textContent = rangeInput.value;
        rangeInput.parentNode.appendChild(valueDisplay);

        rangeInput.addEventListener('input', function() {
            updateRangeDisplay(this, valueDisplay);
        });

        // Initial update
        updateRangeDisplay(rangeInput, valueDisplay);
    });

    function updateRangeDisplay(input, display) {
        const value = input.value;
        const min = parseFloat(input.min) || 0;
        const max = parseFloat(input.max) || 100;
        const percentage = ((value - min) / (max - min)) * 100;

        // Update background gradient
        input.style.background = `linear-gradient(to right, #0d6efd 0%, #0d6efd ${percentage}%, #dee2e6 ${percentage}%, #dee2e6 100%)`;

        // Update value display
        display.textContent = value;
    }
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(this);
            });
        });
    });

    // Skills checkbox validation
    const skillCheckboxes = document.querySelectorAll('.form-check-input[type="checkbox"][name*="skill"]');
    if (skillCheckboxes.length > 0) {
        skillCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', validateSkillSelection);
        });
    }
}

function validateInput(input) {
    const isValid = input.checkValidity();

    if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
    }
}

function validateSkillSelection() {
    const checkboxes = document.querySelectorAll('.form-check-input[type="checkbox"][name*="skill"]');
    const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
    const errorContainer = document.getElementById('skills-error') || createSkillsError();

    if (checkedCount === 0) {
        errorContainer.style.display = 'block';
        checkboxes.forEach(cb => cb.classList.add('is-invalid'));
    } else {
        errorContainer.style.display = 'none';
        checkboxes.forEach(cb => cb.classList.remove('is-invalid'));
    }
}

function createSkillsError() {
    const skillsContainer = document.querySelector('.skills-container') ||
                          document.querySelector('[class*="skill"]').closest('.mb-3');
    const errorDiv = document.createElement('div');
    errorDiv.id = 'skills-error';
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = 'Please select at least one skill';
    errorDiv.style.display = 'none';
    skillsContainer.appendChild(errorDiv);
    return errorDiv;
}

// Auto-save functionality
function initializeAutoSave() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const formInputs = form.querySelectorAll('input, textarea, select');
        let autoSaveTimer;

        formInputs.forEach(input => {
            // Skip file inputs and submit buttons
            if (input.type === 'file' || input.type === 'submit') return;

            input.addEventListener('input', function() {
                clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(() => {
                    saveFormData(form);
                }, 2000); // Auto-save after 2 seconds of inactivity
            });
        });
    });
}

function saveFormData(form) {
    const formData = {};
    const formId = form.id || `form-${window.location.pathname}`;

    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        if (input.name && input.type !== 'file' && input.type !== 'submit') {
            if (input.type === 'checkbox' || input.type === 'radio') {
                formData[input.name] = input.checked;
            } else {
                formData[input.name] = input.value;
            }
        }
    });

    localStorage.setItem(formId, JSON.stringify(formData));
    showNotification('Draft saved', 'success');
}

function restoreFormData() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const formId = form.id || `form-${window.location.pathname}`;
        const savedData = localStorage.getItem(formId);

        if (savedData) {
            try {
                const formData = JSON.parse(savedData);

                Object.entries(formData).forEach(([name, value]) => {
                    const input = form.elements[name];
                    if (input) {
                        if (input.type === 'checkbox' || input.type === 'radio') {
                            input.checked = value;
                        } else {
                            input.value = value;
                        }
                        // Trigger change event to update any dependent UI
                        input.dispatchEvent(new Event('change'));
                    }
                });

                showNotification('Draft restored', 'info');
            } catch (e) {
                console.error('Error restoring form data:', e);
            }
        }
    });
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification alert alert-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        min-width: 250px;
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to save draft
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const activeForm = document.querySelector('form:not([style*="display: none"])');
            if (activeForm) {
                saveFormData(activeForm);
            }
        }

        // Ctrl+D to clear form
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            if (confirm('Clear all form data?')) {
                clearFormData();
            }
        }
    });
}

function clearFormData() {
    const activeForm = document.querySelector('form:not([style*="display: none"])');
    if (activeForm) {
        activeForm.reset();
        const formId = activeForm.id || `form-${window.location.pathname}`;
        localStorage.removeItem(formId);
        showNotification('Form cleared', 'warning');
    }
}

// Sidebar navigation enhancement
function initializeSidebarNavigation() {
    const sidebarLinks = document.querySelectorAll('.nav-link-sidebar');

    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
            }

            // Update active state
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            // Store active state
            localStorage.setItem('activeUploadType', this.getAttribute('href'));
        });
    });

    // Restore active state
    const activeType = localStorage.getItem('activeUploadType');
    if (activeType) {
        const activeLink = document.querySelector(`.nav-link-sidebar[href="${activeType}"]`);
        if (activeLink) {
            sidebarLinks.forEach(l => l.classList.remove('active'));
            activeLink.classList.add('active');
        }
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .file-info-display {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-radius: 0.25rem;
    }
    
    .range-value-display {
        font-weight: bold;
        color: #0d6efd;
    }
`;
document.head.appendChild(style);

// Clean up on form submission
document.addEventListener('submit', function(e) {
    if (e.target.tagName === 'FORM') {
        const formId = e.target.id || `form-${window.location.pathname}`;
        localStorage.removeItem(formId);
    }
});

