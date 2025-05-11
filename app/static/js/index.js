$(document).ready(function() {
    // Handle Why Choose section interactions 
    $('.why-item').click(function() {
        $('.why-item').removeClass('active');
        $('.why-image').removeClass('active');
        $(this).addClass('active');
        const target = $(this).data('target');
        $(`#${target}-img`).addClass('active');
    });

    const languageOptions = document.querySelectorAll('.language');
    const learningGoalsTitle = document.querySelector('.learning-goals .goals-container h2');
    const defaultTitle = learningGoalsTitle.textContent;

    languageOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            const target = e.target.closest('a');
            // if the clicked element is a link with class 'btn-primary', allow default behavior
            if (target && target.classList.contains('btn-primary')) {
                return; // allow default behavior
            }

            // prevent default behavior for other clicks
            e.preventDefault();

            const languageButton = this.querySelector('.language-btn');
            if (languageButton) {
                const languageName = languageButton.textContent;
                const newTitle = `Learn ${languageName}: 3 Best Ways to Start`;
                learningGoalsTitle.textContent = newTitle;
            } else {
                learningGoalsTitle.textContent = defaultTitle;
            }

            // select the clicked language option
            languageOptions.forEach(lang => lang.classList.remove('selected'));
            this.classList.add('selected');
        });
    });

    // if no language is selected, set the default language
    const defaultLanguageOption = document.querySelector('.language:first-child'); // 
    // Select the first language option
    if (defaultLanguageOption) {
        const englishButton = defaultLanguageOption.querySelector('.language-btn');
        if (englishButton && englishButton.textContent === 'English') {
            defaultLanguageOption.click();
        }
    }

    $('.goal-link').hover(
        function() {
            $(this).find('h3').css('color', '#0040ff');
            $(this).find('p').css('color', '#333');
        },
        function() {
            $(this).find('h3').css('color', ''); 
            $(this).find('p').css('color', '#666');
        }
    );
});