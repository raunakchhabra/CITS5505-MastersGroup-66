// for share_data.html

// nav part event listeners
document.addEventListener('DOMContentLoaded', () => {

    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const leftDropdown = document.querySelector('.left-dropdown');
    const userProfile = document.querySelector('.user-profile');
    const rightDropdown = document.querySelector('.right-dropdown');
    const dataMenu = document.querySelector('.data-menu'); // Get the new data menu container
    const dataDropdown = document.querySelector('.data-dropdown'); // Get the new data dropdown
    const navLeft = document.querySelector('.nav-left');

    // Event listeners for navigation dropdowns
    if (hamburgerMenu && navLeft && leftDropdown) {
        hamburgerMenu.addEventListener('click', () => {
            navLeft.classList.toggle('open');
        });

        document.addEventListener('click', (event) => {
            if (!navLeft.contains(event.target) && !leftDropdown.contains(event.target)) {
                navLeft.classList.remove('open');
            }
        });
    }
    // Event listener for the Data dropdown
    if (dataMenu && dataDropdown) {
        dataMenu.addEventListener('click', (event) => {
            dataDropdown.classList.toggle('open');
            event.stopPropagation(); // Prevent closing immediately if clicking inside
        });

        document.addEventListener('click', (event) => {
            if (dataDropdown.classList.contains('open') && !dataMenu.contains(event.target)) {
                dataDropdown.classList.remove('open');
            }
        });
    }

    // Event listener for the user profile dropdown
    if (userProfile && rightDropdown) {
        userProfile.addEventListener('click', (event) => {
            rightDropdown.classList.toggle('open');
            event.stopPropagation(); // Prevent closing immediately if clicking inside
        });

        document.addEventListener('click', (event) => {
            if (rightDropdown.classList.contains('open') && !userProfile.contains(event.target)) {
                rightDropdown.classList.remove('open');
            }
        });
    }
});