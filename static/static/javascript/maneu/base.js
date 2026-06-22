/**
 * 用户下拉菜单切换
 */
function toggleUserDropdown(event) {
    event.preventDefault();
    event.stopPropagation();
    const menu = document.getElementById('userDropdownMenu');
    const toggle = document.getElementById('userDropdown');
    const isOpen = menu.style.display === 'block';
    menu.style.display = isOpen ? 'none' : 'block';
    toggle.setAttribute('aria-expanded', !isOpen);
}

/**
 * 点击页面其他地方关闭下拉菜单
 */
document.addEventListener('click', function (event) {
    const menu = document.getElementById('userDropdownMenu');
    const toggle = document.getElementById('userDropdown');
    if (menu && toggle && menu.style.display === 'block') {
        if (!toggle.contains(event.target) && !menu.contains(event.target)) {
            menu.style.display = 'none';
            toggle.setAttribute('aria-expanded', 'false');
        }
    }
});

/**
 * 打开移动端菜单
 */
function openMobileMenu() {
    document.getElementById('mobileMenuPanel').classList.add('show');
    document.getElementById('mobileMenuOverlay').classList.add('show');
    document.body.style.overflow = 'hidden';
}

/**
 * 关闭移动端菜单
 */
function closeMobileMenu() {
    document.getElementById('mobileMenuPanel').classList.remove('show');
    document.getElementById('mobileMenuOverlay').classList.remove('show');
    document.body.style.overflow = '';
}

/**
 * 导航栏滚动阴影效果
 */
(function () {
    const navbar = document.getElementById('mainNavbar');
    if (!navbar) return;
    let ticking = false;
    window.addEventListener('scroll', function () {
        if (!ticking) {
            requestAnimationFrame(function () {
                if (window.scrollY > 8) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
                ticking = false;
            });
            ticking = true;
        }
    });
})();

/**
 * 根据当前URL自动高亮导航链接
 */
(function () {
    const currentPath = window.location.pathname;
    const allNavLinks = document.querySelectorAll('.nav-link-custom, .nav-link-mobile');

    allNavLinks.forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && href !== '#' && currentPath.indexOf(href.replace(/\/$/, '')) !== -1 &&
            href.replace(/\/$/, '') !== '') {
            link.classList.add('active');
        }
    });
})();

/**
 * ESC 键关闭移动端菜单
 */
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeMobileMenu();
        const userMenu = document.getElementById('userDropdownMenu');
        const userToggle = document.getElementById('userDropdown');
        if (userMenu && userMenu.style.display === 'block') {
            userMenu.style.display = 'none';
            if (userToggle) userToggle.setAttribute('aria-expanded', 'false');
        }
    }
});
