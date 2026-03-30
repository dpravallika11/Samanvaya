// Add any global JS functionality here
document.addEventListener('DOMContentLoaded', () => {
    // Fade in animation on load for auth elements
    const fadeElements = document.querySelectorAll('.animate-fade-in');
    fadeElements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
