const toggle = document.getElementById('menuToggle');
const nav = document.getElementById('nav');
toggle.addEventListener('click', () => nav.classList.toggle('open'));
nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => nav.classList.remove('open')));
