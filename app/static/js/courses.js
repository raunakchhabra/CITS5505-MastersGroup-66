document.addEventListener('DOMContentLoaded', () => {

    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const leftDropdown = document.querySelector('.left-dropdown');
    const userProfile = document.querySelector('.user-profile');
    const rightDropdown = document.querySelector('.right-dropdown');
    const dataMenu = document.querySelector('.data-menu'); // Get the new data menu container
    const dataDropdown = document.querySelector('.data-dropdown'); // Get the new data dropdown
    const languageSelect = document.getElementById('language');
    const purposeSelect = document.getElementById('purpose');
    const levelSelect = document.getElementById('level');
    const clearFilters = document.querySelectorAll('.clear-filter');
    const courseListSection = document.querySelector('.course-list');
    const navLeft = document.querySelector('.nav-left');

    // Sample course data (replace with your actual data fetching)
    const allCourses = [
        { language: 'english', purpose: 'travel', level: 'a1', title: 'English for Beginners (Travel)', description: 'Essential English for your travels.', duration: '4 weeks' },
        { language: 'french', purpose: 'academic', level: 'a1', title: 'Beginner French (Academic)', description: 'French basics for academic purposes.', duration: '6 weeks' },
        { language: 'spanish', purpose: 'business', level: 'a2', title: 'Intermediate Spanish (Business)', description: 'Spanish for professional communication.', duration: '8 weeks' },
        { language: 'japanese', purpose: 'travel', level: 'b1', title: 'Intermediate Japanese (Travel)', description: 'Enhance your Japanese travel skills.', duration: '5 weeks' },
        { language: 'chinese', purpose: 'academic', level: 'b2', title: 'Upper-Intermediate Chinese (Academic)', description: 'Advanced Chinese for academic studies.', duration: '10 weeks' },
        { language: 'french', purpose: 'travel', level: 'a2', title: 'French for Travelers (Level 2)', description: 'More French for your adventures.', duration: '5 weeks' },
        { language: 'english', purpose: 'business', level: 'b1', title: 'Business English Communication', description: 'Improve your English in a business context.', duration: '7 weeks' },
        { language: 'spanish', purpose: 'academic', level: 'c1', title: 'Advanced Spanish (Academic)', description: 'Mastering Spanish for academic discussions.', duration: '12 weeks' },
        { language: 'japanese', purpose: 'business', level: 'a1', title: 'Basic Japanese for Business', description: 'Introduction to Japanese business language.', duration: '6 weeks' },
        { language: 'chinese', purpose: 'travel', level: 'a1', title: 'Basic Chinese for Travel', description: 'First steps in Chinese for travelers.', duration: '4 weeks' },
        { language: 'french', purpose: 'business', level: 'b1', title: 'Business French Fluency', description: 'Achieve fluency in French for business.', duration: '9 weeks' },
        { language: 'english', purpose: 'academic', level: 'c2', title: 'Advanced English (Academic Writing)', description: 'Refine your English academic writing skills.', duration: '11 weeks' },
        // Add more courses here
    ];

    let filteredCourses = [...allCourses]; // Start with all courses

    function renderCourses(courses) {
        courseListSection.innerHTML = '';
        if (courses.length === 0) {
            courseListSection.innerHTML = '<p>No courses found matching your criteria.</p>';
            return;
        }
        courses.forEach(course => {
            const courseCard = document.createElement('div');
            courseCard.classList.add('course-card');
            courseCard.innerHTML = `
                <h3>${course.title}</h3>
                <p>${course.description}</p>
                <div class="course-details">
                    <span class="language">Language: ${course.language.charAt(0).toUpperCase() + course.language.slice(1)}</span>
                    <span class="purpose">Purpose: ${course.purpose.charAt(0).toUpperCase() + course.purpose.slice(1)}</span>
                    <span class="level">Level: ${course.level.toUpperCase()}</span>
                </div>
                <button class="join-button">Join</button>
            `;
            courseListSection.appendChild(courseCard);
        });
    }

    function filterCourses() {
        const selectedLanguage = languageSelect.value;
        const selectedPurpose = purposeSelect.value;
        const selectedLevel = levelSelect.value;

        filteredCourses = allCourses.filter(course => {
            const languageMatch = !selectedLanguage || course.language === selectedLanguage;
            const purposeMatch = !selectedPurpose || course.purpose === selectedPurpose;
            const levelMatch = !selectedLevel || course.level === selectedLevel;
            return languageMatch && purposeMatch && levelMatch;
        });

        renderCourses(filteredCourses);
    }

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


    // Event listeners for course filtering
    languageSelect.addEventListener('change', filterCourses);
    purposeSelect.addEventListener('change', filterCourses);
    levelSelect.addEventListener('change', filterCourses);

    clearFilters.forEach(button => {
        button.addEventListener('click', function() {
            const filterType = this.dataset.filter;
            if (filterType === 'language') {
                languageSelect.value = '';
            } else if (filterType === 'purpose') {
                purposeSelect.value = '';
            } else if (filterType === 'level') {
                levelSelect.value = '';
            }
            filterCourses();
        });
    });

    // Initial rendering of courses
    renderCourses(filteredCourses);
});