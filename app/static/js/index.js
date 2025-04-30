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
            // to prevent the default action of the link
            e.preventDefault();

            const languageButton = this.querySelector('.language-btn');
            if (languageButton) {
                const languageName = languageButton.textContent;
                const newTitle = `Learn ${languageName}: 3 Best Ways to Start`;
                learningGoalsTitle.textContent = newTitle;
            } else {
                learningGoalsTitle.textContent = defaultTitle;
            }

            languageOptions.forEach(lang => lang.classList.remove('selected'));
            this.classList.add('selected');

            // comment out the following line to prevent page reload
            //window.location.href = this.querySelector('a').getAttribute('href');
        });
    });

    // if the user clicks on the language button, it will change the title
    const defaultLanguageOption = document.querySelector('.language:first-child'); // assume the first language option is the default one
    if (defaultLanguageOption) {
        const englishButton = defaultLanguageOption.querySelector('.language-btn');
        if (englishButton && englishButton.textContent === 'English') {
            defaultLanguageOption.click();
        }
    }

    $('.goal-link').hover(
        function() {
            // mouse hover effect
            $(this).find('h3').css('color', '#0040ff');
            $(this).find('p').css('color', '#333');
        },
        function() {
            // mouse leave effect
            $(this).find('h3').css('color', ''); // reset to default
            $(this).find('p').css('color', '#666');
        }
    );
});