// Main JavaScript for Lost & Found application

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeImagePreview();
    initializeFormValidation();
    initializeSearchFilters();
    initializeContactForm();
    initializeCardAnimations();
    initializeSmoothScrolling();
    initializeAccessibility();
    handleImageErrors();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

// Initialize image preview functionality
function initializeImagePreview() {
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size (16MB limit)
                if (file.size > 16 * 1024 * 1024) {
                    alert('File size must be less than 16MB');
                    this.value = '';
                    return;
                }
                
                // Check file type
                const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Please select a valid image file (PNG, JPG, JPEG, GIF, or WebP)');
                    this.value = '';
                    return;
                }
                
                // Show preview if container exists
                const previewContainer = document.getElementById('imagePreview');
                if (previewContainer) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewContainer.innerHTML = `
                            <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
                            <p class="mt-2 mb-0 text-muted">${file.name}</p>
                        `;
                    };
                    reader.readAsDataURL(file);
                }
            }
        });
    }
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[id$="Form"]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    });
}

// Form validation function
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            showFieldError(field, 'This field is required');
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            isValid = false;
            showFieldError(field, 'Please enter a valid email address');
        }
    });
    
    // Description length validation
    const descriptionField = form.querySelector('#description');
    if (descriptionField && descriptionField.value.trim().length < 10) {
        isValid = false;
        showFieldError(descriptionField, 'Please provide a more detailed description (at least 10 characters)');
    }
    
    return isValid;
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Email validation helper
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Initialize search and filter functionality
function initializeSearchFilters() {
    const filterForm = document.querySelector('form[method="GET"]');
    if (filterForm) {
        // Auto-submit on filter change
        const filterInputs = filterForm.querySelectorAll('select, input[type="text"]');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Add small delay to allow for typing
                setTimeout(() => {
                    if (this.type === 'text') {
                        // Only auto-submit if user has stopped typing for 500ms
                        clearTimeout(this.searchTimeout);
                        this.searchTimeout = setTimeout(() => {
                            filterForm.submit();
                        }, 500);
                    } else {
                        filterForm.submit();
                    }
                }, 100);
            });
        });
    }
    
    // Search functionality in navbar
    const searchForm = document.querySelector('.navbar form[role="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="q"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                alert('Please enter a search term');
                searchInput.focus();
            }
        });
    }
}

// Initialize contact form functionality
function initializeContactForm() {
    const contactButtons = document.querySelectorAll('a[href^="mailto:"]');
    contactButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Track contact attempts (if analytics is implemented)
            if (typeof gtag !== 'undefined') {
                gtag('event', 'contact_attempt', {
                    'event_category': 'user_engagement',
                    'event_label': 'email_contact'
                });
            }
        });
    });
}

// Utility function to show loading state
function showLoading(element, text = 'Loading...') {
    const originalContent = element.innerHTML;
    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
        ${text}
    `;
    element.disabled = true;
    return originalContent;
}

// Utility function to hide loading state
function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Initialize card animations
function initializeCardAnimations() {
    const cards = document.querySelectorAll('.card');
    
    // Intersection Observer for fade-in animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
}

// Initialize smooth scrolling for anchor links
function initializeSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]:not([data-bs-toggle])');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            // Skip if href is just "#" or empty
            if (!href || href === '#') {
                return;
            }
            try {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            } catch (error) {
                // Invalid selector - ignore
                console.warn('Invalid selector:', href);
            }
        });
    });
}

// Initialize accessibility features
function initializeAccessibility() {
    // Add skip link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'visually-hidden-focusable btn btn-primary position-absolute top-0 start-0 m-2';
    skipLink.style.zIndex = '9999';
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content ID if it doesn't exist
    const mainContent = document.querySelector('main');
    if (mainContent && !mainContent.id) {
        mainContent.id = 'main-content';
    }
}

// Error handling for images
function handleImageErrors() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBmb3VuZDwvdGV4dD48L3N2Zz4=';
            this.alt = 'Image not found';
        });
    });
}

// Initialize all features after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCardAnimations();
    initializeSmoothScrolling();
    initializeAccessibility();
    handleImageErrors();
});

// Export functions for potential use in other scripts
window.LostAndFound = {
    showLoading,
    hideLoading,
    formatDate,
    isValidEmail,
    validateForm
};
