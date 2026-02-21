document.addEventListener('DOMContentLoaded', function () {
    var mobileMenuButton = document.getElementById('mobile-menu-button');
    var mobileMenu = document.getElementById('mobile-menu');

    mobileMenuButton.addEventListener('click', function () {
        var isHidden = !mobileMenu.classList.contains('visible');
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
            var item = e.target.closest('.dropdown-item');
            var category = item.getAttribute('data-category');
            var blogId = item.getAttribute('data-id');
            console.log('Clicked blog:', { category: category, blogId: blogId });
        }
    });

    document.addEventListener('click', function (e) {
        if (e.target.closest('.know-more-item')) {
            var item = e.target.closest('.dropdown-container');
            var category = item.getAttribute('data-category');
            console.log('Know More clicked for:', category);
        }
    });

    if (mobileMenu) {
        mobileMenu.addEventListener('click', function (e) {
            var toggle = e.target.closest('.accordion-toggle');
            if (!toggle) return;

            e.preventDefault();
            var content = toggle.nextElementSibling;
            var isCurrentlyOpen = toggle.getAttribute('aria-expanded') === 'true';

            mobileMenu.querySelectorAll('.accordion-toggle').forEach(function (otherToggle) {
                if (otherToggle !== toggle) {
                    otherToggle.setAttribute('aria-expanded', 'false');
                    var otherContent = otherToggle.nextElementSibling;
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
                var menuRect = mobileMenu.getBoundingClientRect();
                if (menuRect.bottom < 0) {
                    mobileMenu.classList.remove('visible', 'slide-down');
                    mobileMenuButton.classList.remove('hamburger-active');
                    document.body.style.overflow = '';
                }
            }
        });
    }

    var highFiveEmojis = document.querySelectorAll('.high-five-emoji');
    var countNumbers = document.querySelectorAll('.count-number');
    var highFiveCount = parseInt(localStorage.getItem('highFiveCount') || '521');

    function updateHighFiveDisplay() {
        countNumbers.forEach(function (numDisplay) {
            numDisplay.textContent = highFiveCount;
        });
    }

    updateHighFiveDisplay();

    highFiveEmojis.forEach(function (emoji) {
        emoji.addEventListener('click', function () {
            highFiveCount++;
            updateHighFiveDisplay();
            localStorage.setItem('highFiveCount', highFiveCount);
            emoji.style.transform = 'scale(1.2)';
            setTimeout(function () {
                emoji.style.transform = 'scale(1)';
            }, 150);
        });
    });
});
