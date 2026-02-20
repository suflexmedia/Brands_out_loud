from .more_blogs import get_more_blogs_section
from .faq_section import get_faq_section
from .blog_body import get_blog_body


EMPTY_BLOG_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class= "scroll-smooth w-[29rem] md:w-[100%]">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>News Page Dev</title>
    <link rel="icon" type="image/png" href="static/icon/website_icon.png" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@phosphor-icons/web@2.0.3"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
        rel="stylesheet" />
    <link
        href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@600&family=Inter:wght@500&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,700&display=swap"
        rel="stylesheet" />
    <script>
        /* Define custom fonts in Tailwind (optional, better in tailwind.config.js) */
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        jakarta: ['"Plus Jakarta Sans"', "sans-serif"],
                        "helvetica-now": ['"Helvetica Now Display"', "sans-serif"],
                        helvetica: ['"Helvetica"', "sans-serif"],
                        "ibm-plex": ['"IBM Plex Sans"', "sans-serif"],
                        inter: ['"Inter"', "sans-serif"],
                    },
                    backgroundImage: {
                        "header-banner":
                            "url('digital-marketing-agency-website-banner-ad-template-lzytv.png')",
                        "hero-gradient":
                            "linear-gradient(0deg, rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://picsum.photos/1920/1080')", // Placeholder image used for gradient bg
                        "podcast-bg":
                            "linear-gradient(360deg, rgba(255, 255, 255, 0) 74.02%, #FFFFFF 100%), linear-gradient(180deg, rgba(255, 255, 255, 0) 61.61%, #FFFFFF 100%), url('Your paragraph text (8).png')",
                        "cta-bg":
                            "linear-gradient(0deg, rgba(0, 0, 0, 0.69), rgba(0, 0, 0, 0.69)), url('Screenshot 2024-09-18 at 9.57.41\u202FPM.png')",
                        "gradient-line":
                            "linear-gradient(90deg, #000000 0%, #9747FF 100%)",
                    },
                },
            },
        };
    </script>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const mobileMenuButton = document.getElementById('mobile-menu-button');
            const mobileMenu = document.getElementById('mobile-menu');

            mobileMenuButton.addEventListener('click', function () {
                mobileMenu.classList.toggle('hidden');
                mobileMenuButton.classList.toggle('hamburger-active');

                if (!mobileMenu.classList.contains('hidden')) {
                    mobileMenu.classList.add('slide-down');
                } else {
                    mobileMenu.classList.remove('slide-down');
                }
            });

            // Blog item click handlers
            document.addEventListener('click', function (e) {
                if (e.target.closest('.dropdown-item:not(.know-more-item)')) {
                    const item = e.target.closest('.dropdown-item');
                    const category = item.getAttribute('data-category');
                    const blogId = item.getAttribute('data-id');

                    console.log('Clicked blog:', { category, blogId });
                    // Replace with actual navigation
                    // window.location.href = `/blog/${category}/${blogId}`;
                }
            });

            // Know More click handlers
            document.addEventListener('click', function (e) {
                if (e.target.closest('.know-more-item')) {
                    const item = e.target.closest('.dropdown-container');
                    const category = item.getAttribute('data-category');

                    console.log('Know More clicked for:', category);
                    // Replace with actual navigation
                    // window.location.href = `/category/${category}`;
                }
            });

            // --- Mobile Accordion Menu Logic ---
            const mobileMenuContainer = document.getElementById('mobile-menu');
            if (mobileMenuContainer) {
                mobileMenuContainer.addEventListener('click', function (e) {
                    const toggle = e.target.closest('.accordion-toggle');
                    if (!toggle) return;

                    e.preventDefault();
                    const content = toggle.nextElementSibling;
                    const isCurrentlyOpen = toggle.getAttribute('aria-expanded') === 'true';

                    // Close all other accordions before opening a new one
                    mobileMenuContainer.querySelectorAll('.accordion-toggle').forEach(otherToggle => {
                        if (otherToggle !== toggle) {
                            otherToggle.setAttribute('aria-expanded', 'false');
                            const otherContent = otherToggle.nextElementSibling;
                            if (otherContent) otherContent.style.maxHeight = '0px';
                        }
                    });

                    // Toggle the clicked accordion
                    if (isCurrentlyOpen) {
                        toggle.setAttribute('aria-expanded', 'false');
                        content.style.maxHeight = '0px';
                    } else {
                        toggle.setAttribute('aria-expanded', 'true');
                        content.style.maxHeight = content.scrollHeight + 'px';
                    }
                });
            }

        });
    </script>
    <style>
        @media screen and (max-width: 768px) {
            .hero-text {
                font-size: 28px !important;
                line-height: 36px !important;
            }

            .article-container {
                padding-left: 20px !important;
                padding-right: 20px !important;
            }

            .toc-container {
                padding: 10px !important;
            }
        }

        @import url("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@600&family=Inter:wght@500&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,700&display=swap");

        @font-face {
            font-family: "Helvetica Now Display";
            src: local("Helvetica Neue"), local("Helvetica"), local("Arial"),
                sans-serif;
            /* Basic fallback */
            font-weight: 700;
        }

        @font-face {
            font-family: "Helvetica";
            src: local("Helvetica Neue"), local("Helvetica"), local("Arial"),
                sans-serif;
            /* Basic fallback */
            font-weight: 400;
        }

        ::-webkit-scrollbar {
            display: none;
        }

        body {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
        @media screen and (min-width: 1024px) {
            body {
                zoom: 1.145;
            }
        }

        @keyframes slideDown {
            from {
                transform: translateY(-10px);
                opacity: 0;
            }

            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .slide-down {
            animation: slideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        :root {
            --clr-dark-black: #121212;
            --clr-bdr-gray: #2a2a2a;
            --clr-white: #fff;
            --clr-primary: #9747ff;
            --clr-primary-light: #cda7ff;
            --clr-gray-800: #1e1e1e;
        }

        .mobile-menu-item {
            padding: 0.875rem 1rem;
            background: var(--clr-dark-black);
            border-bottom: solid 1px var(--clr-bdr-gray);
            color: var(--clr-white);
            cursor: pointer;
            display: flex;
            align-items: center;
            transition: background-color 0.2s ease;
        }

        .mobile-menu-item:hover {
            background-color: #1a1a1a;
        }

        .mobile-menu-item:active {
            background-color: #252525;
        }

        .item-title {
            flex-grow: 1;
            margin-left: 0.75rem;
            font-weight: 500;
        }

        .hamburger-line {
            transition: all 0.3s ease;
        }

        .hamburger-active .hamburger-line:nth-child(1) {
            transform: translateY(7px) rotate(45deg);
        }

        .hamburger-active .hamburger-line:nth-child(2) {
            opacity: 0;
        }

        .hamburger-active .hamburger-line:nth-child(3) {
            transform: translateY(-7px) rotate(-45deg);
        }

        .search-input {
            transition: all 0.2s ease;
        }

        .search-input:focus {
            box-shadow: 0 0 0 2px rgba(151, 71, 255, 0.5);
        }

        @keyframes shine {
            from {
                transform: translateX(-100%);
            }

            to {
                transform: translateX(100%);
            }
        }

        .login-btn {
            transition: all 0.2s ease;
        }

        .login-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(205, 167, 255, 0.4);
        }

        /* TOC container enhancements */
        aside .p-6 {
            scrollbar-width: thin;
            scrollbar-color: #3533cd #f5f5f5;
            scroll-behavior: smooth;
            transition: all 0.3s ease;
        }

        .toc-container {
            scrollbar-width: thin;
            scrollbar-color: #3533cd #f5f5f5;
            scroll-behavior: smooth;
            transition: all 0.3s ease;
        }

        /* Custom scrollbar for webkit browsers */
        aside .p-6::-webkit-scrollbar,
        .toc-container::-webkit-scrollbar {
            width: 6px;
        }

        aside .p-6::-webkit-scrollbar-track,
        .toc-container::-webkit-scrollbar-track {
            background: #f5f5f5;
            border-radius: 10px;
        }

        aside .p-6::-webkit-scrollbar-thumb,
        .toc-container::-webkit-scrollbar-thumb {
            background: rgba(53, 51, 205, 0.5);
            border-radius: 10px;
        }

        /* Smooth transitions for TOC links */
        .toc-link {
            transition: color 0.3s ease, font-weight 0.2s ease,
                border-color 0.3s ease;
        }

        /* Active indicator animation */
        .toc-link.text-\[\#3533CD\] {
            position: relative;
        }

        .toc-link.text-\[\#3533CD\]::after {
            content: "";
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 70%;
            border-radius: 2px;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }

            to {
                opacity: 1;
            }
        }

        /* --- UPDATED DROPDOWN STYLES --- */
        .dropdown-container {
            position: relative;
            padding-bottom: 20px;
            /* Creates an invisible area below the link for the cursor to travel over */
            margin-bottom: -20px;
            /* Negative margin to pull layout back up */
        }

        .dropdown-content {
            position: absolute;
            top: 100%;
            /* Positions the dropdown right below the parent's padding area */
            left: 50%;
            transform: translateX(-50%);
            width: 320px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            border: 1px solid #e5e7eb;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s ease, visibility 0.2s;
            z-index: 50;
            pointer-events: none;
            padding: 1rem;
        }

        .dropdown-container:hover .dropdown-content {
            opacity: 1;
            visibility: visible;
            pointer-events: auto;
        }

        .line-clamp-2 {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .dropdown-item {
            transition: all 0.2s ease;
        }

        .dropdown-item:hover {
            background-color: #f9fafb;
            transform: translateX(2px);
        }

        .dropdown-item:hover .ph-arrow-right {
            transform: translateX(2px);
            color: #3533CD;
        }

        /* --- MOBILE ACCORDION STYLES --- */
        .accordion-toggle .item-title {
            flex-grow: 1;
        }

        .accordion-icon {
            transition: transform 0.3s ease, color 0.3s ease;
        }

        .accordion-toggle[aria-expanded="true"] .accordion-icon {
            transform: rotate(180deg);
            color: white;
        }

        .accordion-content {
            background-color: #1a1a1a;
            overflow: hidden;
            max-height: 0;
            transition: max-height 0.4s cubic-bezier(0.25, 1, 0.5, 1);
        }

        .sub-menu-item {
            display: flex;
            align-items: center;
            padding: 0.5rem;
            border-radius: 0.375rem;
            transition: background-color 0.2s ease;
            color: white;
            text-decoration: none;
        }

        .sub-menu-item:hover {
            background-color: #252525;
        }

        

        /* Mobile TOC arrow styling for better touch targets */
        @media screen and (max-width: 1023px) {
            .toc-arrow {
                padding: 8px;
                margin: -8px;
                cursor: pointer;
                border-radius: 4px;
                transition: background-color 0.2s ease;
                position: relative;
                z-index: 10;
            }

            .toc-arrow:hover {
                background-color: rgba(53, 51, 205, 0.1);
            }
        }
    </style>
</head>

<body class="font-jakarta bg-white text-bol-black flex flex-col items-center w-full max-w-[1440px] mx-auto bg-white overflow-x-hidden relative">

        [[total_body]]


    <script>
        const stripSection = document.querySelector(".strip-section");
        if (stripSection) {
            const stripContent = stripSection.querySelector(".animate-marquee");
            if (stripContent && stripContent.children.length > 0) {
                const contentWidth = stripContent.scrollWidth / 2;
                const containerWidth = stripSection.offsetWidth;
                stripContent.innerHTML += stripContent.innerHTML;
            }
        }
        // Enhanced TOC with auto-scrolling functionality
        document.addEventListener("DOMContentLoaded", function () {
            const tocDesktop = document.querySelector("aside .p-6");
            const tocMobile = document.querySelector(".toc-container");
            const tocLinks = document.querySelectorAll(".toc-link");
            const sections = document.querySelectorAll("h1[id], h2[id], h3[id], p[id]");
            console.log("TOC Debug - Found sections:", sections.length);
            sections.forEach(section => {
                console.log("Section:", section.tagName, section.id);
            });
            // Colors and styles for active/inactive states
            const activeColorClass = "text-[#3533CD]";
            const inactiveColorClass = "text-gray-800";
            const activeFontWeightClass = "font-bold";
            const inactiveFontWeightClass = "font-medium";
            const activeBorderClass = "border-[#3533CD]";
            const inactiveBorderClass = "border-gray-200";        // Collapsible TOC functionality - different behavior for mobile and desktop
            const tocToggleLinks = document.querySelectorAll(
                "a[data-toggle-target]"
            );
            tocToggleLinks.forEach((link) => {
                const arrowIcon = link.querySelector(".toc-arrow");
                const textDiv = link.querySelector("div");
                // Handle arrow clicks for mobile
                if (arrowIcon) {
                    arrowIcon.addEventListener("click", function (event) {
                        event.preventDefault();
                        event.stopPropagation();
                        const targetId = link.getAttribute("data-toggle-target");
                        const targetElement = document.querySelector(targetId);
                        if (targetElement) {
                            targetElement.classList.toggle("hidden");
                            arrowIcon.classList.toggle("rotate-180");
                        }
                    });
                }
                // Handle text clicks for navigation
                if (textDiv) {
                    textDiv.addEventListener("click", function (event) {
                        const href = link.getAttribute("href");
                        if (href && href.startsWith("#")) {
                            event.preventDefault();
                            const targetElement = document.querySelector(href);
                            if (targetElement) {
                                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            }
                        }
                    });
                }
                // For desktop, maintain original behavior
                link.addEventListener("click", function (event) {
                    const isMobile = window.innerWidth < 1024;
                    if (!isMobile) {
                        const targetId = this.getAttribute("data-toggle-target");
                        const targetElement = document.querySelector(targetId);
                        if (targetElement) {
                            targetElement.classList.toggle("hidden");
                            if (arrowIcon) {
                                arrowIcon.classList.toggle("rotate-180");
                            }
                        }
                    }
                });
            });
            // Handle sub-category links (those without data-toggle-target)
            const subCategoryLinks = document.querySelectorAll('.toc-link:not([data-toggle-target])');
            subCategoryLinks.forEach((link) => {
                link.addEventListener("click", function (event) {
                    const href = this.getAttribute("href");
                    if (href && href.startsWith("#")) {
                        event.preventDefault();
                        const targetElement = document.querySelector(href);
                        if (targetElement) {
                            targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }
                });
            });
            // Enhanced scrollspy with TOC auto-scrolling
            function activateTocLink() {
                let currentSectionId = "";
                let currentParentSectionId = "";
                const scrollPosition = window.scrollY;
                const offset = 150; // Adjust based on header height
                let activeLink = null;
                // Find current section in view
                sections.forEach((section) => {
                    const sectionTop = section.offsetTop;
                    if (scrollPosition >= sectionTop - offset) {
                        currentSectionId = section.getAttribute("id");
                        // Determine parent H1 section (main section)
                        let parentH1 = null;
                        if (section.tagName === "H1") {
                            parentH1 = section;
                        } else {
                            // Find preceding H1
                            let previousElement = section.previousElementSibling;
                            while (previousElement) {
                                if (
                                    previousElement.tagName === "H1" &&
                                    previousElement.hasAttribute("id")
                                ) {
                                    parentH1 = previousElement;
                                    break;
                                }
                                previousElement = previousElement.previousElementSibling;
                            }
                            if (!parentH1) {
                                const parentDiv = section.closest("div");
                                if (parentDiv) {
                                    const h1InDiv = parentDiv.querySelector("h1[id]");
                                    if (h1InDiv) parentH1 = h1InDiv;
                                }
                            }
                        }
                        if (parentH1) {
                            currentParentSectionId = parentH1.getAttribute("id");
                        } else if (section.tagName === "H1") {
                            currentParentSectionId = currentSectionId;
                        }
                    }
                });
                // Update TOC link styles and expand sections
                tocLinks.forEach((link) => {
                    const linkHref = link.getAttribute("href");
                    const linkTargetId = linkHref ? linkHref.substring(1) : null;
                    const isH1Link = link.classList.contains("toc-h2-link"); // Note: class name is still "toc-h2-link" but represents H1 sections
                    const parentTocSection = link.closest(".toc-section");
                    const parentSectionDataId = parentTocSection
                        ? parentTocSection.dataset.sectionId
                        : null;
                    // Reset styles
                    link.classList.remove(activeFontWeightClass);
                    link.classList.add(inactiveFontWeightClass);
                    link.classList.replace(activeColorClass, inactiveColorClass);
                    // Border classes for subcategory links (H2 links)
                    if (!isH1Link) {
                        link.classList.replace(activeBorderClass, inactiveBorderClass);
                    }
                    // Highlight active link
                    if (linkTargetId === currentSectionId) {
                        link.classList.add(activeFontWeightClass);
                        link.classList.remove(inactiveFontWeightClass);
                        link.classList.replace(inactiveColorClass, activeColorClass);
                        if (!isH1Link) {
                            link.classList.replace(inactiveBorderClass, activeBorderClass);
                        }
                        activeLink = link; // Store active link for scrolling
                    }
                    // Highlight parent H1 if child is active
                    else if (
                        isH1Link &&
                        parentSectionDataId === currentParentSectionId
                    ) {
                        link.classList.add(activeFontWeightClass);
                        link.classList.remove(inactiveFontWeightClass);
                    }
                });          // Auto-expand/collapse TOC sections - disabled for mobile
                document.querySelectorAll(".toc-section").forEach((tocSection) => {
                    const sectionId = tocSection.dataset.sectionId;
                    const subcategoriesDiv =
                        tocSection.querySelector(".toc-subcategories");
                    const arrowIcon = tocSection.querySelector(".toc-arrow");
                    const isMobile = window.innerWidth < 1024;
                    if (subcategoriesDiv && arrowIcon && !isMobile) {
                        // Only auto-expand/collapse for desktop
                        if (sectionId === currentParentSectionId) {
                            // Expand current section
                            subcategoriesDiv.classList.remove("hidden");
                            arrowIcon.classList.add("rotate-180");
                        } else {
                            // Collapse other sections
                            subcategoriesDiv.classList.add("hidden");
                            arrowIcon.classList.remove("rotate-180");
                        }
                    }
                });
                // Scroll active link into view (for both mobile and desktop TOC)
                if (activeLink) {
                    // Handle desktop TOC scrolling
                    if (tocDesktop && window.innerWidth >= 1024) {
                        const linkTop = activeLink.offsetTop;
                        const tocTop = tocDesktop.scrollTop;
                        const tocHeight = tocDesktop.clientHeight;
                        // Check if link is not visible in the current view
                        if (linkTop < tocTop || linkTop > tocTop + tocHeight - 50) {
                            // Smoothly scroll to the active link
                            tocDesktop.scrollTo({
                                top: linkTop - tocHeight / 3,
                                behavior: "smooth",
                            });
                        }
                    }
                    // Handle mobile TOC scrolling
                    if (tocMobile && window.innerWidth < 1024) {
                        const linkTop = activeLink.offsetTop;
                        const tocTop = tocMobile.scrollTop;
                        const tocHeight = tocMobile.clientHeight;
                        if (linkTop < tocTop || linkTop > tocTop + tocHeight - 40) {
                            tocMobile.scrollTo({
                                top: linkTop - tocHeight / 3,
                                behavior: "smooth",
                            });
                        }
                    }
                }
            }
            // Initialize active state on load
            activateTocLink();
            // Update on scroll
            window.addEventListener("scroll", activateTocLink);
            
            // Add functionality for download and share buttons
            setupDownloadAndShareButtons();
        });
        
        function setupDownloadAndShareButtons() {
            console.log('Setting up download and share buttons');
            
            // Download PDF functionality - find buttons with download icons
            const allButtons = document.querySelectorAll('button');
            let downloadButtonsFound = 0;
            
            console.log('Found total buttons:', allButtons.length);
            
            // Check each button for download icon
            allButtons.forEach(button => {
                const downloadIcon = button.querySelector('i.ph-download');
                if (downloadIcon) {
                    console.log('Found download button, adding click listener');
                    downloadButtonsFound++;
                    button.addEventListener('click', handleDownloadClick);
                }
            });
            
            console.log('Download buttons found and configured:', downloadButtonsFound);
            
            function handleDownloadClick(e) {
                console.log('Download button clicked!');
                e.preventDefault();
                e.stopPropagation();
                
                // Get article title for filename
                const articleTitle = document.querySelector('h1')?.textContent || 'Article';
                console.log('Article title:', articleTitle);
                
                // Method 1: Try window.print() approach
                try {
                    const printWindow = window.open('', '_blank');
                    if (printWindow) {
                        const content = document.querySelector('main')?.innerHTML || document.querySelector('section')?.innerHTML || document.body.innerHTML;
                        printWindow.document.write(`
                            <html>
                                <head>
                                    <title>${articleTitle}</title>
                                    <style>
                                        @media print {
                                            body { font-family: Arial, sans-serif; margin: 40px; }
                                            h1 { color: #3533CD; border-bottom: 2px solid #3533CD; padding-bottom: 10px; }
                                            h2 { color: #333; margin-top: 30px; }
                                            p { line-height: 1.6; margin-bottom: 15px; }
                                            .toc-container, aside, .mobile-menu, header, footer, nav { display: none !important; }
                                        }
                                        body { font-family: Arial, sans-serif; margin: 40px; }
                                        h1 { color: #3533CD; border-bottom: 2px solid #3533CD; padding-bottom: 10px; }
                                        h2 { color: #333; margin-top: 30px; }
                                        p { line-height: 1.6; margin-bottom: 15px; }
                                        .toc-container, aside, .mobile-menu, header, footer, nav { display: none !important; }
                                    </style>
                                </head>
                                <body>
                                    ${content}
                                </body>
                            </html>
                        `);
                        printWindow.document.close();
                        
                        // Wait for content to load then print
                        setTimeout(() => {
                            printWindow.print();
                            printWindow.close();
                        }, 1000);
                        
                        console.log('Print window opened successfully');
                    } else {
                        console.log('Failed to open print window, trying fallback');
                        fallbackDownload(articleTitle);
                    }
                } catch (error) {
                    console.error('Print method failed:', error);
                    fallbackDownload(articleTitle);
                }
            }
            
            function fallbackDownload(articleTitle) {
                console.log('Using fallback download method');
                
                // Fallback: Create a downloadable HTML file
                const content = document.querySelector('main')?.innerHTML || document.querySelector('section')?.innerHTML || document.body.innerHTML;
                const htmlContent = `
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>${articleTitle}</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 40px; max-width: 800px; }
                                h1 { color: #3533CD; border-bottom: 2px solid #3533CD; padding-bottom: 10px; }
                                h2 { color: #333; margin-top: 30px; }
                                p { line-height: 1.6; margin-bottom: 15px; }
                                .toc-container, aside, .mobile-menu, header, footer, nav { display: none !important; }
                            </style>
                        </head>
                        <body>
                            <h1>${articleTitle}</h1>
                            ${content}
                        </body>
                    </html>
                `;
                
                const blob = new Blob([htmlContent], { type: 'text/html' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = articleTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '.html';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                console.log('HTML file download initiated');
            }
            
            // Share functionality - more specific selector
            const shareIcons = document.querySelectorAll('i.ph-share-network');
            shareIcons.forEach(icon => {
                const button = icon.closest('div');
                if (button) {
                    button.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const articleTitle = document.querySelector('h1')?.textContent || 'Check out this article';
                        const articleUrl = window.location.href;
                        const shareText = `${articleTitle} - ${articleUrl}`;
                        
                        // Check if Web Share API is supported and we're in a secure context
                        if (navigator.share && window.isSecureContext) {
                            navigator.share({
                                title: articleTitle,
                                url: articleUrl
                            }).catch(err => {
                                console.log('Share failed, falling back to clipboard');
                                fallbackToClipboard(shareText);
                            });
                        } else {
                            // Fallback: Copy to clipboard
                            fallbackToClipboard(shareText);
                        }
                    });
                }
            });
            
            function fallbackToClipboard(shareText) {
                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(shareText).then(() => {
                        showNotification('Link copied to clipboard!');
                    }).catch(() => {
                        fallbackToTwitter(shareText);
                    });
                } else {
                    fallbackToTwitter(shareText);
                }
            }
            
            function fallbackToTwitter(shareText) {
                const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
                window.open(shareUrl, '_blank');
            }
            
            function showNotification(message) {
                const notification = document.createElement('div');
                notification.textContent = message;
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #3533CD;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    z-index: 1000;
                    font-size: 14px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                `;
                document.body.appendChild(notification);
                setTimeout(() => notification.remove(), 3000);
            }
            
            // WhatsApp share functionality
            const whatsappButtons = document.querySelectorAll('img[alt="WhatsApp"]');
            whatsappButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const articleTitle = document.querySelector('h1')?.textContent || 'Check out this article';
                    const articleUrl = window.location.href;
                    const shareText = `${articleTitle} - ${articleUrl}`;
                    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(shareText)}`;
                    window.open(whatsappUrl, '_blank');
                });
            });
            
            // Instagram share functionality (opens Instagram in new tab)
            const instagramButtons = document.querySelectorAll('img[alt="Instagram"]');
            instagramButtons.forEach(button => {
                button.addEventListener('click', function() {
                    window.open('https://www.instagram.com/', '_blank');
                });
            });
        }
    </script>
</body>

</html>"""