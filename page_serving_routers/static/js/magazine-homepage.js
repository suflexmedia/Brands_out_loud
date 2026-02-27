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

    var carouselTrack = document.getElementById('profilesTrack');
    var dotsContainer = document.getElementById('carouselDots');
    var carouselAutoPlay = null;
    var carouselActive = false;
    var carouselIndex = 0;
    var touchStartX = 0;
    var touchDelta = 0;

    function goToSlide(index) {
        var cards = carouselTrack ? carouselTrack.querySelectorAll('.profile-card') : [];
        var total = cards.length;
        carouselIndex = (index + total) % total;
        carouselTrack.style.transform = 'translateX(-' + (carouselIndex * 100) + '%)';
        var dots = dotsContainer ? dotsContainer.querySelectorAll('.carousel-dot') : [];
        dots.forEach(function (dot, i) {
            dot.classList.toggle('active', i === carouselIndex);
        });
    }

    function buildDots(total) {
        if (!dotsContainer) return;
        dotsContainer.innerHTML = '';
        for (var i = 0; i < total; i++) {
            var btn = document.createElement('button');
            btn.className = 'carousel-dot' + (i === 0 ? ' active' : '');
            btn.setAttribute('aria-label', 'Go to slide ' + (i + 1));
            btn.setAttribute('data-index', i);
            btn.addEventListener('click', function () {
                goToSlide(parseInt(this.getAttribute('data-index')));
                resetAutoPlay();
            });
            dotsContainer.appendChild(btn);
        }
    }

    function resetAutoPlay() {
        clearInterval(carouselAutoPlay);
        var cards = carouselTrack ? carouselTrack.querySelectorAll('.profile-card') : [];
        carouselAutoPlay = setInterval(function () {
            goToSlide(carouselIndex + 1);
        }, 4000);
    }

    function initCarousel() {
        if (!carouselTrack || !dotsContainer) return;
        var cards = carouselTrack.querySelectorAll('.profile-card');
        if (cards.length === 0) return;

        carouselIndex = 0;
        carouselTrack.style.transform = 'translateX(0)';
        buildDots(cards.length);
        resetAutoPlay();

        carouselTrack.addEventListener('touchstart', function (e) {
            touchStartX = e.touches[0].clientX;
            clearInterval(carouselAutoPlay);
        }, { passive: true });

        carouselTrack.addEventListener('touchend', function (e) {
            touchDelta = e.changedTouches[0].clientX - touchStartX;
            if (Math.abs(touchDelta) > 40) {
                goToSlide(touchDelta < 0 ? carouselIndex + 1 : carouselIndex - 1);
            }
            resetAutoPlay();
        }, { passive: true });

        carouselActive = true;
    }

    function destroyCarousel() {
        if (!carouselActive) return;
        clearInterval(carouselAutoPlay);
        if (carouselTrack) carouselTrack.style.transform = '';
        if (dotsContainer) dotsContainer.innerHTML = '';
        carouselActive = false;
    }

    function handleCarouselOnResize() {
        if (window.innerWidth < 768) {
            if (!carouselActive) initCarousel();
        } else {
            destroyCarousel();
        }
    }

    handleCarouselOnResize();
    window.addEventListener('resize', handleCarouselOnResize);


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
