// share_data.js - JavaScript for share data functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    const newShareModal = new bootstrap.Modal(document.getElementById('newShareModal'));
    const createGroupModal = new bootstrap.Modal(document.getElementById('createGroupModal'));

    // State management
    let selectedDataItems = [];
    let currentRecipient = null;
    let currentShareType = 'individual'; // 'individual' or 'group'

    // Initialize the page
    initializePage();

    // Consolidate user data to prevent duplicate cards
    function consolidateUserData(users) {
        const userMap = new Map();

        users.forEach(user => {
            const userId = user.id;

            if (userMap.has(userId)) {
                // Merge shared data for existing user
                const existingUser = userMap.get(userId);

                // Merge shared_data arrays
                const existingDataTypes = new Set(existingUser.shared_data.map(d => d.type));
                user.shared_data.forEach(data => {
                    if (!existingDataTypes.has(data.type)) {
                        existingUser.shared_data.push(data);
                    } else {
                        // Update existing data type if needed
                        const existingData = existingUser.shared_data.find(d => d.type === data.type);
                        if (existingData && data.shared) {
                            existingData.shared = true;
                        }
                    }
                });

                // Use the most permissive permission
                if (user.permission === 'edit' || existingUser.permission === 'edit') {
                    existingUser.permission = 'edit';
                }
            } else {
                // Add new user to map
                userMap.set(userId, {
                    ...user,
                    shared_data: [...user.shared_data]
                });
            }
        });

        return Array.from(userMap.values());
    }

    function initializePage() {
        loadSharedUsers();
        loadShareGroups();
        loadSharedWithMe();
        loadShareHistory();
        loadQuickShareGroups();

        // Event listeners
        document.getElementById('create-share-btn').addEventListener('click', showNewShareModal);
        document.getElementById('add-user-btn').addEventListener('click', showNewShareModal);
        document.getElementById('create-group-btn').addEventListener('click', showCreateGroupModal);
        document.getElementById('confirm-share-btn').addEventListener('click', confirmShare);
        document.getElementById('confirm-create-group-btn').addEventListener('click', createGroup);
        document.getElementById('search-users-btn').addEventListener('click', searchUsers);
        document.getElementById('search-groups-btn').addEventListener('click', searchGroups);
        document.getElementById('search-recipient-btn').addEventListener('click', searchRecipient);

        // Tab navigation from sidebar
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const tabName = this.getAttribute('data-tab');
                showTab(tabName);
            });
        });

        // Search on enter key
        document.getElementById('search-users').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') searchUsers();
        });

        document.getElementById('search-groups').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') searchGroups();
        });

        // Recipient search autocomplete
        document.getElementById('share-recipient').addEventListener('input', function() {
            const query = this.value;
            if (query.length > 2) {
                searchRecipientSuggestions(query);
            } else {
                hideSuggestions();
            }
        });
    }

    // Load shared users
    async function loadSharedUsers() {
        showLoading('shared-users-container');

        try {
            const response = await fetch('/api/shared_users');
            const data = await response.json();

            if (response.ok) {
                displaySharedUsers(data.users);
            } else {
                showError('shared-users-container', 'Failed to load shared users');
            }
        } catch (error) {
            showError('shared-users-container', 'An error occurred while loading shared users');
        }
    }

    // Display shared users
    function displaySharedUsers(users) {
        const container = document.getElementById('shared-users-container');

        if (users.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <div class="empty-state-icon">👥</div>
                        <h5>No shared users yet</h5>
                        <p class="text-muted">Start sharing your progress with friends and teachers</p>
                        <button class="btn btn-primary mt-3" onclick="document.getElementById('add-user-btn').click()">
                            Add Your First User
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        // Consolidate users by ID to prevent duplicate cards
        const consolidatedUsers = consolidateUserData(users);
        const userCards = consolidatedUsers.map(user => createUserCard(user)).join('');
        container.innerHTML = userCards + createAddUserCard();
    }

    // Create user card HTML
    function createUserCard(user) {
        const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase();
        const sharedDataList = user.shared_data.map(data => `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="share${user.id}${data.type}" 
                       ${data.shared ? 'checked' : ''} data-user-id="${user.id}" data-type="${data.type}">
                <label class="form-check-label" for="share${user.id}${data.type}">${data.label}</label>
            </div>
        `).join('');

        return `
            <div class="col-md-6">
                <div class="card user-card">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="user-avatar me-3 ${user.role === 'teacher' ? 'bg-info text-white' : 'bg-primary text-white'}">
                                <span>${initials}</span>
                            </div>
                            <div>
                                <h5 class="mb-0">${user.name}</h5>
                                <p class="text-muted mb-0">${user.email}</p>
                            </div>
                            <div class="ms-auto">
                                <span class="badge ${user.role === 'teacher' ? 'bg-info' : 'bg-success'}">
                                    ${user.role === 'teacher' ? 'Teacher' : 'Connected'}
                                </span>
                            </div>
                        </div>
                        <div class="mb-3">
                            <p class="mb-2"><strong>Shared Data:</strong></p>
                            ${sharedDataList}
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="permission${user.id}" 
                                           ${user.permission === 'read' ? 'checked' : ''}>
                                    <label class="form-check-label" for="permission${user.id}">Read-only access</label>
                                </div>
                            </div>
                            <div>
                                <button class="btn btn-sm btn-primary" onclick="updateSharing(${user.id})">Update</button>
                                <button class="btn btn-sm btn-outline-danger" onclick="revokeSharing(${user.id})">Revoke</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Create add user card
    function createAddUserCard() {
        return `
            <div class="col-md-6">
                <div class="card user-card h-100 border-dashed">
                    <div class="card-body d-flex flex-column align-items-center justify-content-center text-center p-4">
                        <div class="mb-3 text-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-person-plus" viewBox="0 0 16 16">
                                <path d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H1s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C9.516 10.68 8.289 10 6 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>
                                <path fill-rule="evenodd" d="M13.5 5a.5.5 0 0 1 .5.5V7h1.5a.5.5 0 0 1 0 1H14v1.5a.5.5 0 0 1-1 0V8h-1.5a.5.5 0 0 1 0-1H13V5.5a.5.5 0 0 1 .5-.5z"/>
                            </svg>
                        </div>
                        <h5>Invite New User</h5>
                        <p class="text-muted">Invite friends, classmates, or teachers to see your language learning progress</p>
                        <button class="btn btn-outline-primary mt-2" onclick="document.getElementById('add-user-btn').click()">
                            <span class="me-2">+</span> Add User
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    // Load share groups
    async function loadShareGroups() {
        showLoading('share-groups-container');

        try {
            const response = await fetch('/api/share_groups');
            const data = await response.json();

            if (response.ok) {
                displayShareGroups(data.groups);
            } else {
                showError('share-groups-container', 'Failed to load groups');
            }
        } catch (error) {
            showError('share-groups-container', 'An error occurred while loading groups');
        }
    }

    // Display share groups
    function displayShareGroups(groups) {
        const container = document.getElementById('share-groups-container');

        if (groups.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <div class="empty-state-icon">👨‍👩‍👧‍👦</div>
                        <h5>No groups yet</h5>
                        <p class="text-muted">Create a group to share progress with multiple people at once</p>
                        <button class="btn btn-primary mt-3" onclick="document.getElementById('create-group-btn').click()">
                            Create Your First Group
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        const groupCards = groups.map(group => createGroupCard(group)).join('');
        container.innerHTML = groupCards + createAddGroupCard();
    }

    // Create group card HTML
    function createGroupCard(group) {
        const sharedDataList = group.shared_data.map(data => `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="group${group.id}${data.type}" 
                       ${data.shared ? 'checked' : ''} data-group-id="${group.id}" data-type="${data.type}">
                <label class="form-check-label" for="group${group.id}${data.type}">${data.label}</label>
            </div>
        `).join('');

        return `
            <div class="col-md-6">
                <div class="card group-card">
                    <div class="card-header">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">${group.name}</h5>
                            <span class="badge bg-primary">${group.member_count} Members</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <p class="text-muted mb-3">${group.description || 'No description'}</p>
                        
                        <p class="mb-2"><strong>Shared Data:</strong></p>
                        <div class="mb-3">
                            ${sharedDataList}
                        </div>
                        
                        <div class="d-flex justify-content-between">
                            <button class="btn btn-sm btn-outline-secondary" onclick="viewGroupMembers(${group.id})">
                                View Members
                            </button>
                            <div>
                                <button class="btn btn-sm btn-primary" onclick="updateGroupSharing(${group.id})">Update</button>
                                <button class="btn btn-sm btn-outline-danger" onclick="leaveGroup(${group.id})">
                                    ${group.is_owner ? 'Delete' : 'Leave'} Group
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Create add group card
    function createAddGroupCard() {
        return `
            <div class="col-md-6">
                <div class="card group-card h-100 border-dashed">
                    <div class="card-body d-flex flex-column align-items-center justify-content-center text-center p-4">
                        <div class="mb-3 text-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-people-fill" viewBox="0 0 16 16">
                                <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1H7zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
                                <path fill-rule="evenodd" d="M5.216 14A2.238 2.238 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.325 6.325 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1h4.216z"/>
                                <path d="M4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/>
                            </svg>
                        </div>
                        <h5>Create New Group</h5>
                        <p class="text-muted">Create a group to share progress with multiple people at once</p>
                        <button class="btn btn-outline-primary mt-2" onclick="document.getElementById('create-group-btn').click()">
                            <span class="me-2">+</span> Create Group
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    // Load shared with me data
    async function loadSharedWithMe() {
        showLoading('shared-with-me-container');

        try {
            const response = await fetch('/api/shared_with_me');
            const data = await response.json();

            if (response.ok) {
                displaySharedWithMe(data.shared_data);
            } else {
                showError('shared-with-me-container', 'Failed to load shared data');
            }
        } catch (error) {
            showError('shared-with-me-container', 'An error occurred while loading shared data');
        }
    }

    // Display shared with me data
    function displaySharedWithMe(sharedData) {
        const container = document.getElementById('shared-with-me-container');

        if (sharedData.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <div class="empty-state-icon">🔄</div>
                        <h5>No data shared with you</h5>
                        <p class="text-muted">When others share their progress with you, it will appear here</p>
                    </div>
                </div>
            `;
            return;
        }

        const dataCards = sharedData.map(data => createSharedDataCard(data)).join('');
        container.innerHTML = dataCards;
    }

    // Create shared data card
    function createSharedDataCard(data) {
        const typeBadgeClass = `data-type-${data.data_type}`;
        const typeLabel = data.data_type.replace('_', ' ').charAt(0).toUpperCase() + data.data_type.slice(1);
        const date = new Date(data.created_at);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const formattedDate = `${year}-${month}-${day}`;
        return `
            <div class="col-md-6 col-lg-4">
                <div class="shared-data-card">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <h6 class="mb-0">${data.title}</h6>
                        <span class="data-type-badge ${typeBadgeClass}">${typeLabel}</span>
                    </div>
                    <p class="text-muted mb-2">Shared by: ${data.owner_name}</p>
                    <p class="text-muted mb-2">Shared on: ${formattedDate}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="permission-icon permission-${data.permission} me-2">
                            <span>${data.permission === 'read' ? 'R' : 'E'}</span>
                        </div>
                        <span class="small">${data.permission === 'read' ? 'Read-only' : 'Edit'} access</span>
                        <a href="${data.view_url}" class="btn btn-sm btn-primary">View</a>
                    </div>
                </div>
            </div>
        `;
    }

    // Load share history
    async function loadShareHistory() {
        showLoading('share-history-container');

        try {
            const response = await fetch('/api/share_history');
            const data = await response.json();

            if (response.ok) {
                displayShareHistory(data.history);
            } else {
                showError('share-history-container', 'Failed to load history');
            }
        } catch (error) {
            showError('share-history-container', 'An error occurred while loading history');
        }
    }

    // Display share history
    function displayShareHistory(history) {
        const container = document.getElementById('share-history-container');

        if (history.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <h5>No sharing history</h5>
                    <p class="text-muted">Your sharing activity will appear here</p>
                </div>
            `;
            return;
        }

        const historyItems = history.map(item => createHistoryItem(item)).join('');
        container.innerHTML = historyItems;
    }

    // Create history item
    function createHistoryItem(item) {
        return `
            <div class="share-history-item">
                <div class="d-flex justify-content-between mb-2">
                    <h6 class="mb-0">${item.title}</h6>
                    <span class="text-muted small">${formatDate(item.created_at)}</span>
                </div>
                <p class="mb-2">${item.description}</p>
                <div class="d-flex align-items-center">
                    <div class="permission-icon permission-${item.permission} me-2">
                        <span>${item.permission === 'read' ? 'R' : 'E'}</span>
                    </div>
                    <span class="small">${item.permission === 'read' ? 'Read-only' : 'Edit'} access</span>
                    <a href="#" class="btn btn-sm btn-link ms-auto" onclick="viewShareDetails(${item.id})">Manage</a>
                </div>
            </div>
        `;
    }

    // Load quick share groups
    async function loadQuickShareGroups() {
        try {
            const response = await fetch('/api/quick_share_groups');
            const data = await response.json();

            if (response.ok) {
                displayQuickShareGroups(data.groups);
            }
        } catch (error) {
            console.error('Error loading quick share groups:', error);
        }
    }

    // Display quick share groups
    function displayQuickShareGroups(groups) {
        const container = document.getElementById('quick-share-groups');

        if (groups.length === 0) {
            container.innerHTML = '<p class="text-muted small">No groups yet</p>';
            return;
        }

        const groupItems = groups.map(group => `
            <a href="#" class="list-group-item list-group-item-action" onclick="quickShareToGroup(${group.id})">
                ${group.name}
            </a>
        `).join('');

        container.innerHTML = groupItems + `
            <a href="#" class="list-group-item list-group-item-action" onclick="document.getElementById('create-group-btn').click()">
                + Create New Group
            </a>
        `;
    }

    // Show new share modal
    async function showNewShareModal() {
        // Load user's data
        await loadUserData();
        newShareModal.show();
    }

    // Load user's data for sharing
    async function loadUserData() {
        try {
            const response = await fetch('/api/my_data_summary');
            const data = await response.json();

            if (response.ok) {
                displayDataSelection(data.data_items);
            }
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    }

    // Display data selection in modal
    function displayDataSelection(dataItems) {
        const container = document.getElementById('data-selection-container');

        if (dataItems.length === 0) {
            container.innerHTML = '<p class="text-muted">No data available to share</p>';
            return;
        }

        const dataCheckboxes = dataItems.map(item => `
            <div class="data-item-checkbox">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="data-${item.id}" 
                           value="${item.id}" onchange="toggleDataItem(${item.id})">
                    <label class="form-check-label" for="data-${item.id}">
                        <strong>${item.title}</strong>
                        <span class="text-muted"> - ${item.data_type}</span>
                        <br>
                        <small class="text-muted">${item.description || 'No description'}</small>
                    </label>
                </div>
            </div>
        `).join('');

        container.innerHTML = dataCheckboxes;
    }

    // Toggle data item selection
    window.toggleDataItem = function(dataId) {
        const index = selectedDataItems.indexOf(dataId);
        if (index > -1) {
            selectedDataItems.splice(index, 1);
        } else {
            selectedDataItems.push(dataId);
        }
    };

    // Search recipient suggestions
    async function searchRecipientSuggestions(query) {
        try {
            const response = await fetch(`/api/search_users?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (response.ok) {
                displaySuggestions(data.users);
            }
        } catch (error) {
            console.error('Error searching users:', error);
        }
    }

    // Display suggestions
    function displaySuggestions(users) {
        const container = document.getElementById('recipient-suggestions');

        if (users.length === 0) {
            container.style.display = 'none';
            return;
        }

        const suggestions = users.map(user => `
            <div class="suggestion-item" onclick="selectRecipient(${user.id}, '${user.email}')">
                <strong>${user.name}</strong> - ${user.email}
            </div>
        `).join('');

        container.innerHTML = suggestions;
        container.style.display = 'block';
    }

    // Hide suggestions
    function hideSuggestions() {
        document.getElementById('recipient-suggestions').style.display = 'none';
    }

    // Select recipient
    window.selectRecipient = function(userId, email) {
        currentRecipient = userId;
        document.getElementById('share-recipient').value = email;
        hideSuggestions();
    };

    // Confirm share
    async function confirmShare() {
        const recipientInput = document.getElementById('share-recipient').value;
        const permission = document.getElementById('share-permission').value;
        const message = document.getElementById('share-message').value;

        if (!currentRecipient && !recipientInput) {
            showAlert('Please select a recipient', 'error');
            return;
        }

        if (selectedDataItems.length === 0) {
            showAlert('Please select at least one data item to share', 'error');
            return;
        }

        const shareData = {
            recipient_id: currentRecipient,
            recipient_email: !currentRecipient ? recipientInput : null,
            data_ids: selectedDataItems,
            permission: permission,
            message: message
        };

        try {
            const response = await fetch('/api/share_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(shareData)
            });

            const result = await response.json();

            if (response.ok) {
                showAlert('Data shared successfully!', 'success');
                newShareModal.hide();
                // Reset the form
                document.getElementById('share-form').reset();
                selectedDataItems = [];
                currentRecipient = null;
                // Reload the shared users list
                loadSharedUsers();
                loadShareHistory();
            } else {
                showAlert(result.error || 'Failed to share data', 'error');
            }
        } catch (error) {
            showAlert('An error occurred while sharing data', 'error');
        }
    }

    // Create group
    async function createGroup() {
        const groupName = document.getElementById('group-name').value;
        const groupDescription = document.getElementById('group-description').value;

        if (!groupName) {
            showAlert('Please enter a group name', 'error');
            return;
        }

        try {
            const response = await fetch('/api/create_group', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: groupName,
                    description: groupDescription
                })
            });

            const result = await response.json();

            if (response.ok) {
                showAlert('Group created successfully!', 'success');
                createGroupModal.hide();
                loadShareGroups();
                document.getElementById('create-group-form').reset();
            } else {
                showAlert(result.error || 'Failed to create group', 'error');
            }
        } catch (error) {
            showAlert('An error occurred while creating group', 'error');
        }
    }

    // Search users
    async function searchUsers() {
        const query = document.getElementById('search-users').value;
        showLoading('shared-users-container');

        try {
            const response = await fetch(`/api/search_shared_users?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (response.ok) {
                displaySharedUsers(data.users);
            } else {
                showError('shared-users-container', 'Search failed');
            }
        } catch (error) {
            showError('shared-users-container', 'An error occurred during search');
        }
    }

    // Search groups
    async function searchGroups() {
        const query = document.getElementById('search-groups').value;
        showLoading('share-groups-container');

        try {
            const response = await fetch(`/api/search_groups?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (response.ok) {
                displayShareGroups(data.groups);
            } else {
                showError('share-groups-container', 'Search failed');
            }
        } catch (error) {
            showError('share-groups-container', 'An error occurred during search');
        }
    }

    // Search recipient
    async function searchRecipient() {
        const query = document.getElementById('share-recipient').value;
        if (query.length < 2) {
            showAlert('Please enter at least 2 characters to search', 'warning');
            return;
        }
        searchRecipientSuggestions(query);
    }

    // Create group modal
    function showCreateGroupModal() {
        createGroupModal.show();
    }

    // Utility functions
    function showLoading(containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <div class="col-12">
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        `;
    }

    function showError(containerId, message) {
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger" role="alert">
                    ${message}
                </div>
            </div>
        `;
    }

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        const container = document.querySelector('.col-md-9');
        container.insertBefore(alertDiv, container.firstChild);

        setTimeout(() => alertDiv.remove(), 5000);
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
            return 'Today';
        } else if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return `${diffDays} days ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    function showTab(tabName) {
        // Update sidebar active state
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            if (link.getAttribute('data-tab') === tabName) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Show corresponding tab
        const tabButton = document.querySelector(`#${tabName}-tab`);
        if (tabButton) {
            tabButton.click();
        }
    }

    // Global functions for onclick handlers
    window.updateSharing = async function(userId) {
        const checkboxes = document.querySelectorAll(`[data-user-id="${userId}"]`);
        const permissionToggle = document.getElementById(`permission${userId}`);

        const sharedData = [];
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                sharedData.push(checkbox.getAttribute('data-type'));
            }
        });

        const permission = permissionToggle.checked ? 'read' : 'edit';

        try {
            const response = await fetch(`/api/update_sharing/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    shared_data: sharedData,
                    permission: permission
                })
            });

            if (response.ok) {
                showAlert('Sharing settings updated successfully', 'success');
            } else {
                showAlert('Failed to update sharing settings', 'error');
            }
        } catch (error) {
            showAlert('An error occurred while updating', 'error');
        }
    };

    window.revokeSharing = async function(userId) {
        if (!confirm('Are you sure you want to revoke sharing with this user?')) {
            return;
        }

        try {
            const response = await fetch(`/api/revoke_share/${userId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showAlert('Sharing revoked successfully', 'success');
                loadSharedUsers();
            } else {
                showAlert('Failed to revoke sharing', 'error');
            }
        } catch (error) {
            showAlert('An error occurred', 'error');
        }
    };

    window.updateGroupSharing = async function(groupId) {
        const checkboxes = document.querySelectorAll(`[data-group-id="${groupId}"]`);

        const sharedData = [];
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                sharedData.push(checkbox.getAttribute('data-type'));
            }
        });

        try {
            const response = await fetch(`/api/update_group_sharing/${groupId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    shared_data: sharedData
                })
            });

            if (response.ok) {
                showAlert('Group sharing settings updated', 'success');
            } else {
                showAlert('Failed to update group settings', 'error');
            }
        } catch (error) {
            showAlert('An error occurred', 'error');
        }
    };

    window.leaveGroup = async function(groupId) {
        const confirmMessage = 'Are you sure you want to leave this group?';
        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            const response = await fetch(`/api/leave_group/${groupId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showAlert('Left group successfully', 'success');
                loadShareGroups();
            } else {
                showAlert('Failed to leave group', 'error');
            }
        } catch (error) {
            showAlert('An error occurred', 'error');
        }
    };

    window.viewGroupMembers = async function(groupId) {
        try {
            const response = await fetch(`/api/group_members/${groupId}`);
            const data = await response.json();

            if (response.ok) {
                showGroupMembersModal(data.members);
            } else {
                showAlert('Failed to load group members', 'error');
            }
        } catch (error) {
            showAlert('An error occurred', 'error');
        }
    };

    window.viewShareDetails = async function(shareId) {
        try {
            const response = await fetch(`/api/share_details/${shareId}`);
            const data = await response.json();

            if (response.ok) {
                showShareDetailsModal(data);
            } else {
                showAlert('Failed to load share details', 'error');
            }
        } catch (error) {
            showAlert('An error occurred', 'error');
        }
    };

    window.quickShareToGroup = async function(groupId) {
        currentShareType = 'group';
        currentRecipient = groupId;
        await loadUserData();
        document.getElementById('share-recipient').value = 'Group: ' + groupId;
        document.getElementById('share-recipient').disabled = true;
        newShareModal.show();
    };

    // Modal display functions
    function showGroupMembersModal(members) {
        const modalContent = members.map(member => `
            <div class="d-flex align-items-center justify-content-between p-2">
                <div>
                    <strong>${member.name}</strong>
                    <span class="text-muted">${member.email}</span>
                </div>
                <span class="badge ${member.is_owner ? 'bg-primary' : 'bg-secondary'}">
                    ${member.is_owner ? 'Owner' : 'Member'}
                </span>
            </div>
        `).join('');

        const modalHtml = `
            <div class="modal fade" id="groupMembersModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Group Members</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${modalContent}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('groupMembersModal'));
        modal.show();

        document.getElementById('groupMembersModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    function showShareDetailsModal(details) {
        const modalHtml = `
            <div class="modal fade" id="shareDetailsModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Share Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p><strong>Shared with:</strong> ${details.recipient_name}</p>
                            <p><strong>Data Type:</strong> ${details.data_type}</p>
                            <p><strong>Permission:</strong> ${details.permission}</p>
                            <p><strong>Shared on:</strong> ${formatDate(details.created_at)}</p>
                            ${details.message ? `<p><strong>Message:</strong> ${details.message}</p>` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-danger" onclick="revokeShare(${details.id})">
                                Revoke Access
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('shareDetailsModal'));
        modal.show();

        document.getElementById('shareDetailsModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    window.revokeShare = async function(shareId) {
        if (!confirm('Are you sure you want to revoke this share?')) {
            return;
        }

        try {
            const response = await fetch(`/api/revoke_share/${shareId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showAlert('Share revoked successfully', 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('shareDetailsModal'));
                modal.hide();
                loadShareHistory();
                loadSharedUsers();
            } else {
                showAlert('Failed to revoke share', 'error');
            }
        } catch (error) {
            showAlert('An error occurred', 'error');
        }
    };

    // Reset modal state when closed
    document.getElementById('newShareModal').addEventListener('hidden.bs.modal', function() {
        document.getElementById('share-form').reset();
        selectedDataItems = [];
        currentRecipient = null;
        currentShareType = 'individual';
        document.getElementById('share-recipient').disabled = false;
        hideSuggestions();
    });

    document.getElementById('createGroupModal').addEventListener('hidden.bs.modal', function() {
        document.getElementById('create-group-form').reset();
    });
});