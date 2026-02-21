document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
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

    const highFiveEmojis = document.querySelectorAll('.high-five-emoji');
    const countNumbers = document.querySelectorAll('.count-number');
    let highFiveCount = parseInt(localStorage.getItem('highFiveCount') || '521');

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

    // Strip section marquee not present in magazine page, but kept if needed
    const stripSection = document.querySelector('.strip-section');
    if (stripSection) {
        const stripContent = stripSection.querySelector('.marquee-track');
        if (stripContent && stripContent.children.length > 0) {
            stripContent.innerHTML += stripContent.innerHTML;
        }
    }
});

// Flipbook iframe parent-child communication
(function () {
    var iframeEl = document.getElementById('my-flipbook-container');
    function triggerDownload(url, filename) {
        try {
            var safeName = filename || (url ? url.split('/').pop() : 'document.pdf') || 'document.pdf';
            var proxiedUrl = window.location.origin + "/download_proxy?pdf=" + encodeURIComponent(url) + "&filename=" + encodeURIComponent(safeName);
            var a = document.createElement('a');
            a.href = proxiedUrl;
            a.download = safeName;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch (err) {
            console.error('Parent download error:', err);
        }
    }
    window.addEventListener('message', function (event) {
        try {
            if (!iframeEl || event.source !== iframeEl.contentWindow) return;
            var data = event.data || {};
            var type = data.type || data.action;
            if (type === 'download' || type === 'downloadResponse') {
                triggerDownload(data.pdfUrl, data.filename);
            }
        } catch (e) {
            console.error('Parent message handler error:', e);
        }
    });
})();
