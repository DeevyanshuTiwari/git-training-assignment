/**
 * Browse Logic
 * Fetches and displays activities, handles search/filtering, and joining.
 */

import { isAuthenticated, logout, getProfile, browseActivities, joinActivity } from './api.js';

// Route Protection
if (!isAuthenticated()) {
    window.location.href = '../index.html';
}

document.addEventListener('DOMContentLoaded', async () => {
    // Topbar Setup (Shared Logic)
    const btnLogout = document.getElementById('btn-logout');
    const userAvatarMini = document.getElementById('user-avatar-mini');
    if (btnLogout) btnLogout.addEventListener('click', logout);

    const activitiesGrid = document.getElementById('activities-grid');
    const searchName = document.getElementById('search-name');
    const searchLocation = document.getElementById('search-location');
    const searchDate = document.getElementById('search-date');
    const searchCategory = document.getElementById('search-category');
    const btnSearch = document.getElementById('btn-search');
    const btnClear = document.getElementById('btn-clear');
    const browseAlert = document.getElementById('browse-alert');

    // State
    let allActivities = [];
    let currentUserId = null;

    // --- Helpers --- //

    const showAlert = (message, isSuccess = false) => {
        browseAlert.textContent = message;
        browseAlert.classList.remove('hidden');
        if (isSuccess) {
            browseAlert.style.backgroundColor = '#dcfce7';
            browseAlert.style.color = '#166534';
            browseAlert.style.borderColor = '#bbf7d0';
        } else {
            browseAlert.style.backgroundColor = '#fef2f2';
            browseAlert.style.color = '#ef4444';
            browseAlert.style.borderColor = '#fecaca';
        }
        setTimeout(() => {
            browseAlert.classList.add('hidden');
        }, 4000);
    };

    // Load Mini Avatar
    try {
        const profile = await getProfile();
        if (profile) {
            currentUserId = profile.id;
            if (userAvatarMini) {
                const name = profile.name || profile.email.split('@')[0];
                userAvatarMini.textContent = name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 1);
            }
        }
    } catch (e) {
        console.error("Avatar load error", e);
    }

    // --- Core Logic --- //

    const fetchAndRenderActivities = async (params = {}) => {
        activitiesGrid.innerHTML = `
            <div class="loading-state">
                <div class="spinner-large"></div>
                <p>Loading activities...</p>
            </div>
        `;
        try {
            // Fetch from API
            allActivities = await browseActivities(params);
            renderGrid(allActivities);
        } catch (error) {
            activitiesGrid.innerHTML = `
                <div class="no-results" style="border-color: #fca5a5; color: #ef4444;">
                    <i class="ph ph-warning-circle" style="color: #ef4444;"></i>
                    <h3>Error loading activities</h3>
                    <p>${error.message}</p>
                </div>
            `;
        }
    };

    const renderGrid = (activities) => {
        if (!activities || activities.length === 0) {
            activitiesGrid.innerHTML = `
                <div class="no-results">
                    <i class="ph ph-magnifying-glass"></i>
                    <h3>No activities found</h3>
                    <p>Try adjusting your search or filter criteria.</p>
                </div>
            `;
            return;
        }

        let html = '';

        activities.forEach(activity => {
            // Provide sensible fallbacks based on generic API schema
            const title = activity.title || 'Untitled Activity';
            const category = activity.category || 'General';
            const location = activity.location || 'TBD';

            // Format Date safely
            const rawDate = activity.activity_date || '';
            let displayDate = 'TBD';
            if (rawDate) {
                try {
                    displayDate = new Date(rawDate).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
                } catch(e) {}
            }
            const time = activity.activity_time || 'TBD';

            // Seat calculations (keeping for display if needed)
            const max = activity.max_participants || 10;
            const current = activity.participants_count || 0;
            const available = max - current;
            const isFull = available <= 0;

            const isOwner = currentUserId === activity.created_by;
            const editStyles = isOwner ? 'flex: 1;' : 'flex: 1; opacity: 0.5; cursor: not-allowed; pointer-events: none;';
            const editDisabledAttr = isOwner ? '' : 'disabled title="Only the owner can edit this activity."';

            // Using template literals to inject HTML dynamically
            html += `
                <div class="activity-card glass-panel">
                    <div class="card-header">
                        <span class="category-tag">${category}</span>
                    </div>
                    <h3 class="activity-title">${title}</h3>

                    <div class="activity-meta">
                        <div class="meta-item">
                            <i class="ph ph-calendar"></i>
                            <span>${displayDate} at ${time}</span>
                        </div>
                        <div class="meta-item">
                            <i class="ph ph-map-pin"></i>
                            <span>${location}</span>
                        </div>
                    </div>

                    <div class="card-footer" style="display: flex; gap: 10px; margin-top: auto; border-top: 1px solid rgba(0,0,0,0.05); padding-top: 16px;">
                        <a href="activity-details.html?id=${activity.id || activity._id}" class="btn btn-primary" style="flex: 1; text-align: center; text-decoration: none; padding: 10px;">View Details</a>
                        <button class="btn btn-outline btn-edit" data-id="${activity.id || activity._id}" style="${editStyles}" ${editDisabledAttr}>Edit</button>
                    </div>
                </div>
            `;
        });

        activitiesGrid.innerHTML = html;

        // Attach event listeners to newly injected Edit buttons
        const editButtons = document.querySelectorAll('.btn-edit');
        editButtons.forEach(btn => {
            btn.addEventListener('click', handleEditClick);
        });
    };

    const handleEditClick = (e) => {
        const activityId = e.currentTarget.getAttribute('data-id');
        window.location.href = `edit-activity.html?id=${activityId}`;
    };

    const handleJoinClick = async (e) => {
        const btn = e.currentTarget;
        const activityId = btn.getAttribute('data-id');

        // Basic loading UI on button
        const originalText = btn.textContent;
        btn.textContent = '...';
        btn.disabled = true;

        try {
            await joinActivity(activityId);
            showAlert("Successfully requested to join activity!", true);
            btn.textContent = 'Requested';
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline');
        } catch (error) {
            showAlert(error.message);
            btn.textContent = originalText;
            btn.disabled = false;
        }
    };

    const applyFilters = () => {
        const params = {
            title: searchName.value.trim(),
            location: searchLocation.value.trim(),
            activity_date: searchDate.value,
            category: searchCategory.value
        };
        fetchAndRenderActivities(params);
    };

    const handleClearFilters = () => {
        searchName.value = '';
        searchLocation.value = '';
        searchDate.value = '';
        searchCategory.value = '';
        applyFilters();
    };

    // --- Initialization --- //

    if (btnSearch) btnSearch.addEventListener('click', applyFilters);
    if (btnClear) btnClear.addEventListener('click', handleClearFilters);

    // Optional: Also search on enter key in inputs
    [searchName, searchLocation, searchDate, searchCategory].forEach(el => {
        if (el) {
            el.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') applyFilters();
            });
        }
    });

    await fetchAndRenderActivities();
});
