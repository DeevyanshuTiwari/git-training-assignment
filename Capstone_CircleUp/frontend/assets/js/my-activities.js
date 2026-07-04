import {
    isAuthenticated, logout, getProfile,
    getCreatedActivities, getJoinedActivities, getPendingRequests,
    cancelActivity, getOrganizerContact, getActivityParticipants,
    getActivityRequests, approveParticipant, rejectParticipant,
    withdrawRequest, leaveActivity
} from './api.js';

if (!isAuthenticated()) {
    window.location.href = '../index.html';
}

document.addEventListener('DOMContentLoaded', async () => {
    const btnLogout = document.getElementById('btn-logout');
    const userAvatarMini = document.getElementById('user-avatar-mini');
    if (btnLogout) btnLogout.addEventListener('click', logout);

    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const globalAlert = document.getElementById('my-activities-alert');

    const showAlert = (message, isSuccess = false) => {
        globalAlert.textContent = message;
        globalAlert.classList.remove('hidden');
        if (isSuccess) {
            globalAlert.style.backgroundColor = '#dcfce7';
            globalAlert.style.color = '#166534';
            globalAlert.style.borderColor = '#bbf7d0';
        } else {
            globalAlert.removeAttribute('style');
        }
        setTimeout(() => globalAlert.classList.add('hidden'), 4000);
    };

    let currentUserProfile = null;
    try {
        currentUserProfile = await getProfile();
        if (currentUserProfile && userAvatarMini) {
            const name = currentUserProfile.full_name || currentUserProfile.email.split('@')[0];
            userAvatarMini.textContent = name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
        }
    } catch (e) {}

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');
        });
    });

    const formatDate = (raw) => {
        if (!raw) return 'TBD';
        try { return new Date(raw).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }); }
        catch(e) { return 'TBD'; }
    };

    const loadHosting = async () => {
        const loader = document.getElementById('hosting-loader');
        const list = document.getElementById('hosting-list');
        loader.classList.remove('hidden');
        list.innerHTML = '';
        try {
            const activities = await getCreatedActivities();
            loader.classList.add('hidden');
            if (activities.length === 0) {
                list.innerHTML = `
                    <div class="no-results" style="padding: 40px; text-align: center; background: white; border-radius: 12px; border: 1px dashed #cbd5e1;">
                        <i class="ph ph-plus-circle" style="font-size: 3rem; color: #cbd5e1;"></i>
                        <h3 style="margin-top: 10px;">You aren't hosting any activities</h3>
                        <a href="create-activity.html" class="btn btn-primary">Host an Activity</a>
                    </div>`;
                return;
            }
            let html = '';
            activities.forEach(act => {
                const statusBadge = act.status === 'CANCELLED' ? '<span class="status-badge rejected">Cancelled</span>' : '<span class="status-badge hosting">Hosting</span>';
                html += `
                    <div class="list-item">
                        <div class="item-main">
                            <div class="item-header">
                                <h3>${act.title || 'Untitled'}</h3>
                                ${statusBadge}
                            </div>
                            <div class="item-meta">
                                <span><i class="ph ph-calendar"></i> ${formatDate(act.activity_date)} at ${act.activity_time || ''}</span>
                                <span><i class="ph ph-users"></i> ${act.max_participants || 0} spots</span>
                            </div>
                        </div>
                        <div class="item-actions">
                            <button class="btn btn-outline manage-btn" onclick="openManageRequests(${act.id})">Requests</button>
                            <button class="btn btn-outline manage-btn" onclick="openParticipants(${act.id})">Participants</button>
                            ${act.status !== 'CANCELLED' ? `<button class="btn btn-outline manage-btn" style="color: #991b1b; border-color: #991b1b;" onclick="handleCancelActivity(${act.id})">Cancel</button>` : ''}
                        </div>
                    </div>
                `;
            });
            list.innerHTML = html;
        } catch (e) {
            loader.classList.add('hidden');
            showAlert("Error loading hosted activities.");
        }
    };

    const loadJoined = async () => {
        const loader = document.getElementById('joined-loader');
        const list = document.getElementById('joined-list');
        loader.classList.remove('hidden');
        list.innerHTML = '';
        try {
            const activities = await getJoinedActivities();
            loader.classList.add('hidden');
            if (activities.length === 0) {
                list.innerHTML = `
                    <div class="no-results" style="padding: 40px; text-align: center; background: white; border-radius: 12px; border: 1px dashed #cbd5e1;">
                        <i class="ph ph-calendar-blank" style="font-size: 3rem; color: #cbd5e1;"></i>
                        <h3 style="margin-top: 10px;">You haven't joined any activities yet</h3>
                        <a href="browse.html" class="btn btn-primary">Browse Activities</a>
                    </div>`;
                return;
            }
            let html = '';
            activities.forEach(act => {
                html += `
                    <div class="list-item">
                        <div class="item-main">
                            <div class="item-header">
                                <h3>${act.title || 'Untitled'}</h3>
                                <span class="status-badge approved">Joined</span>
                            </div>
                            <div class="item-meta">
                                <span><i class="ph ph-calendar"></i> ${formatDate(act.activity_date)} at ${act.activity_time || ''}</span>
                                <span><i class="ph ph-map-pin"></i> ${act.location || 'TBD'}</span>
                            </div>
                        </div>
                        <div class="item-actions">
                            <button class="btn btn-outline manage-btn" onclick="openOrganizerContact(${act.id})">Organizer</button>
                            <button class="btn btn-outline manage-btn" style="color: #991b1b; border-color: #991b1b;" onclick="handleLeaveActivity(${act.id})">Leave</button>
                        </div>
                    </div>
                `;
            });
            list.innerHTML = html;
        } catch (e) {
            loader.classList.add('hidden');
            showAlert("Error loading joined activities.");
        }
    };

    const loadPending = async () => {
        const loader = document.getElementById('pending-loader');
        const list = document.getElementById('pending-list');
        loader.classList.remove('hidden');
        list.innerHTML = '';
        try {
            const requests = await getPendingRequests();
            loader.classList.add('hidden');
            if (requests.length === 0) {
                list.innerHTML = `
                    <div class="no-results" style="padding: 40px; text-align: center; background: white; border-radius: 12px; border: 1px dashed #cbd5e1;">
                        <i class="ph ph-hourglass" style="font-size: 3rem; color: #cbd5e1;"></i>
                        <h3 style="margin-top: 10px;">No pending requests</h3>
                    </div>`;
                return;
            }
            let html = '';
            requests.forEach(req => {
                html += `
                    <div class="list-item">
                        <div class="item-main">
                            <div class="item-header">
                                <h3>Activity ID: ${req.activity_id}</h3>
                                <span class="status-badge pending">Pending</span>
                            </div>
                            <div class="item-meta">
                                <span>Waiting for organizer approval</span>
                            </div>
                        </div>
                        <div class="item-actions">
                            <button class="btn btn-outline manage-btn" style="color: #991b1b; border-color: #991b1b;" onclick="handleWithdrawRequest(${req.id})">Withdraw</button>
                        </div>
                    </div>
                `;
            });
            list.innerHTML = html;
        } catch (e) {
            loader.classList.add('hidden');
            showAlert("Error loading pending requests.");
        }
    };

    window.handleCancelActivity = async (id) => {
        if (!confirm("Are you sure you want to cancel this activity?")) return;
        try {
            await cancelActivity(id);
            showAlert("Activity cancelled successfully", true);
            loadHosting();
        } catch (e) {
            showAlert("Error cancelling activity: " + e.message);
        }
    };

    window.handleLeaveActivity = async (id) => {
        if (!confirm("Are you sure you want to leave this activity?")) return;
        try {
            await leaveActivity(id);
            showAlert("Successfully left activity", true);
            loadJoined();
        } catch (e) {
            showAlert("Error leaving activity: " + e.message);
        }
    };

    window.handleWithdrawRequest = async (id) => {
        if (!confirm("Are you sure you want to withdraw this request?")) return;
        try {
            await withdrawRequest(id);
            showAlert("Request withdrawn", true);
            loadPending();
        } catch (e) {
            showAlert("Error withdrawing request: " + e.message);
        }
    };

    window.openManageRequests = async (activityId) => {
        const modal = document.getElementById('manage-requests-modal');
        const list = document.getElementById('requests-list');
        list.innerHTML = '<div class="spinner-large" style="margin:20px auto;"></div>';
        modal.classList.remove('hidden');
        try {
            const requests = await getActivityRequests(activityId);
            if (requests.length === 0) {
                list.innerHTML = '<p style="text-align:center; padding: 20px;">No requests found.</p>';
                return;
            }
            let html = '';
            requests.forEach(req => {
                if(req.status !== 'PENDING') return;
                html += `
                    <div class="list-item" style="margin-bottom:10px;">
                        <div class="item-main">
                            <div class="item-header">
                                <h3>${req.user_name || 'User ' + req.user_id}</h3>
                            </div>
                        </div>
                        <div class="item-actions">
                            <button class="btn btn-primary" onclick="handleApprove(${req.id}, ${activityId})">Approve</button>
                            <button class="btn btn-outline" style="color:#991b1b; border-color:#991b1b;" onclick="handleReject(${req.id}, ${activityId})">Reject</button>
                        </div>
                    </div>
                `;
            });
            if(html === '') html = '<p style="text-align:center; padding: 20px;">No pending requests.</p>';
            list.innerHTML = html;
        } catch (e) {
            list.innerHTML = '<p style="color:red; text-align:center;">Failed to load requests.</p>';
        }
    };

    window.handleApprove = async (reqId, actId) => {
        try {
            await approveParticipant(reqId);
            openManageRequests(actId);
            loadHosting();
        } catch (e) {
            alert(e.message);
        }
    };

    window.handleReject = async (reqId, actId) => {
        try {
            await rejectParticipant(reqId);
            openManageRequests(actId);
        } catch (e) {
            alert(e.message);
        }
    };

    window.openParticipants = async (activityId) => {
        const modal = document.getElementById('participants-modal');
        const list = document.getElementById('participants-list');
        list.innerHTML = '<div class="spinner-large" style="margin:20px auto;"></div>';
        modal.classList.remove('hidden');
        try {
            const participants = await getActivityParticipants(activityId);
            if (participants.length === 0) {
                list.innerHTML = '<p style="text-align:center; padding: 20px;">No approved participants.</p>';
                return;
            }
            let html = '';
            participants.forEach(p => {
                html += `
                    <div class="list-item" style="margin-bottom:10px; display:block;">
                        <p><strong>Name:</strong> ${p.name || 'N/A'}</p>
                        <p><strong>Email:</strong> ${p.email}</p>
                        <p><strong>Phone:</strong> ${p.phone_number || 'N/A'}</p>
                    </div>
                `;
            });
            list.innerHTML = html;
        } catch (e) {
            list.innerHTML = '<p style="color:red; text-align:center;">Failed to load participants.</p>';
        }
    };

    window.openOrganizerContact = async (activityId) => {
        const modal = document.getElementById('organizer-modal');
        const info = document.getElementById('organizer-info');
        info.innerHTML = '<div class="spinner-large" style="margin:20px auto;"></div>';
        modal.classList.remove('hidden');
        try {
            const contact = await getOrganizerContact(activityId);
            info.innerHTML = `
                <p><strong>Organizer:</strong> ${contact.name}</p>
                <p><strong>Phone:</strong> ${contact.phone_number || 'Not provided'}</p>
            `;
        } catch (e) {
            info.innerHTML = '<p style="color:red;">Failed to load contact info.</p>';
        }
    };

    await Promise.all([loadHosting(), loadJoined(), loadPending()]);
});
