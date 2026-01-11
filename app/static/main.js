document.querySelectorAll('.gate-toggle-btn').forEach(btn => {
    btn.onclick = function() {
        const deviceId = this.getAttribute('data-device-id');
        
        fetch(`/open-gate/${deviceId}`, { method: 'POST' });
        
        this.innerText = 'Sent';
        setTimeout(() => { this.innerText = 'Toggle Gate'; }, 2000);
    };
});