def get_faq_section():
    return """
    <style>
    /* --- Minimal FAQ Styles --- */
    .faq-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .faq-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 80px;
        align-items: start;
    }
    
    .faq-header {
        position: sticky;
        top: 100px;
    }
    
    .faq-badge {
        display: inline-block;
        background: #f3f4f6;
        color: #6b7280;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 24px;
        border: 1px solid #6b7280;
    }
    
    .faq-title {
        font-size: 48px;
        font-weight: 400;
        line-height: 1.1;
        color: #1a1a1a;
        margin: 0 0 24px 0;
    }
    
    .faq-description {
        font-size: 18px;
        line-height: 1.6;
        color: #6b7280;
        margin-bottom: 32px;
    }
    
    .faq-cta {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #1a1a1a;
        font-size: 16px;
        font-weight: 500;
        text-decoration: none;
        padding: 12px 20px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        transition: all 0.2s ease;
        background: white;
    }
    
    .faq-cta:hover {
        border-color: #3533CD;
        background: #fafbff;
    }
    
    .faq-cta svg {
        width: 16px;
        height: 16px;
    }
    
    .faq-list {
        border-radius: 12px;
        overflow: hidden;
    }
    
    .faq-item {
        border-bottom: 1px solid #6b7280;
    }
    
    .faq-item:last-child {
        border-bottom: none;
    }
    
    .faq-toggle {
        width: 100%;
        padding: 24px;
        background: none;
        border: none;
        text-align: left;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        transition: background-color 0.2s ease;
    }
    
    
    .faq-question {
        font-size: 16px;
        font-weight: 500;
        color: #1a1a1a;
        line-height: 1.5;
        margin: 0;
    }
    
    .faq-icon {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        transition: transform 0.2s ease;
    }
    
    .faq-toggle[aria-expanded="true"] .faq-icon {
        transform: rotate(180deg);
    }
    
    .faq-icon svg {
        width: 16px;
        height: 16px;
        color: #6b7280;
    }
    
    .faq-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
    }
    
    .faq-answer {
        padding: 0 24px 24px 24px;
        color: #6b7280;
        line-height: 1.6;
        font-size: 15px;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .faq-grid {
            grid-template-columns: 1fr;
            gap: 48px;
        }
        
        .faq-header {
            position: static;
        }
        
        .faq-title {
            font-size: 36px;
        }
        
        .faq-description {
            font-size: 16px;
        }
        
        .faq-toggle {
            padding: 20px;
        }
        
        .faq-answer {
            padding: 0 20px 20px 20px;
        }
    }
    </style>

    <!-- ========== Minimal FAQ Section Start ========== -->
    <section class="faq-container py-4" id="faq">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="faq-grid">
                <!-- Left Column - Header -->
                <div class="faq-header">
                    <h2 class="faq-title">This is the start of something new</h2>
                    <p class="faq-description">
                        Managing a small business today is already tough. Avoid further complications by ditching outdated, tedious trade methods. Our goal is to streamline SMB trade, making it easier and faster than ever.
                    </p>
                    <a href="#contact" class="faq-cta">
                        <span>Any questions? Reach out</span>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M7 17L17 7M17 7H7M17 7V17"/>
                        </svg>
                    </a>
                </div>
                
                <!-- Right Column - FAQ Items -->
                <div class="faq-list" id="faq-accordion">
                    <!-- FAQ Item 1 -->
                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">What is Brands Out Loud?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                Brands Out Loud is a premier digital media platform dedicated to providing in-depth analysis, insightful articles, and the latest news on business, technology, startups, and global trends. We focus on the stories that shape our future, with a special emphasis on innovation in the GCC region and beyond.
                            </div>
                        </div>
                    </div>

                    <!-- FAQ Item 2 -->
                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">Who is the content for?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                Our content is created for forward-thinkers, entrepreneurs, business leaders, tech enthusiasts, and anyone curious about the forces driving modern economies. Whether you're a startup founder, a C-suite executive, or an aspiring innovator, you'll find valuable perspectives here.
                            </div>
                        </div>
                    </div>

                    <!-- FAQ Item 3 -->
                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">Can I contribute an article to Brands Out Loud?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                We are always open to collaborating with industry experts and thought leaders. If you have a unique perspective or a compelling story to share, please visit our 'Write for Us' page for submission guidelines. We look for original, well-researched, and insightful content that aligns with our core topics.
                            </div>
                        </div>
                    </div>

                    <!-- FAQ Item 4 -->
                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">How do I subscribe to the newsletter?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                Subscribing is easy! You can find the newsletter subscription form in the footer of our website. Just enter your email address and click "Subscribe" to receive our latest articles, special reports, and event invitations directly in your inbox.
                            </div>
                        </div>
                    </div>

                    <!-- FAQ Item 5 -->
                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">What topics do you cover?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                We cover a wide range of topics including business strategy, technology trends, startup ecosystem, digital transformation, leadership insights, and market analysis with a focus on the GCC region and global markets.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <script>
    // --- FAQ Accordion Logic ---
    document.addEventListener('DOMContentLoaded', function() {
        const faqAccordion = document.getElementById('faq-accordion');
        if (!faqAccordion) return;

        faqAccordion.addEventListener('click', function (e) {
            const toggle = e.target.closest('.faq-toggle');
            if (!toggle) return;

            const item = toggle.closest('.faq-item');
            const content = item.querySelector('.faq-content');
            const isExpanded = toggle.getAttribute('aria-expanded') === 'true';

            // Close all other items
            faqAccordion.querySelectorAll('.faq-item').forEach(otherItem => {
                if (otherItem !== item) {
                    const otherToggle = otherItem.querySelector('.faq-toggle');
                    const otherContent = otherItem.querySelector('.faq-content');
                    
                    otherToggle.setAttribute('aria-expanded', 'false');
                    otherContent.style.maxHeight = '0px';
                }
            });

            // Toggle current item
            if (isExpanded) {
                toggle.setAttribute('aria-expanded', 'false');
                content.style.maxHeight = '0px';
            } else {
                toggle.setAttribute('aria-expanded', 'true');
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    });
    </script>
    <!-- ========== Minimal FAQ Section End ========== -->
    """