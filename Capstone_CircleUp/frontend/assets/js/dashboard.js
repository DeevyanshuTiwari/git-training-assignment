/**
 * Dashboard Logic
 * Protected route logic, profile fetching, and data population.
 */

import { isAuthenticated, logout, getProfile, getCreatedActivities, getJoinedActivities, getPendingRequests } from './api.js';

// Route Protection: Redirect if not logged in
if (!isAuthenticated()) {
    window.location.href = '../index.html';
}

document.addEventListener('DOMContentLoaded', async () => {
    // DOM Elements
    const btnLogout = document.getElementById('btn-logout');
    const welcomeMessage = document.getElementById('welcome-message');
    const userAvatarMini = document.getElementById('user-avatar-mini');

    // Auth actions
    if (btnLogout) {
        btnLogout.addEventListener('click', () => {
            logout();
        });
    }

    // Load Profile Data
    try {
        const profile = await getProfile();

        if (profile) {
            // Populate Welcome Message
            const name = profile.name.split(" ")[0];
            welcomeMessage.textContent = `Welcome back, ${name}!`;

            // Populate Avatar initials
            if (profile.name) {
                const initials = profile.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0,1);
                userAvatarMini.textContent = initials;
            } else {
                userAvatarMini.textContent = name.substring(0,2).toUpperCase();
            }
        }
    } catch (error) {
        console.error("Failed to fetch profile for dashboard:", error);
    }

    // Load Stats & Upcoming Activities
    try {
        const [created, joined, pending] = await Promise.all([
            getCreatedActivities(),
            getJoinedActivities(),
            getPendingRequests()
        ]);

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        // Filter for upcoming (created + joined that are >= today)
        const allActivities = [...created, ...joined];

        // Remove duplicates if a user joined their own activity somehow
        const uniqueMap = new Map();
        allActivities.forEach(act => uniqueMap.set(act.id, act));

        const upcomingActivities = Array.from(uniqueMap.values()).filter(act => {
            if (!act.activity_date) return false;
            const actDate = new Date(act.activity_date);
            return actDate >= today;
        });

        // Sort upcoming by date ascending
        upcomingActivities.sort((a, b) => new Date(a.activity_date) - new Date(b.activity_date));

        // Update Stat Badges
        document.getElementById('stat-created').textContent = created.length;
        document.getElementById('stat-joined').textContent = joined.length;
        document.getElementById('stat-pending').textContent = pending.length;
        document.getElementById('stat-upcoming').textContent = upcomingActivities.length;

        // Render Upcoming List
        const upcomingList = document.getElementById('upcoming-list');
        if (upcomingActivities.length === 0) {
            upcomingList.innerHTML = `
                <div class="empty-state">
                    <i class="ph ph-calendar-blank"></i>
                    <p>No upcoming activities. <a href="browse.html">Find something to do!</a></p>
                </div>
            `;
        } else {
            let html = '';
            // Only show up to 3 upcoming on dashboard
            upcomingActivities.slice(0, 3).forEach(act => {
                const dateStr = new Date(act.activity_date).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
                html += `
                    <div class="activity-card-mini">
                        <div class="mini-info">
                            <h4>${act.title}</h4>
                            <p>${dateStr} • ${act.location}</p>
                        </div>
                        <a href="activity-details.html?id=${act.id}" class="btn btn-outline btn-sm">View</a>
                    </div>
                `;
            });
            upcomingList.innerHTML = html;
        }

    } catch (error) {
        console.error("Error loading dashboard stats:", error);
    }
});
