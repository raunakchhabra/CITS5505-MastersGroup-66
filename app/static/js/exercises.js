const questions = [
    { text: 'Translate: "Hola, ¿cómo estás?"', options: ['Hello, how are you?', 'Goodbye, see you!', 'I am fine, thanks!'], correct: 0 },
    { text: 'Translate: "Gracias"', options: ['Thank you', 'Please', 'Goodbye'], correct: 0 },
    { text: 'Translate: "Buenos días"', options: ['Good morning', 'Good night', 'Good afternoon'], correct: 0 },
    { text: 'Translate: "Lo siento"', options: ['I\'m sorry', 'I love you', 'Excuse me'], correct: 0 },
    { text: 'Translate: "Adios"', options: ['Hello', 'Thank you', 'Goodbye'], correct: 2 }
];

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