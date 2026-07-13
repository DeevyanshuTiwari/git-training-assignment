/**
 * Activity Details Logic
 * Fetches single activity by ID, renders details, handles Join action.
 */

import { isAuthenticated, logout, getProfile, getActivityDetails, joinActivity } from './api.js';

if (!isAuthenticated()) {
    window.location.href = '../index.html';
}

document.addEventListener('DOMContentLoaded', async () => {
    // Shared Topbar
    const btnLogout = document.getElementById('btn-logout');
    const userAvatarMini = document.getElementById('user-avatar-mini');
    if (btnLogout) btnLogout.addEventListener('click', logout);

    // Parse URL params
    const urlParams = new URLSearchParams(window.location.search);
    const activityId = urlParams.get('id');

    // DOM Elements
    const container = document.getElementById('details-container');
    const loader = document.getElementById('details-loader');
    const errorState = document.getElementById('details-error');

    const elCategory = document.getElementById('det-category');
    const elTitle = document.getElementById('det-title');
    const elOrgAvatar = document.getElementById('org-avatar');
    const elOrgName = document.getElementById('org-name');
    const elDesc = document.getElementById('det-description');

    const elDateTime = document.getElementById('det-datetime');
    const elLocation = document.getElementById('det-location');
    const elSeats = document.getElementById('det-seats');

    const btnJoin = document.getElementById('btn-join-details');
    const detailsAlert = document.getElementById('details-alert');

    // Contact DOM
    const contactContainer = document.getElementById('contact-info-container');
    const contactDetails = document.getElementById('contact-details');
    const restrictedNotice = contactContainer.querySelector('.restricted-notice');
    const orgEmail = document.getElementById('org-email');
    const orgPhone = document.getElementById('org-phone');

    // Load Avatar
    let currentUserProfile = null;
    try {
        currentUserProfile = await getProfile();
        if (currentUserProfile && userAvatarMini) {
            const name = currentUserProfile.full_name || currentUserProfile.email.split('@')[0];
            userAvatarMini.textContent = name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 1);
        }
    } catch (e) {}

    // --- Helpers --- //

    const showAlert = (message, isSuccess = false) => {
        detailsAlert.textContent = message;
        detailsAlert.classList.remove('hidden');
        if (isSuccess) {
            detailsAlert.style.backgroundColor = '#dcfce7';
            detailsAlert.style.color = '#166534';
            detailsAlert.style.borderColor = '#bbf7d0';
        } else {
            detailsAlert.style.backgroundColor = '#fef2f2';
            detailsAlert.style.color = '#ef4444';
            detailsAlert.style.borderColor = '#fecaca';
        }
    };

    const toggleLoadingBtn = (isLoading) => {
        const text = btnJoin.querySelector('.btn-text');
        const spinner = btnJoin.querySelector('.spinner');
        if (isLoading) {
            btnJoin.disabled = true;
            text.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            btnJoin.disabled = false;
            text.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    };

    // --- Core Logic --- //

    if (!activityId) {
        loader.classList.add('hidden');
        errorState.classList.remove('hidden');
        return;
    }

    try {
        const activity = await getActivityDetails(activityId);

        // Populate Data
        elCategory.textContent = activity.category || 'General';
        elTitle.textContent = activity.title || 'Untitled Activity';
        elDesc.textContent = activity.description || 'No description provided.';

        const orgName = activity.organizer_name || 'Anonymous';
        elOrgName.textContent = orgName;
        elOrgAvatar.textContent = orgName.substring(0,1).toUpperCase();

        const rawDate = activity.activity_date || '';
        const displayDate = rawDate ? new Date(rawDate).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) : 'TBD';
        const time = activity.activity_time || 'TBD';
        elDateTime.textContent = `${displayDate} at ${time}`;

        elLocation.textContent = activity.location || 'TBD';

        // Seats Logic
        const max = activity.max_participants || 10;
        const current = activity.participants_count || 0;
        const available = max - current;
        const isFull = available <= 0;

        if (isFull) {
            elSeats.innerHTML = `<span style="color:#ef4444; font-weight:600;">Full</span>`;
            const textSpan = btnJoin.querySelector('.btn-text');
            textSpan.textContent = 'Join Waitlist';
            btnJoin.classList.replace('btn-primary', 'btn-outline');
        } else {
            elSeats.innerHTML = `<span style="color:#22c55e; font-weight:600;">${available} spots left</span> (out of ${max})`;
        }

        // Backend returns organizer email/phone ONLY if the user is an approved participant.
        if (activity.organizer_email || activity.organizer_phone) {
            restrictedNotice.classList.add('hidden');
            contactDetails.classList.remove('hidden');
            orgEmail.textContent = activity.organizer_email || 'Not provided';
            orgPhone.textContent = activity.organizer_phone || 'Not provided';
        }

        // Disable button if user already requested/joined
        if (activity.is_participant) {
            btnJoin.disabled = true;
            btnJoin.classList.replace('btn-primary', 'btn-outline');
            btnJoin.querySelector('.btn-text').textContent = 'Already Requested / Joined';
        }

        // Show UI
        loader.classList.add('hidden');
        container.classList.remove('hidden');

    } catch (error) {
        loader.classList.add('hidden');
        errorState.classList.remove('hidden');
        console.error("Failed to load activity details", error);
    }

    // Join Button Event
    if (btnJoin) {
        btnJoin.addEventListener('click', async () => {
            detailsAlert.classList.add('hidden');
            toggleLoadingBtn(true);

            try {
                await joinActivity(activityId);
                showAlert("Successfully requested to join activity!", true);
                const text = btnJoin.querySelector('.btn-text');
                text.textContent = 'Requested';
                btnJoin.classList.replace('btn-primary', 'btn-outline');
                btnJoin.disabled = true; // Prevent double submit in session
            } catch (error) {
                showAlert(error.message);
            } finally {
                toggleLoadingBtn(false);
            }
        });
    }
});
