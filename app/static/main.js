document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.gate-toggle-btn').forEach(btn => {
        btn.onclick = function() {
            const deviceId = this.getAttribute('data-device-id');
            
            fetch(`/open-gate/${deviceId}`, { method: 'POST' });
            
            const originalText = this.innerText;
            this.innerText = 'Sent';
            this.disabled = true;

            setTimeout(() => { 
                this.innerText = originalText; 
                this.disabled = false;
            }, 2000);
        };
    });
    const editModal = document.getElementById('editDeviceModal');

    if (editModal) {
        editModal.addEventListener('show.bs.modal', event => {
            const button = event.relatedTarget;
        
            const deviceId = button.getAttribute('data-device-id');
            const deviceName = button.getAttribute('data-device-name');
            
            const input = document.getElementById('edit_device_name');
            if (input) {
                input.value = deviceName;
            }
            
            const form = document.getElementById('editDeviceForm');
            if (form) {
                form.action = `/devices/${deviceId}/edit`;
            }
        });
    }

});