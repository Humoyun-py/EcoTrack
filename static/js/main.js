// Umumiy JavaScript funksiyalari

// Form validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showError(input, 'Bu maydon to\'ldirilishi shart');
            isValid = false;
        } else {
            clearError(input);
        }
    });
    
    return isValid;
}

function showError(input, message) {
    clearError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#e74c3c';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    
    input.style.borderColor = '#e74c3c';
    input.parentNode.appendChild(errorDiv);
}

function clearError(input) {
    input.style.borderColor = '';
    const error = input.parentNode.querySelector('.error-message');
    if (error) {
        error.remove();
    }
}

// Auto-hide alerts
document.addEventListener('DOMContentLoaded', function() {
    // Alert'larni avtomatik yashirish
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
    
    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Local storage utilities
const Storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('LocalStorage ga yozish muvaffaqiyatsiz:', e);
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('LocalStorage dan o\'qish muvaffaqiyatsiz:', e);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('LocalStorage dan o\'chirish muvaffaqiyatsiz:', e);
        }
    }
};

// Theme management
const Theme = {
    init: () => {
        const savedTheme = Storage.get('theme', 'light');
        Theme.set(savedTheme);
    },
    
    set: (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        Storage.set('theme', theme);
    },
    
    toggle: () => {
        const current = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = current === 'light' ? 'dark' : 'light';
        Theme.set(newTheme);
    }
};

// Initialize theme on load
document.addEventListener('DOMContentLoaded', Theme.init);