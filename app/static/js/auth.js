// js/auth.js

// This file contains the code for user authentication including：
// - login
// - register
// - forgot password
// - reset password

document.addEventListener('DOMContentLoaded', () => {
    // registration logic
    const registerForm = document.querySelector('form');
    if (registerForm && window.location.pathname.includes('register.html')) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // to prevent the default form submission

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
                    alert(data.error);
                }
            } catch (error) {
                alert('registration failed, please try again later!');
            }
        });
    }

    // login logic
    const loginForm = document.querySelector('form');
    if (loginForm && window.location.pathname.includes('login.html')) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // to prevent the default form submission

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
                    alert(data.message);
                    window.location.href = '/dashboard.html';
                } else {
                    alert(data.error);
                }
            } catch (error) {
                alert('login failed, please try again later!');
            }
        });
    }

    // forgot password logic
    const forgotPasswordForm = document.querySelector('#forgotPasswordForm');
    if (forgotPasswordForm && window.location.pathname.includes('forgot-password.html')) {
        forgotPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // to prevent the default form submission

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
                    // mock redirect to reset password page
                    // In a real application, you would send an email with a reset link
                    // and the user would click that link to be redirected her
                    window.location.href = '/reset-password.html';
                } else {
                    alert(data.error);
                }
            } catch (error) {
                alert('reset password failed, please try again later!');
            }
        });
    }

    // reset password logic
    const resetPasswordForm = document.querySelector('#resetPasswordForm');
    if (resetPasswordForm && window.location.pathname.includes('reset-password.html')) {
        // from the URL to get the token
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token') || '';

        resetPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // to prevent the default form submission

            const newPassword = document.getElementById('newPassword').value;
            const confirmNewPassword = document.getElementById('confirmNewPassword').value;

            if (newPassword !== confirmNewPassword) {
                alert('unmatched password, please try again!');
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
                    alert(data.error);
                }
            } catch (error) {
                alert('reset password failed, please try again later!');
            }
        });
    }
});
