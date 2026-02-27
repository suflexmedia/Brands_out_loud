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


    // ── Dynamic Magazine Grid ──────────────────────────────────────
    var magazineGridContainer = document.getElementById('dynamic-magazine-grid');
    var currentGridPage = 1;
    var gridPerPage = 6;

    function buildMagazineCard(mag) {
        var card = document.createElement('div');
        card.className = 'magazine-card';
        card.onclick = function () {
            window.location.href = '/magazine/' + mag.slug;
        };
        card.style.cursor = 'pointer';

        var thumb = document.createElement('div');
        thumb.className = 'magazine-card-thumb';

        var overlay = document.createElement('div');
        overlay.className = 'magazine-card-overlay';
        thumb.appendChild(overlay);

        var img = document.createElement('img');
        img.src = mag.image_url || mag.thumbnail_url || 'https://picsum.photos/1920/1080/?random=' + mag.slug;
        img.alt = mag.title || 'Magazine';
        thumb.appendChild(img);

        var title = document.createElement('div');
        title.className = 'magazine-card-title';
        title.textContent = (mag.title || 'Untitled').toUpperCase();

        card.appendChild(thumb);
        card.appendChild(title);
        return card;
    }

    function renderMagazineGrid(magazines) {
        if (!magazineGridContainer) return;
        // Clear existing content except pagination
        var existingPagination = magazineGridContainer.querySelector('.magazine-grid-pagination');
        magazineGridContainer.innerHTML = '';

        // Build rows of 3
        for (var i = 0; i < magazines.length; i += 3) {
            var row = document.createElement('div');
            row.className = 'magazine-row';
            var rowItems = magazines.slice(i, i + 3);
            for (var j = 0; j < rowItems.length; j++) {
                row.appendChild(buildMagazineCard(rowItems[j]));
            }
            magazineGridContainer.appendChild(row);
        }
    }

    function renderGridPagination(data) {
        if (!magazineGridContainer || !data.has_next) return;

        var paginationDiv = document.createElement('div');
        paginationDiv.className = 'magazine-grid-pagination';
        paginationDiv.style.textAlign = 'center';
        paginationDiv.style.marginTop = '2rem';

        var loadMoreBtn = document.createElement('button');
        loadMoreBtn.className = 'fuel-ambition-btn';
        loadMoreBtn.textContent = 'Load More Magazines';
        loadMoreBtn.style.cssText = 'padding: 0.75rem 2rem; background: #0D1030; color: white; border: none; font-family: "Oswald", sans-serif; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; cursor: pointer; transition: background 0.2s;';
        loadMoreBtn.onmouseover = function () { this.style.background = '#3B4FD4'; };
        loadMoreBtn.onmouseout = function () { this.style.background = '#0D1030'; };
        loadMoreBtn.onclick = function () {
            currentGridPage++;
            loadMagazineGrid(true);
        };

        paginationDiv.appendChild(loadMoreBtn);
        magazineGridContainer.appendChild(paginationDiv);
    }

    function loadMagazineGrid(append) {
        if (!magazineGridContainer) return;

        fetch('/admin/api/magazines/grid?page=' + currentGridPage + '&per_page=' + gridPerPage)
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (append) {
                    // Remove old pagination before appending
                    var oldPagination = magazineGridContainer.querySelector('.magazine-grid-pagination');
                    if (oldPagination) oldPagination.remove();

                    // Append new rows
                    var mags = data.magazines || [];
                    for (var i = 0; i < mags.length; i += 3) {
                        var row = document.createElement('div');
                        row.className = 'magazine-row';
                        var rowItems = mags.slice(i, i + 3);
                        for (var j = 0; j < rowItems.length; j++) {
                            row.appendChild(buildMagazineCard(rowItems[j]));
                        }
                        magazineGridContainer.appendChild(row);
                    }
                } else {
                    renderMagazineGrid(data.magazines || []);
                }
                renderGridPagination(data);
            })
            .catch(function (err) {
                console.error('Failed to load magazine grid:', err);
            });
    }

    var gridMode = magazineGridContainer ? magazineGridContainer.getAttribute('data-mode') : 'auto';
    if (gridMode === 'auto') {
        loadMagazineGrid(false);
    }

    // ── High Five Counter ────────────────────────────────────────────
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
