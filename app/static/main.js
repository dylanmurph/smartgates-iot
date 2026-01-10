const btn = document.getElementById('gate-toggle-btn');
if (btn) {
    btn.onclick = () => fetch('/open-gate', { method: 'POST' });
}