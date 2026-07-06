import { isAuthenticated, logout, getActivityDetails, updateActivity } from './api.js';

if (!isAuthenticated()) {
    window.location.href = '../index.html';
}

document.addEventListener('DOMContentLoaded', async () => {
    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) btnLogout.addEventListener('click', logout);

    const form = document.getElementById('edit-activity-form');
    const alertBox = document.getElementById('activity-alert');
    const btnSave = document.getElementById('btn-save-activity');
    const btnCancel = document.getElementById('btn-cancel');
    const loader = document.getElementById('loader');

    // Form inputs
    const elTitle = document.getElementById('act-title');
    const elCategory = document.getElementById('act-category');
    const elLocation = document.getElementById('act-location');
    const elDate = document.getElementById('act-date');
    const elTime = document.getElementById('act-time');
    const elMax = document.getElementById('act-max');
    const elDesc = document.getElementById('act-description');

    // Parse URL params
    const urlParams = new URLSearchParams(window.location.search);
    const activityId = urlParams.get('id');

    if (!activityId) {
        loader.classList.add('hidden');
        showAlert("Activity ID is missing. Cannot edit.");
        return;
    }

    // Load initial data
    try {
        const activity = await getActivityDetails(activityId);

        elTitle.value = activity.title || '';
        elCategory.value = activity.category || '';
        elLocation.value = activity.location || '';
        elDate.value = activity.activity_date || '';
        elTime.value = activity.activity_time ? activity.activity_time.substring(0, 5) : '';
        elMax.value = activity.max_participants || '';
        elDesc.value = activity.description || '';

        loader.classList.add('hidden');
        form.classList.remove('hidden');
    } catch (e) {
        loader.classList.add('hidden');
        showAlert("Failed to load activity details: " + e.message);
    }

    const showAlert = (message, isSuccess = false) => {
        alertBox.textContent = message;
        alertBox.classList.remove('hidden');
        if (isSuccess) {
            alertBox.style.backgroundColor = '#dcfce7';
            alertBox.style.color = '#166534';
            alertBox.style.borderColor = '#bbf7d0';
        } else {
            alertBox.removeAttribute('style');
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const toggleLoading = (isLoading) => {
        const text = btnSave.querySelector('.btn-text');
        const spinner = btnSave.querySelector('.spinner');
        if (isLoading) {
            btnSave.disabled = true;
            text.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            btnSave.disabled = false;
            text.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    };

    btnCancel.addEventListener('click', () => {
        window.history.back();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        alertBox.classList.add('hidden');

        const validateForm = (title, description, dateStr, timeStr, maxPart) => {
            if (!title || title.trim().length < 3) return "Title must have at least 3 characters.";
            if (!description || description.trim().split(/\s+/).length < 3) return "Description must have at least 3 words.";
            if (parseInt(maxPart, 10) <= 0) return "Max participants must be at least 1.";

            const now = new Date();
            const selectedDateTime = new Date(`${dateStr}T${timeStr}:00`);
            if (selectedDateTime <= now) {
                return "Activity time cannot be in the past.";
            }
            return null;
        };

        const validationError = validateForm(elTitle.value, elDesc.value, elDate.value, elTime.value, elMax.value);
        if (validationError) {
            showAlert(validationError);
            return;
        }

        toggleLoading(true);

        const updatedData = {
            title: elTitle.value.trim(),
            description: elDesc.value.trim(),
            category: elCategory.value,
            location: elLocation.value.trim(),
            activity_date: elDate.value,
            activity_time: elTime.value + ":00", // Ensure HH:MM:SS format
            max_participants: parseInt(elMax.value, 10)
        };

        try {
            await updateActivity(activityId, updatedData);
            showAlert("Activity updated successfully!", true);
            setTimeout(() => {
                window.location.href = `activity-details.html?id=${activityId}`;
            }, 1500);
        } catch (error) {
            showAlert(error.message);
        } finally {
            toggleLoading(false);
        }
    });
});
