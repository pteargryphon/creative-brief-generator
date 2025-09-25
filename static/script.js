let currentJobId = null;
let pollInterval = null;

function generateBrief() {
    const url = document.getElementById('brand-url').value.trim();
    
    if (!url) {
        alert('Please enter a valid URL');
        return;
    }
    
    // Validate URL format
    try {
        new URL(url);
    } catch (e) {
        alert('Please enter a valid URL (e.g., https://example.com)');
        return;
    }
    
    // Disable button and show progress
    document.getElementById('generate-btn').disabled = true;
    showSection('progress-section');
    
    // Reset progress
    updateProgress(0, 'Initializing...');
    
    // Send request to backend
    fetch('/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to start generation');
        }
        return response.json();
    })
    .then(data => {
        currentJobId = data.job_id;
        startPolling();
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Failed to start brief generation. Please try again.');
    });
}

function startPolling() {
    // Poll every 2 seconds
    pollInterval = setInterval(checkStatus, 2000);
    // Check immediately
    checkStatus();
}

function checkStatus() {
    if (!currentJobId) return;
    
    fetch(`/api/status/${currentJobId}`)
    .then(response => response.json())
    .then(data => {
        updateProgress(data.progress, data.message);
        
        if (data.status === 'completed') {
            stopPolling();
            showResult(data.result);
        } else if (data.status === 'failed') {
            stopPolling();
            showError(data.error || 'Brief generation failed');
        }
    })
    .catch(error => {
        console.error('Status check error:', error);
    });
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

function updateProgress(percentage, message) {
    document.getElementById('progress-fill').style.width = percentage + '%';
    document.getElementById('progress-percent').textContent = percentage;
    document.getElementById('status-text').textContent = message;
}

function showResult(result) {
    document.getElementById('coda-link').href = result.coda_url;
    showSection('result-section');
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    showSection('error-section');
}

function showSection(sectionId) {
    // Hide all sections
    ['input-section', 'progress-section', 'result-section', 'error-section'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('hidden');
        }
    });
    
    // Show requested section
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.remove('hidden');
    }
}

function resetForm() {
    // Reset form
    document.getElementById('brand-url').value = '';
    document.getElementById('generate-btn').disabled = false;
    
    // Stop any ongoing polling
    stopPolling();
    currentJobId = null;
    
    // Show input section
    showSection('input-section');
    
    // Hide other sections
    ['progress-section', 'result-section', 'error-section'].forEach(id => {
        document.getElementById(id).classList.add('hidden');
    });
}

// Allow Enter key to submit
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('brand-url').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            generateBrief();
        }
    });
});