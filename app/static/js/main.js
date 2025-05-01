// Main JavaScript file for general use across the application

// Add confirmation for dangerous actions
document.addEventListener('DOMContentLoaded', function() {
   // Find all elements with confirmation prompts
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
   
   // Handle flash messages auto-dismiss
   const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
   flashMessages.forEach(flash => {
       setTimeout(() => {
           flash.classList.add('fade');
           setTimeout(() => {
               flash.remove();
           }, 500);
       }, 5000);
   });
   
   // Initialize any tooltips
   const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
   tooltipTriggerList.map(function(tooltipTriggerEl) {
       return new bootstrap.Tooltip(tooltipTriggerEl);
   });
});

// Function to format dates
function formatDate(dateString) {
   const date = new Date(dateString);
   return date.toLocaleDateString();
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

// Call function on page load
document.addEventListener('DOMContentLoaded', handleFileInputs);
