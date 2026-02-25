// Main JavaScript for AutoDrive Website

// Mobile Menu Toggle
function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
}

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}

// Smooth Scrolling
document.addEventListener('DOMContentLoaded', function() {
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

// Set Active Navigation Link
function setActiveNavLink() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', setActiveNavLink);

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = '#ff0000';
        } else {
            input.style.borderColor = 'rgba(255, 61, 0, 0.3)';
        }
    });
    
    return isValid;
}

// Show Success Message
function showSuccessMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(135deg, #FF3D00 0%, #FF6F00 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        box-shadow: 0 20px 60px rgba(255, 61, 0, 0.5);
        z-index: 3000;
        animation: slideInRight 0.5s ease-out;
        font-weight: 600;
    `;
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.style.animation = 'slideOutRight 0.5s ease-out';
        setTimeout(() => messageDiv.remove(), 500);
    }, 3000);
}

// Add animation styles for success message
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Local Storage Functions
const Storage = {
    saveItem: function(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    },
    
    getItem: function(key) {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },
    
    removeItem: function(key) {
        localStorage.removeItem(key);
    },
    
    clear: function() {
        localStorage.clear();
    }
};

// User Authentication State
const Auth = {
    isLoggedIn: function() {
        return Storage.getItem('user') !== null;
    },
    
    login: function(userData) {
        Storage.saveItem('user', userData);
        this.updateAuthUI();
    },
    
    logout: function() {
        Storage.removeItem('user');
        this.updateAuthUI();
        window.location.href = 'index.html';
    },
    
    getUser: function() {
        return Storage.getItem('user');
    },
    
    updateAuthUI: function() {
        const authButtons = document.querySelector('.auth-buttons');
        if (!authButtons) return;
        
        if (this.isLoggedIn()) {
            const user = this.getUser();
            authButtons.innerHTML = `
                <span style="color: var(--text); margin-right: 1rem;">Welcome, ${user.name}</span>
                <button class="btn btn-outline" onclick="Auth.logout()">Logout</button>
            `;
        } else {
            authButtons.innerHTML = `
                <button class="btn btn-outline" onclick="openModal('loginModal')">Login</button>
                <button class="btn btn-primary" onclick="openModal('registerModal')">Sign Up</button>
            `;
        }
    }
};

// Initialize Auth UI on page load
document.addEventListener('DOMContentLoaded', function() {
    Auth.updateAuthUI();
});

// Saved Cars Management
const SavedCars = {
    getSaved: function() {
        return Storage.getItem('savedCars') || [];
    },
    
    save: function(car) {
        const saved = this.getSaved();
        if (!saved.find(c => c.id === car.id)) {
            saved.push(car);
            Storage.saveItem('savedCars', saved);
            showSuccessMessage('Car saved to favorites!');
            return true;
        }
        return false;
    },
    
    remove: function(carId) {
        const saved = this.getSaved();
        const filtered = saved.filter(c => c.id !== carId);
        Storage.saveItem('savedCars', filtered);
        showSuccessMessage('Car removed from favorites!');
    },
    
    isSaved: function(carId) {
        return this.getSaved().some(c => c.id === carId);
    }
};

// Test Drive Bookings
const TestDrives = {
    getBookings: function() {
        return Storage.getItem('testDrives') || [];
    },
    
    book: function(booking) {
        const bookings = this.getBookings();
        booking.id = Date.now();
        booking.status = 'pending';
        bookings.push(booking);
        Storage.saveItem('testDrives', bookings);
        return booking;
    },
    
    cancel: function(bookingId) {
        const bookings = this.getBookings();
        const filtered = bookings.filter(b => b.id !== bookingId);
        Storage.saveItem('testDrives', filtered);
    }
};

// Comparison Management
const Comparison = {
    getCompared: function() {
        return Storage.getItem('comparedCars') || [];
    },
    
    add: function(car) {
        const compared = this.getCompared();
        if (compared.length >= 3) {
            showSuccessMessage('Maximum 3 cars can be compared at once!');
            return false;
        }
        if (!compared.find(c => c.id === car.id)) {
            compared.push(car);
            Storage.saveItem('comparedCars', compared);
            showSuccessMessage('Car added to comparison!');
            return true;
        }
        return false;
    },
    
    remove: function(carId) {
        const compared = this.getCompared();
        const filtered = compared.filter(c => c.id !== carId);
        Storage.saveItem('comparedCars', filtered);
    },
    
    clear: function() {
        Storage.saveItem('comparedCars', []);
    }
};

// Format Currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0
    }).format(amount);
}

// Format Date
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Debounce Function
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
