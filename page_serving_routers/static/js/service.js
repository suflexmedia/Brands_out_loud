document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    mobileMenuButton.addEventListener('click', function () {
        const isHidden = !mobileMenu.classList.contains('visible');
        if (isHidden) {
            mobileMenu.classList.add('visible', 'slide-down');
            mobileMenuButton.classList.add('hamburger-active');
            document.body.style.overflow = 'hidden';
        } else {
            mobileMenu.classList.remove('visible', 'slide-down');
            mobileMenuButton.classList.remove('hamburger-active');
            document.body.style.overflow = '';
        }
    });

    document.addEventListener('click', function (e) {
        if (e.target.closest('.dropdown-item:not(.know-more-item)')) {
            const item = e.target.closest('.dropdown-item');
            const category = item.getAttribute('data-category');
            const blogId = item.getAttribute('data-id');
            console.log('Clicked blog:', { category, blogId });
        }
    });

    document.addEventListener('click', function (e) {
        if (e.target.closest('.know-more-item')) {
            const item = e.target.closest('.dropdown-container');
            const category = item.getAttribute('data-category');
            console.log('Know More clicked for:', category);
        }
    });

    if (mobileMenu) {
        mobileMenu.addEventListener('click', function (e) {
            const toggle = e.target.closest('.accordion-toggle');
            if (!toggle) return;

            e.preventDefault();
            const content = toggle.nextElementSibling;
            const isCurrentlyOpen = toggle.getAttribute('aria-expanded') === 'true';

            mobileMenu.querySelectorAll('.accordion-toggle').forEach(function (otherToggle) {
                if (otherToggle !== toggle) {
                    otherToggle.setAttribute('aria-expanded', 'false');
                    const otherContent = otherToggle.nextElementSibling;
                    if (otherContent) otherContent.style.maxHeight = '0px';
                }
            });

            if (isCurrentlyOpen) {
                toggle.setAttribute('aria-expanded', 'false');
                content.style.maxHeight = '0px';
            } else {
                toggle.setAttribute('aria-expanded', 'true');
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    }

    if (mobileMenu && mobileMenuButton) {
        window.addEventListener('scroll', function () {
            if (mobileMenu.classList.contains('visible')) {
                const menuRect = mobileMenu.getBoundingClientRect();
                if (menuRect.bottom < 0) {
                    mobileMenu.classList.remove('visible', 'slide-down');
                    mobileMenuButton.classList.remove('hamburger-active');
                    document.body.style.overflow = '';
                }
            }
        });
    }
});
