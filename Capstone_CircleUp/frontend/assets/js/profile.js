/**
 * Profile Logic
 * Handles fetching current user data and updating profile information.
 */

import { isAuthenticated, logout, getProfile, updateProfile } from './api.js';

// Route Protection
if (!isAuthenticated()) {
    window.location.href = '../index.html';
}

document.addEventListener('DOMContentLoaded', async () => {
    // DOM Elements - Shell
    const btnLogout = document.getElementById('btn-logout');
    const userAvatarMini = document.getElementById('user-avatar-mini');

    // DOM Elements - Profile Page
    const profileAvatarLarge = document.getElementById('profile-avatar-large');
    const displayName = document.getElementById('display-name');
    const displayEmail = document.getElementById('display-email');

    // Form Elements
    const profileForm = document.getElementById('profile-form');
    const inputName = document.getElementById('prof-name');
    const inputEmail = document.getElementById('prof-email');
    const inputPhone = document.getElementById('prof-phone');
    const inputCity = document.getElementById('prof-city');
    const inputBio = document.getElementById('prof-bio');

    const profileAlert = document.getElementById('profile-alert');
    const btnEditProfile = document.getElementById('btn-edit-profile');
    const btnCancelEdit = document.getElementById('btn-cancel-edit');
    const btnSaveProfile = document.getElementById('btn-save-profile');

    // State
    let cachedProfile = null;

    // --- Helpers --- //

    const showAlert = (message, isSuccess = false) => {
        profileAlert.textContent = message;
        profileAlert.classList.remove('hidden');
        if (isSuccess) {
            profileAlert.style.backgroundColor = '#dcfce7';
            profileAlert.style.color = '#166534';
            profileAlert.style.borderColor = '#bbf7d0';
        } else {
            profileAlert.removeAttribute('style'); // Default error styling
        }
    };

    const hideAlert = () => {
        profileAlert.classList.add('hidden');
        profileAlert.textContent = '';
    };

    const toggleLoading = (isLoading) => {
        const text = btnSaveProfile.querySelector('.btn-text');
        const spinner = btnSaveProfile.querySelector('.spinner');

        if (isLoading) {
            btnSaveProfile.disabled = true;
            text.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            btnSaveProfile.disabled = false;
            text.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    };

    const updateAvatars = (name) => {
        const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 1);
        if (userAvatarMini) userAvatarMini.textContent = initials;
        if (profileAvatarLarge) profileAvatarLarge.textContent = initials;
    };

    const toggleEditMode = (isEditing) => {
        const fields = [inputName, inputPhone, inputCity, inputBio];
        fields.forEach(field => {
            if (isEditing) {
                field.removeAttribute('readonly');
                field.removeAttribute('disabled');
            } else {
                field.setAttribute('readonly', 'true');
                field.setAttribute('disabled', 'true');
            }
        });

        if (isEditing) {
            btnEditProfile.classList.add('hidden');
            btnCancelEdit.classList.remove('hidden');
            btnSaveProfile.classList.remove('hidden');
            inputName.focus();
        } else {
            btnEditProfile.classList.remove('hidden');
            btnCancelEdit.classList.add('hidden');
            btnSaveProfile.classList.add('hidden');
        }
    };

    const populateForm = (data) => {
        inputName.value = data.name || '';
        inputEmail.value = data.email || '';
        inputPhone.value = data.phone_number || '';
        inputCity.value = data.city || '';
        inputBio.value = data.bio || '';
    };

    // --- Core Logic --- //

    // 1. Fetch and Populate Data
    const loadProfileData = async () => {
        try {
            const profile = await getProfile();
            if (profile) {
                cachedProfile = profile;
                // Populate Headers
                const name = profile.name || 'User';
                displayName.textContent = name;
                displayEmail.textContent = profile.email;
                updateAvatars(name);

                // Populate Form
                populateForm(profile);
            }
        } catch (error) {
            showAlert("Failed to load profile data. Please refresh.");
            console.error("Profile load error:", error);
        }
    };

    // 2. Handle Update
    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        hideAlert();
        toggleLoading(true);

        const updatedData = {
            name: inputName.value,
            phone_number: inputPhone.value,
            city: inputCity.value,
            bio: inputBio.value
        };

        try {
            const newProfile = await updateProfile(updatedData);
            cachedProfile = newProfile; // Update cache

            showAlert("Profile updated successfully!", true);

            // Update Headers dynamically
            const name = newProfile.name || inputName.value;
            displayName.textContent = name;
            updateAvatars(name);

            // Revert to Read-Only mode
            toggleEditMode(false);

            // Auto hide success message after 3 seconds
            setTimeout(hideAlert, 3000);
        } catch (error) {
            showAlert(error.message);
        } finally {
            toggleLoading(false);
        }
    };

    const handleCancelEdit = () => {
        hideAlert();
        if (cachedProfile) {
            populateForm(cachedProfile);
        }
        toggleEditMode(false);
    };

    // --- Initialization --- //

    if (btnLogout) btnLogout.addEventListener('click', logout);
    if (btnEditProfile) btnEditProfile.addEventListener('click', () => toggleEditMode(true));
    if (btnCancelEdit) btnCancelEdit.addEventListener('click', handleCancelEdit);
    if (profileForm) profileForm.addEventListener('submit', handleUpdateProfile);

    // Initial Load
    await loadProfileData();
});
