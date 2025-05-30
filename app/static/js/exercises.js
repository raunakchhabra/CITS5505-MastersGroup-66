// Get 'lang' parameter from URL or default to 'spanish'
const urlParams = new URLSearchParams(window.location.search);
const lang = urlParams.get('lang') || 'spanish';

// Shared answer options for all languages
const baseOptions = [
    ['Hello, how are you?', 'Goodbye, see you!', 'I am fine, thanks!'],
    ['Thank you', 'Please', 'Goodbye'],
    ['Good morning', 'Good night', 'Good afternoon'],
    ["I'm sorry", 'I love you', 'Excuse me'],
    ['Hello', 'Thank you', 'Goodbye']
];

// Correct answer index for each question (0-based)
const correctAnswerIndices = [0, 0, 0, 0, 2]; // Correct option indexes for each question

// Multilingual versions of each question (same structure, different language)
const questionTexts = {
    spanish: [
        'Translate: "Hola, ¿cómo estás?"',
        'Translate: "Gracias"',
        'Translate: "Buenos días"',
        'Translate: "Lo siento"',
        'Translate: "Adiós"'
    ],
    french: [
        'Translate: "Bonjour, comment ça va ?" ',
        'Translate: "Merci"',
        'Translate: "Bonjour"',
        'Translate: "Je suis désolé"',
        'Translate: "Au revoir"'
    ],
    japanese: [
        'Translate: "こんにちは、お元気ですか？"',
        'Translate: "ありがとう"',
        'Translate: "おはようございます"',
        'Translate: "ごめんなさい"',
        'Translate: "さようなら"'
    ],
    english: [
        'Translate: "Hello, how are you?"',
        'Translate: "Thank you"',
        'Translate: "Good morning"',
        'Translate: "I\'m sorry"',
        'Translate: "Goodbye"'
    ],
    chinese: [
        'Translate: "你好，最近怎么样？"',
        'Translate: "谢谢"',
        'Translate: "早上好"',
        'Translate: "对不起"',
        'Translate: "再见"'
    ]
};

// Select question set for the current language or fallback to Spanish
const langQuestions = questionTexts[lang] || questionTexts['spanish'];

// Combine question text, options, and correct answer index
const questions = langQuestions.map((qText, index) => ({
    text: qText,
    options: baseOptions[index],
    correct: correctAnswerIndices[index]
}));


let currentQuestion = 0;
let correctAnswers = 0;

function loadQuestion() {
    if (currentQuestion < questions.length) {
        const q = questions[currentQuestion];
        document.getElementById('question-text').innerText = q.text;
        document.getElementById('question-counter').innerText = `Question ${currentQuestion + 1} of ${questions.length}`;
        document.getElementById('progress').style.width = `${((currentQuestion) / questions.length) * 100}%`;

        const optionsDiv = document.getElementById('options');
        optionsDiv.innerHTML = '';

        q.options.forEach((opt, i) => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.innerText = opt;
            btn.onclick = () => {
                document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                btn.dataset.selected = opt;  // store the selected answer
            };
            optionsDiv.appendChild(btn);
        });
    }
}

function submitAnswer() {
    const selected = document.querySelector('.option-btn.selected');
    if (!selected) return alert('Please select an option.');

    const userAnswer = selected.dataset.selected;
    const correctAnswer = questions[currentQuestion].options[questions[currentQuestion].correct];
    const isCorrect = userAnswer === correctAnswer;

    // submit the answer to the server
    fetch('/exercise/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: questions[currentQuestion].text,
            user_answer: userAnswer,
            correct_answer: correctAnswer,
            is_correct: isCorrect
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.is_correct) {
            correctAnswers++;
        }

        currentQuestion++;

        if (currentQuestion < questions.length) {
            loadQuestion();
        } else {
            document.getElementById('question-text').innerText = 'Exercise Completed!';
            document.getElementById('options').innerHTML = '';
            document.querySelector('.submit-btn').style.display = 'none';
            document.getElementById('question-counter').innerText = 'Done';
            document.getElementById('progress').style.width = '100%';
            document.getElementById('result').innerText = `You answered ${correctAnswers} out of ${questions.length} correctly. Your score: ${Math.round((correctAnswers / questions.length) * 100)}%`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting answer. Please try again.');
    });
}

window.onload = loadQuestion;