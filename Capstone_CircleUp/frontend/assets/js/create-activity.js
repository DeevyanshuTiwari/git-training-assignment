/**
 * Create Activity Logic
 * Handles form validation, payload construction, and API submission.
 */

import { isAuthenticated, logout, getProfile, createActivity } from './api.js';

// Route Protection
if (!isAuthenticated()) {
    window.location.href = '../index.html';
}

document.addEventListener('DOMContentLoaded', async () => {
    // Topbar Setup (Shared Logic)
    const btnLogout = document.getElementById('btn-logout');
    const userAvatarMini = document.getElementById('user-avatar-mini');
    if (btnLogout) btnLogout.addEventListener('click', logout);

    // Form Elements
    const form = document.getElementById('create-activity-form');
    const inputTitle = document.getElementById('act-title');
    const inputCategory = document.getElementById('act-category');
    const inputLocation = document.getElementById('act-location');
    const inputDate = document.getElementById('act-date');
    const inputTime = document.getElementById('act-time');
    const inputMax = document.getElementById('act-max');
    const inputDescription = document.getElementById('act-description');

    const activityAlert = document.getElementById('activity-alert');
    const btnCreate = document.getElementById('btn-create-activity');
    const btnCancel = document.getElementById('btn-cancel');

    // Load Mini Avatar
    try {
        const profile = await getProfile();
        if (profile && userAvatarMini) {
            const name = profile.full_name || profile.email.split('@')[0];
            userAvatarMini.textContent = name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 1);
        }
    } catch (e) {}

    // --- Set Min Date to Today --- //
    // This prevents users from creating events in the past
    const today = new Date().toISOString().split('T')[0];
    inputDate.setAttribute('min', today);

    // --- Helpers --- //

    const showAlert = (message, isSuccess = false) => {
        activityAlert.textContent = message;
        activityAlert.classList.remove('hidden');
        if (isSuccess) {
            activityAlert.style.backgroundColor = '#dcfce7';
            activityAlert.style.color = '#166534';
            activityAlert.style.borderColor = '#bbf7d0';
        } else {
            activityAlert.style.backgroundColor = '#fef2f2';
            activityAlert.style.color = '#ef4444';
            activityAlert.style.borderColor = '#fecaca';
        }

        // Scroll to alert
        activityAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    const toggleLoading = (isLoading) => {
        const text = btnCreate.querySelector('.btn-text');
        const spinner = btnCreate.querySelector('.spinner');

        if (isLoading) {
            btnCreate.disabled = true;
            text.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            btnCreate.disabled = false;
            text.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    };

    // --- Form Submission --- //

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        activityAlert.classList.add('hidden');

        // Front-end Validation: Prevent past date/time if today
        const selectedDate = inputDate.value;
        const selectedTime = inputTime.value;

        const validateForm = (title, description, dateStr, timeStr, maxPart) => {
            if (!title || title.trim().length < 3) return "Title must have at least 3 characters.";
            if (!description || description.trim().split(/\s+/).length < 3) return "Description must have at least 3 words.";
            if (parseInt(maxPart, 10) <= 0) return "Max participants must be at least 1.";

            const now = new Date();
            const selectedDateTime = new Date(`${dateStr}T${timeStr}`);
            if (selectedDateTime <= now) {
                return "Activity time cannot be in the past.";
            }
            return null;
        };

        const validationError = validateForm(inputTitle.value, inputDescription.value, selectedDate, selectedTime, inputMax.value);
        if (validationError) {
            showAlert(validationError);
            return;
        }

        const payload = {
            title: inputTitle.value,
            description: inputDescription.value,
            category: inputCategory.value,
            location: inputLocation.value,
            activity_date: inputDate.value,
            activity_time: inputTime.value,
            max_participants: parseInt(inputMax.value, 10),
        };

        toggleLoading(true);

        try {
            await createActivity(payload);
            showAlert("Activity created successfully! Redirecting...", true);

            // Redirect to My Activities after a short delay
            setTimeout(() => {
                window.location.href = 'my-activities.html';
            }, 1500);

        } catch (error) {
            showAlert(error.message);
            toggleLoading(false);
        }
    });

    // Cancel Button logic
    if (btnCancel) {
        btnCancel.addEventListener('click', () => {
            window.location.href = 'dashboard.html';
        });
    }
});
