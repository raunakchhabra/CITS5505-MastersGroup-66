// Course filtering and display logic
document.addEventListener('DOMContentLoaded', () => {
    // Course filtering elements
    const languageSelect = document.getElementById('language');
    const purposeSelect = document.getElementById('purpose');
    const levelSelect = document.getElementById('level');
    const clearFilters = document.querySelectorAll('.clear-filter');
    const courseListSection = document.querySelector('.course-list');

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
    ];

    let filteredCourses = [...allCourses]; // Start with all courses

    function renderCourses(courses) {
        if (!courseListSection) return;

        courseListSection.innerHTML = '';

        if (courses.length === 0) {
            courseListSection.innerHTML = '<p class="no-courses">No courses found matching your criteria.</p>';
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
                <a href="/exercise/exercises" class="join-button">Join</a>
            `;
            courseListSection.appendChild(courseCard);
        });
    }

    function filterCourses() {
        const selectedLanguage = languageSelect?.value || '';
        const selectedPurpose = purposeSelect?.value || '';
        const selectedLevel = levelSelect?.value || '';

        filteredCourses = allCourses.filter(course => {
            const languageMatch = !selectedLanguage || course.language === selectedLanguage;
            const purposeMatch = !selectedPurpose || course.purpose === selectedPurpose;
            const levelMatch = !selectedLevel || course.level === selectedLevel;
            return languageMatch && purposeMatch && levelMatch;
        });

        renderCourses(filteredCourses);
    }

    // Event listeners for course filtering
    if (languageSelect) {
        languageSelect.addEventListener('change', filterCourses);
    }

    if (purposeSelect) {
        purposeSelect.addEventListener('change', filterCourses);
    }

    if (levelSelect) {
        levelSelect.addEventListener('change', filterCourses);
    }

    // Clear filter buttons
    clearFilters.forEach(button => {
        button.addEventListener('click', function() {
            const filterType = this.dataset.filter;

            if (filterType === 'language' && languageSelect) {
                languageSelect.value = '';
            } else if (filterType === 'purpose' && purposeSelect) {
                purposeSelect.value = '';
            } else if (filterType === 'level' && levelSelect) {
                levelSelect.value = '';
            }

            filterCourses();
        });
    });

    // Initial rendering of courses
    renderCourses(filteredCourses);

    // Add event listeners for join buttons (event delegation)
    courseListSection?.addEventListener('click', (e) => {
        if (e.target.classList.contains('join-button')) {
            const courseCard = e.target.closest('.course-card');
            const courseTitle = courseCard.querySelector('h3').textContent;

            // Here you can add logic to handle course enrollment
            console.log(`Joining course: ${courseTitle}`);

            // Example: Redirect to course enrollment page
            // window.location.href = `/courses/enroll?course=${encodeURIComponent(courseTitle)}`;
        }
    });
});