document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('message');
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const result = await response.json();
        
        messageDiv.style.display = 'block';
        if (result.success) {
            messageDiv.className = 'success';
            messageDiv.textContent = 'Login successful! Welcome to Student Portal.';
        } else {
            messageDiv.className = 'error';
            messageDiv.textContent = result.message || 'Login failed. Please try again.';
        }
    } catch (error) {
        messageDiv.style.display = 'block';
        messageDiv.className = 'error';
        messageDiv.textContent = 'Connection error. Please try again.';
    }
});