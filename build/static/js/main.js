// QuickInsure Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

function initApp() {
    // Add fade-in animation to cards
    addFadeInAnimation();
    
    // Initialize form handling
    initFormHandling();
    
    // Initialize API testing functionality
    initAPITesting();
}

function addFadeInAnimation() {
    const cards = document.querySelectorAll('.bg-gray-800\\/50');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function initFormHandling() {
    // Add focus effects to inputs
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.classList.add('ring-2', 'ring-blue-500', 'border-blue-500');
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('ring-2', 'ring-blue-500', 'border-blue-500');
        });
    });
}

function initAPITesting() {
    // Add click handlers for API testing buttons if they exist
    const apiButtons = document.querySelectorAll('[data-api-endpoint]');
    apiButtons.forEach(button => {
        button.addEventListener('click', function() {
            const endpoint = this.getAttribute('data-api-endpoint');
            testAPIEndpoint(endpoint);
        });
    });
}

function testAPIEndpoint(endpoint) {
    const token = getJWTToken();
    if (!token) {
        showNotification('No JWT token found. Please login first.', 'error');
        return;
    }
    
    fetch(endpoint, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        showNotification(`API call successful: ${JSON.stringify(data, null, 2)}`, 'success');
    })
    .catch(error => {
        showNotification(`API call failed: ${error.message}`, 'error');
    });
}

function getJWTToken() {
    // Try to get token from session storage or page
    const tokenElement = document.querySelector('code');
    if (tokenElement && tokenElement.textContent.includes('eyJ')) {
        return tokenElement.textContent.trim();
    }
    return null;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-md ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    
    notification.innerHTML = `
        <div class="flex items-center">
            <span class="mr-2">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Utility functions for JWT token manipulation
function decodeJWT(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Error decoding JWT:', error);
        return null;
    }
}

function createForgedJWT(payload, secret = 'secret', algorithm = 'HS256') {
    // This is a simplified version for demonstration
    // In a real scenario, you would use a proper JWT library
    const header = {
        alg: algorithm,
        typ: 'JWT'
    };
    
    const encodedHeader = btoa(JSON.stringify(header));
    const encodedPayload = btoa(JSON.stringify(payload));
    
    if (algorithm === 'none') {
        return `${encodedHeader}.${encodedPayload}.`;
    }
    
    // For HS256, you would need to implement proper HMAC signing
    // This is just a placeholder
    const signature = 'forged_signature';
    
    return `${encodedHeader}.${encodedPayload}.${signature}`;
}

// Export functions for use in browser console
window.QuickInsure = {
    decodeJWT,
    createForgedJWT,
    testAPIEndpoint,
    showNotification
}; 