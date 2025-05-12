// js/auth.js

// This file contains the code for user authentication including:
// - login
// - register
// - forgot password
// - reset password
// - Google login
// - Password strength indicator
// - Auto-generate strong password

document.addEventListener('DOMContentLoaded', () => {
    // Google Login Logic
    const googleLoginBtn = document.getElementById('googleLoginBtn');
    if (googleLoginBtn && window.location.pathname.includes('login.html')) {
        googleLoginBtn.addEventListener('click', () => {
            window.location.href = '/auth/google';
        });
    }
    
    // Floating Label Logic
    const floatingLabelGroups = document.querySelectorAll('.floating-label-group');

    floatingLabelGroups.forEach(group => {
        const input = group.querySelector('.form-control');
        const label = group.querySelector('.form-label');

        if (input && label) {
            input.addEventListener('focus', () => {
                label.classList.add('focused');
            });

            input.addEventListener('blur', () => {
                if (!input.value) {
                    label.classList.remove('focused');
                }
            });

          
            if (input.value) {
                label.classList.add('focused');
            }
        }
    });

    // Registration Logic
    const registerForm = document.querySelector('form');
    if (registerForm && window.location.pathname.includes('register.html')) {
        const nameInput = document.getElementById('name');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const passwordStrength = document.getElementById('password-strength');
        const generatePasswordBtn = document.getElementById('generate-password');
        const togglePassword = document.getElementById('toggle-password');

        // Function to update label position based on input value
        const updateLabelPosition = (input) => {
            const labelClass = input.getAttribute('data-label');
            const label = document.querySelector(`.${labelClass}`);
            if (input.value.trim() !== '') {
                label.classList.add('active');
            } else {
                label.classList.remove('active');
            }
        };

        // Initial check for label positions for all inputs
        [nameInput, emailInput, passwordInput].forEach(input => {
            updateLabelPosition(input);
            input.addEventListener('input', () => updateLabelPosition(input));
            input.addEventListener('focus', () => updateLabelPosition(input));
        });

        // Show "Generate Password" button when password input is focused
        passwordInput.addEventListener('focus', () => {
            generatePasswordBtn.style.display = 'block';
        });

        // Hide "Generate Password" button when password input loses focus
        passwordInput.addEventListener('blur', () => {
            setTimeout(() => {
                if (document.activeElement !== generatePasswordBtn) {
                    generatePasswordBtn.style.display = 'none';
                }
            }, 100);
        });

        // Ensure the button remains visible if clicked
        generatePasswordBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            generatePasswordBtn.style.display = 'block';
        });

        // Toggle password visibility
        togglePassword.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            togglePassword.classList.toggle('fa-eye');
            togglePassword.classList.toggle('fa-eye-slash');
            updateLabelPosition(passwordInput);
        });

        // Real-time password strength indicator and label position update
        passwordInput.addEventListener('input', () => {
            const password = passwordInput.value;
            let strength = 0;

            if (password.length >= 8) strength += 25;
            if (/[A-Z]/.test(password)) strength += 25;
            if (/[0-9]/.test(password)) strength += 25;
            if (/[^A-Za-z0-9]/.test(password)) strength += 25;

            if (strength <= 25) {
                passwordStrength.textContent = 'Weak';
                passwordStrength.style.color = 'red';
            } else if (strength <= 50) {
                passwordStrength.textContent = 'Moderate';
                passwordStrength.style.color = 'orange';
            } else if (strength <= 75) {
                passwordStrength.textContent = 'Good';
                passwordStrength.style.color = 'blue';
            } else {
                passwordStrength.textContent = 'Strong';
                passwordStrength.style.color = 'green';
            }

            updateLabelPosition(passwordInput);
        });

        // Auto-generate strong password
        generatePasswordBtn.addEventListener('click', () => {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()';
            let generatedPassword = '';
            for (let i = 0; i < 12; i++) {
                generatedPassword += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            passwordInput.value = generatedPassword;

            // Trigger password strength check
            const event = new Event('input');
            passwordInput.dispatchEvent(event);

            // Keep button visible after generating password
            generatePasswordBtn.style.display = 'block';

            updateLabelPosition(passwordInput);
        });

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name, email, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message);
                    window.location.href = '/login.html';
                } else {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.style.color = 'red';
                    errorDiv.textContent = data.error;
                    registerForm.appendChild(errorDiv);
                    setTimeout(() => errorDiv.remove(), 3000);
                }
            } catch (error) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.style.color = 'red';
                errorDiv.textContent = 'Registration failed, please try again later!';
                registerForm.appendChild(errorDiv);
                setTimeout(() => errorDiv.remove(), 3000);
            }
        });
    }

    // Login Logic
    const loginForm = document.querySelector('form');
    if (loginForm && window.location.pathname.includes('login.html')) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.href = '/courses.html';
                } else {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.style.color = 'red';
                    errorDiv.textContent = data.error;
                    loginForm.appendChild(errorDiv);
                    setTimeout(() => errorDiv.remove(), 3000);
                }
            } catch (error) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.style.color = 'red';
                errorDiv.textContent = 'Login failed, please try again later!';
                loginForm.appendChild(errorDiv);
                setTimeout(() => errorDiv.remove(), 3000);
            }
        });
    }

    // Forgot Password Logic
    const forgotPasswordForm = document.querySelector('#forgotPasswordForm');
    if (forgotPasswordForm && window.location.pathname.includes('forgot-password.html')) {
        forgotPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('forgotEmail').value;

            try {
                const response = await fetch('/forgot-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email }),
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message);
                    window.location.href = '/reset-password.html';
                } else {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.style.color = 'red';
                    errorDiv.textContent = data.error;
                    forgotPasswordForm.appendChild(errorDiv);
                    setTimeout(() => errorDiv.remove(), 3000);
                }
            } catch (error) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.style.color = 'red';
                errorDiv.textContent = 'Reset password failed, please try again later!';
                forgotPasswordForm.appendChild(errorDiv);
                setTimeout(() => errorDiv.remove(), 3000);
            }
        });
    }

    // Reset Password Logic
    const resetPasswordForm = document.querySelector('#resetPasswordForm');
    if (resetPasswordForm && window.location.pathname.includes('reset-password.html')) {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token') || '';

        resetPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const newPassword = document.getElementById('newPassword').value;
            const confirmNewPassword = document.getElementById('confirmNewPassword').value;

            if (newPassword !== confirmNewPassword) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.style.color = 'red';
                errorDiv.textContent = 'Unmatched password, please try again!';
                resetPasswordForm.appendChild(errorDiv);
                setTimeout(() => errorDiv.remove(), 3000);
                return;
            }

            try {
                const response = await fetch('/reset-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ token, newPassword }),
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message);
                    window.location.href = '/login.html';
                } else {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.style.color = 'red';
                    errorDiv.textContent = data.error;
                    resetPasswordForm.appendChild(errorDiv);
                    setTimeout(() => errorDiv.remove(), 3000);
                }
            } catch (error) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.style.color = 'red';
                errorDiv.textContent = 'Reset password failed, please try again later!';
                resetPasswordForm.appendChild(errorDiv);
                setTimeout(() => errorDiv.remove(), 3000);
            }
        });
    }
});