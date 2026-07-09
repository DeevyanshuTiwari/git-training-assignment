/**
 * Auth Module (UI Interactions + API Integration)
 * Handles Login and Register workflows.
 */

import { login, register } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const overlay = document.getElementById('auth-modal-overlay');
    const loginView = document.getElementById('login-view');
    const registerView = document.getElementById('register-view');

    // Forms
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    // Triggers
    const btnLoginNav = document.getElementById('btn-login');
    const btnRegisterNav = document.getElementById('btn-register');
    const closeModal = document.getElementById('close-modal');

    // Switch links
    const linkToRegister = document.getElementById('link-to-register');
    const linkToLogin = document.getElementById('link-to-login');

    // Error Divs
    const loginError = document.getElementById('login-error');
    const registerError = document.getElementById('register-error');

    // Buttons
    const btnSubmitLogin = document.getElementById('btn-submit-login');
    const btnSubmitRegister = document.getElementById('btn-submit-register');

    // State
    let isModalOpen = false;

    // --- UI Helpers --- //

    const openModal = (view) => {
        isModalOpen = true;
        overlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        // Reset forms and errors
        if (loginForm) loginForm.reset();
        if (registerForm) registerForm.reset();
        hideError(loginError);
        hideError(registerError);

        if (view === 'login') {
            showLoginView();
        } else {
            showRegisterView();
        }
    };

    const close = () => {
        isModalOpen = false;
        overlay.classList.add('hidden');
        document.body.style.overflow = '';
    };

    const showLoginView = () => {
        registerView.classList.add('hidden');
        loginView.classList.remove('hidden');
        hideError(loginError);
    };

    const showRegisterView = () => {
        loginView.classList.add('hidden');
        registerView.classList.remove('hidden');
        hideError(registerError);
    };

    const showError = (element, message, isSuccess = false) => {
        element.textContent = message;
        element.classList.remove('hidden');

        if (isSuccess) {
            element.style.backgroundColor = '#dcfce7';
            element.style.color = '#166534';
            element.style.borderColor = '#bbf7d0';
        } else {
            activityAlert.style.backgroundColor = '#fef2f2';
            activityAlert.style.color = '#ef4444';
            activityAlert.style.borderColor = '#fecaca';
        }
        setTimeout(() => element.classList.add('hidden'), 4000);
    };

    const hideError = (element) => {
        element.textContent = '';
        element.classList.add('hidden');
        element.removeAttribute('style');
    };

    const toggleLoading = (btn, isLoading) => {
        const text = btn.querySelector('.btn-text');
        const spinner = btn.querySelector('.spinner');

        if (isLoading) {
            btn.disabled = true;
            text.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            btn.disabled = false;
            text.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    };

    // --- API Handlers --- //

    const handleLogin = async (e) => {
        e.preventDefault();
        hideError(loginError);

        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        if (!email || !password) {
            showError(loginError, "Please fill in all required fields.");
            return;
        }

        const emailRegex = /^[A-Za-z0-9._%+-]+@gmail\.com$/;
        if (!emailRegex.test(email)) {
            showError(loginError, "Please enter a valid email address.");
            return;
        }

        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/;
        if (!passwordRegex.test(password)) {
            showError(loginError, "Incorrect password");
            return;
        }

        toggleLoading(btnSubmitLogin, true);

        try {
            const response = await login(email, password);

            // FastAPI's OAuth2 response returns 'access_token'
            if (response && response.access_token) {
                localStorage.setItem('circleup_jwt', response.access_token);
                // Redirect to Dashboard
                window.location.href = './pages/dashboard.html';
            } else {
                throw new Error("Authentication failed. Invalid token.");
            }
        } catch (error) {
            showError(loginError, error.message);
        } finally {
            toggleLoading(btnSubmitLogin, false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        hideError(registerError);

        const name = document.getElementById('reg-name').value;
        const email = document.getElementById('reg-email').value;
        const phone = document.getElementById('reg-phone').value;
        const city = document.getElementById('reg-city').value;
        const bio = document.getElementById('reg-bio') ? document.getElementById('reg-bio').value : null;
        const password = document.getElementById('reg-password').value;
        const confirmPassword = document.getElementById('reg-confirm-password').value;

        // Front-end validation
        if (!name || !email || !password || !confirmPassword) {
            showError(registerError, "Please fill in all required fields.");
            return;
        }

        if (name.length < 3 || name.length > 16) {
            showError(registerError, "Name must have atleast 3 character and less than 16 character.");
            return;
        }

        const emailRegex = /^[A-Za-z0-9._%+-]+@gmail\.com$/;
        if (!emailRegex.test(email)) {
            showError(registerError, "Please enter a valid email address.");
            return;
        }

        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/;
        if (!passwordRegex.test(password)) {
            showError(registerError, "Password must be at least 8 characters long, contain one capital letter and small letter, one number, and one special character.");
            return;
        }

        if (password !== confirmPassword) {
            showError(registerError, "Passwords do not match.");
            return;
        }

        const phoneRegex = /^(?:\+91|91)?[6-9]\d{9}$/;
        if (phone && !phoneRegex.test(phone.replace(/[\s-]/g, ''))) {
            showError(registerError, "Please enter a valid phone number.");
            return;
        }

        const userData = {
            name: name,
            email: email,
            phone_number: phone,
            city: city,
            bio: bio,
            password: password
        };

        toggleLoading(btnSubmitRegister, true);

        try {
            await register(userData);
            // On success, switch to Login view
            showLoginView();
            showError(loginError, "Registration successful! Please login to continue.", true);
        } catch (error) {
            showError(registerError, error.message);
        } finally {
            toggleLoading(btnSubmitRegister, false);
        }
    };

    // --- Event Listeners --- //

    if (loginForm) loginForm.addEventListener('submit', handleLogin);
    if (registerForm) registerForm.addEventListener('submit', handleRegister);

    // Open/Close triggers
    if (btnLoginNav) btnLoginNav.addEventListener('click', (e) => { e.preventDefault(); openModal('login'); });
    if (btnRegisterNav) btnRegisterNav.addEventListener('click', (e) => { e.preventDefault(); openModal('register'); });
    if (closeModal) closeModal.addEventListener('click', close);
    if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && isModalOpen) close(); });

    // Switch links
    if (linkToRegister) linkToRegister.addEventListener('click', (e) => { e.preventDefault(); showRegisterView(); });
    if (linkToLogin) linkToLogin.addEventListener('click', (e) => { e.preventDefault(); showLoginView(); });
});
