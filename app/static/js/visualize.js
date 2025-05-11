 // for visualize_data.html

// nav part event listeners
 // JavaScript for toggling navigation dropdowns (same as share_data.html)
        document.addEventListener('DOMContentLoaded', () => {
            const hamburgerMenu = document.querySelector('.hamburger-menu');
            const leftDropdown = document.querySelector('.left-dropdown');
            const userProfile = document.querySelector('.user-profile');
            const rightDropdown = document.querySelector('.right-dropdown');
            const dataMenu = document.querySelector('.data-menu');
            const dataDropdown = document.querySelector('.data-dropdown');
            const navLeft = document.querySelector('.nav-left');

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
            if (dataMenu && dataDropdown) {
                dataMenu.addEventListener('click', (event) => {
                    dataDropdown.classList.toggle('open');
                    event.stopPropagation();
                });
                document.addEventListener('click', (event) => {
                    if (dataDropdown.classList.contains('open') && !dataMenu.contains(event.target)) {
                        dataDropdown.classList.remove('open');
                    }
                });
            }
            if (userProfile && rightDropdown) {
                userProfile.addEventListener('click', (event) => {
                    rightDropdown.classList.toggle('open');
                    event.stopPropagation();
                });
                document.addEventListener('click', (event) => {
                    if (rightDropdown.classList.contains('open') && !userProfile.contains(event.target)) {
                        rightDropdown.classList.remove('open');
                    }
                });
            }
        });