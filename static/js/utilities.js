// WorkSphere UI Utilities

// Toast Notification (already in base template but exposing globally)
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    const iconMap = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    
    toast.className = `p-4 rounded-lg text-white animate-fade-in shadow-lg flex items-center gap-3 ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        type === 'warning' ? 'bg-yellow-500' :
        'bg-blue-500'
    }`;
    toast.innerHTML = `
        <i class="fas ${iconMap[type]}"></i>
        <span>${message}</span>
        <button class="ml-auto text-white hover:opacity-80" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, duration);
}

// Modal Manager
class Modal {
    constructor(title, content, actions = []) {
        this.title = title;
        this.content = content;
        this.actions = actions;
        this.element = null;
    }

    open() {
        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fade-in';
        
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'bg-white rounded-xl shadow-xl max-w-md w-full mx-4 animate-fade-in';
        modal.innerHTML = `
            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h3 class="text-lg font-bold text-gray-900">${this.title}</h3>
                <button class="text-gray-500 hover:text-gray-700" onclick="this.closest('.fixed').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="px-6 py-4">${this.content}</div>
            <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3 justify-end">
                <button class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100" onclick="this.closest('.fixed').remove()">
                    Cancel
                </button>
                ${this.actions.map(action => `
                    <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" onclick="${action.onclick}">
                        ${action.label}
                    </button>
                `).join('')}
            </div>
        `;
        
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        this.element = overlay;
        
        return this;
    }

    close() {
        this.element?.remove();
    }
}

// Data Table Utilities
class DataTable {
    constructor(selector) {
        this.table = document.querySelector(selector);
        this.rows = [];
        this.filteredRows = [];
        this.currentPage = 1;
        this.pageSize = 10;
        this.sortColumn = null;
        this.sortOrder = 'asc';
    }

    // Search/Filter
    filter(query) {
        const searchTerm = query.toLowerCase();
        this.filteredRows = this.rows.filter(row => 
            row.textContent.toLowerCase().includes(searchTerm)
        );
        this.currentPage = 1;
        this.render();
    }

    // Sort
    sort(columnIndex) {
        if (this.sortColumn === columnIndex) {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = columnIndex;
            this.sortOrder = 'asc';
        }
        
        this.rows.sort((a, b) => {
            const aText = a.cells[columnIndex].textContent;
            const bText = b.cells[columnIndex].textContent;
            return this.sortOrder === 'asc' ? 
                aText.localeCompare(bText) : 
                bText.localeCompare(aText);
        });
        
        this.render();
    }

    // Pagination
    setPage(page) {
        this.currentPage = page;
        this.render();
    }

    render() {
        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const paginated = this.filteredRows.slice(start, end);
        
        // Update table display
        const tbody = this.table.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = paginated.map(row => row.outerHTML).join('');
        }
    }
}

// Form Validation
function validateForm(formSelector) {
    const form = document.querySelector(formSelector);
    if (!form) return false;
    
    let isValid = true;
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('border-red-500');
            isValid = false;
        } else {
            input.classList.remove('border-red-500');
        }
    });
    
    if (!isValid) {
        showToast('Please fill all required fields', 'warning');
    }
    
    return isValid;
}

// Confirmation Dialog
function confirm(message, onConfirm, onCancel) {
    const modal = new Modal('Confirm', `<p class="text-gray-700">${message}</p>`, [
        {
            label: 'Confirm',
            onclick: `${onConfirm}; this.closest('.fixed').remove();`
        }
    ]);
    modal.open();
}

// API Call with Loading State
async function apiCall(url, options = {}) {
    try {
        // Add CSRF token if posting
        if (options.method && options.method.toUpperCase() !== 'GET') {
            options.headers = {
                ...options.headers,
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            };
        }

        showToast('Loading...', 'info', 100);
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        showToast(options.successMessage || 'Success!', 'success');
        return data;
    } catch (error) {
        showToast(error.message || 'An error occurred', 'error');
        return null;
    }
}

// Export Functions
function exportToCSV(selector, filename = 'export.csv') {
    const table = document.querySelector(selector);
    if (!table) return;
    
    const csv = Array.from(table.querySelectorAll('tr'))
        .map(row => 
            Array.from(row.querySelectorAll('th, td'))
                .map(cell => `"${cell.textContent.trim()}"`)
                .join(',')
        )
        .join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

function exportToPDF(selector, filename = 'export.pdf') {
    showToast('PDF export requires additional library', 'info');
    // Could implement jsPDF here
}

// Local Storage Utilities
function saveToStorage(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function getFromStorage(key) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
}

function clearStorage(key) {
    localStorage.removeItem(key);
}

// Debounce for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Common Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Search inputs with debounce
    document.querySelectorAll('[data-search]').forEach(input => {
        input.addEventListener('input', debounce(function() {
            const tableSelector = this.dataset.search;
            if (tableSelector) {
                // Implement search logic
            }
        }, 300));
    });

    // Confirm delete buttons
    document.querySelectorAll('[data-confirm]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.dataset.confirm;
            if (window.confirm(message)) {
                this.closest('form')?.submit();
            }
        });
    });
});

// Print functionality
function printPage() {
    window.print();
}

// Responsive utilities
function isMobile() {
    return window.innerWidth < 768;
}

function isTablet() {
    return window.innerWidth >= 768 && window.innerWidth < 1024;
}

function isDesktop() {
    return window.innerWidth >= 1024;
}

// Export all functions globally
window.showToast = showToast;
window.Modal = Modal;
window.DataTable = DataTable;
window.validateForm = validateForm;
window.apiCall = apiCall;
window.exportToCSV = exportToCSV;
window.exportToPDF = exportToPDF;
window.printPage = printPage;
