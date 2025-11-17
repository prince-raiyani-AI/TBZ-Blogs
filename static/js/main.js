/* TBZ Blogs - Main JavaScript
 * Reference: https://developer.mozilla.org/en-US/docs/Web/JavaScript/
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('TBZ Blogs loaded successfully');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize popovers
    initializePopovers();
});

/**
 * Initialize Bootstrap tooltips
 * Reference: https://getbootstrap.com/docs/5.3/components/tooltips/
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 * Reference: https://getbootstrap.com/docs/5.3/components/popovers/
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Toggle dark/light theme
 */
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

/**
 * Load saved theme preference
 */
function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
}

// Load theme on page load
loadThemePreference();

/**
 * Show confirmation dialog
 * Reference: https://getbootstrap.com/docs/5.3/components/modal/
 */
function showConfirmDialog(message, onConfirm) {
    if (confirm(message)) {
        onConfirm();
    }
}

/**
 * Format date to readable format
 * Reference: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options);
}

/**
 * AJAX helper function with CSRF token
 * Reference: https://docs.djangoproject.com/en/5.2/howto/csrf/
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Make AJAX request with CSRF token
 */
function makeAjaxRequest(url, method, data, onSuccess, onError) {
    const csrftoken = getCookie('csrftoken');
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    };
    
    if (method !== 'GET' && data) {
        options.body = JSON.stringify(data);
    }
    
    fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (onSuccess) onSuccess(data);
        })
        .catch(error => {
            console.error('Error:', error);
            if (onError) onError(error);
        });
}

/**
 * Show toast notification
 * Reference: https://getbootstrap.com/docs/5.3/components/toasts/
 */
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}
