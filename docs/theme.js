// Shared theme functionality for all pages

function getEffectiveTheme() {
    const attr = document.documentElement.getAttribute('data-theme');
    if (attr === 'dark' || attr === 'light') return attr;
    const systemDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return systemDark ? 'dark' : 'light';
}

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
        // no saved preference: respect system, no attribute (defaults to system)
        document.documentElement.removeAttribute('data-theme');
    }
    updateThemeToggleIcon();
}

function updateThemeToggleIcon() {
    const effective = getEffectiveTheme();
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        const useElement = toggle.querySelector('use');
        if (useElement) {
            useElement.setAttribute('href', effective === 'dark' ? '#icon-sun' : '#icon-moon');
        }
        // Update toggle state semantics
        const isDark = effective === 'dark';
        toggle.setAttribute('aria-pressed', String(isDark));
        toggle.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
    }
}

function toggleTheme() {
    const effective = getEffectiveTheme();
    const next = effective === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeToggleIcon();
}

function setupThemeToggle() {
    const theme = document.getElementById('themeToggle');
    if (theme) theme.addEventListener('click', toggleTheme);
}

// Auto-initialize theme when script loads
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupThemeToggle();
});

// Listen for system theme changes
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        // Only update if user hasn't set an explicit preference
        if (!localStorage.getItem('theme')) {
            updateThemeToggleIcon();
        }
    });
}
