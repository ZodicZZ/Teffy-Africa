
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        const route = item.getAttribute('data-route');
        window.location.href = route;
    });
});
const menuContainer = document.querySelector('.menu-container');
let isScrolling = false;
let startX;
let scrollLeft;

menuContainer.addEventListener('mousedown', (e) => {
    isScrolling = true;
    startX = e.pageX - menuContainer.offsetLeft;
    scrollLeft = menuContainer.scrollLeft;
});

menuContainer.addEventListener('mouseleave', () => {
    isScrolling = false;
});

menuContainer.addEventListener('mouseup', () => {
    isScrolling = false;
});

menuContainer.addEventListener('mousemove', (e) => {
    if (!isScrolling) return;
    e.preventDefault();
    const x = e.pageX - menuContainer.offsetLeft;
    const walk = (x - startX) * 2;
    menuContainer.scrollLeft = scrollLeft - walk;
});
