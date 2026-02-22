from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from typing import Optional
import json
import os
import time
from database_handler.connection import db_handler
from PAGE_SERVING_ROUTERS.routers.navbar_fetcher import get_navbar_data

router = APIRouter()

blog_cache = {
    "data": None,
    "expires_at": 0
}
CACHE_TTL = 300


async def getHeader():
    return """
    <style>
      .header * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 2.25vw 4.75vw;
        background-color: #fff;
        font-family: 'Plus Jakarta Sans', sans-serif;
        height: 6vh;
        gap: 0.625vw;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        box-sizing: border-box;
        z-index: 1000;
        margin: 0;
        position: relative;
        box-shadow: 0 0.68vw 4.83vw 0 #a2a2a2;
      }

      .header .logo img {
        height: 7vh;
      }

      .header .nav-links {
        display: flex;
        gap: 2.5vw;
        align-items: center;
      }

      .header .nav-links a {
        text-decoration: none;
        color: #595959;
        font-size: 1.1vw;
        font-weight: 500;
      }

      .header .nav-links a.active {
        color: #3533CD;
        font-weight: 700;
      }

      .header .nav-links a:hover {
        color: #3533CD;
      }

      .header .hamburger {
        display: none;
        flex-direction: column;
        gap: 5px;
        cursor: pointer;
        z-index: 1001;
      }

      .header .hamburger span {
        width: 25px;
        height: 3px;
        background-color: #000;
        transition: all 0.3s ease;
      }

      .header .hamburger.active span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 4px);
      }

      .header .hamburger.active span:nth-child(2) {
        opacity: 0;
      }

      .header .hamburger.active span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -7px);
      }

      @media (max-width: 1024px) {
        .header .nav-links {
          gap: 1.5vw;
        }

        .header .nav-links a {
          font-size: 1.4vw;
        }
      }

      @media (max-width: 768px) {
        .header {
          padding: 4vw 4vw !important;
          height: 12vh !important;
          justify-content: center !important;
          position: relative !important;
          overflow: visible !important;
          margin: 0 !important;
          width: 100% !important;
          max-width: 100vw !important;
          box-sizing: border-box !important;
          display: flex !important;
          align-items: center !important;
        }

        .header .logo {
          position: absolute !important;
          left: 50% !important;
          transform: translateX(-50%) !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
        }

        .header .logo img {
          height: 6vh !important;
          width: auto !important;
          object-fit: contain !important;
        }

        .header .nav-links {
          position: fixed !important;
          top: 12vh !important;
          left: -100% !important;
          width: 100vw !important;
          height: calc(100vh - 12vh) !important;
          background-color: #fff !important;
          flex-direction: column !important;
          align-items: center !important;
          justify-content: flex-start !important;
          padding-top: 5vh !important;
          gap: 4vh !important;
          transition: left 0.3s ease !important;
          z-index: 999 !important;
          overflow-y: auto !important;
        }

        .header .nav-links.active {
          left: 0 !important;
        }

        .header .nav-links a {
          font-size: 5vw !important;
          padding: 2vh 0 !important;
          width: 80% !important;
          text-align: center !important;
        }

        .header .hamburger {
          display: flex !important;
          position: absolute !important;
          right: 4vw !important;
          top: 50% !important;
          transform: translateY(-50%) !important;
          z-index: 1001 !important;
        }
      }

      @media (max-width: 480px) {
        .header {
          padding: 3vw 4vw !important;
          height: 10vh !important;
          box-shadow: none;
          margin: 0 !important;
          width: 100% !important;
          max-width: 100vw !important;
        }
      }
    </style>

    <header class="header">
      <div class="logo">
        <a href="/"><img src="/static/images/header_logo.png" alt="Brands Out Loud Logo" width="120" height="60"></a>
      </div>
      <nav class="nav-links">
        <a href="/">Home</a>
        <a href="/magazine">Magazine</a>
        <a href="/business">Business</a>
        <a href="/technology">Technology</a>
        <a href="/gcc">GCC</a>
        <a href="/sustainability">Sustainability</a>
        <a href="/semiconductor">Semiconductor</a>
        <a href="/login" style="background-color:#C4C3FF;color:#0D0D0D;padding:0.5vh 1.5vw;border-radius:0.3vw;font-weight:700;white-space:nowrap;">Login / Register</a>
      </nav>
      <div class="hamburger">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </header>

    <script>
      (function() {
        setTimeout(function() {
          const hamburger = document.querySelector('.header .hamburger');
          const navLinks = document.querySelector('.header .nav-links');

          if (hamburger && navLinks) {
            hamburger.addEventListener('click', function() {
              hamburger.classList.toggle('active');
              navLinks.classList.toggle('active');
            });

            const links = navLinks.querySelectorAll('a');
            links.forEach(link => {
              link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
              });
            });
          }
        }, 0);
      })();
    </script>
  """


async def getFooter():
    return """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
      .footer * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      .footer {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 8vh 5vw 4vh 5vw;
        background-color: #0D0D0D;
        font-family: 'Plus Jakarta Sans', sans-serif;
        gap: 4vh;
        width: 100%;
        max-width: 100vw;
        box-sizing: border-box;
        overflow-x: hidden;
        color: #fff;
      }

      .footer .footer-content {
        display: flex;
        justify-content: space-around;
        width: 95vw;
        align-items: flex-start;
        padding: 0 5vw;
      }

      .footer .footer-section {
        display: flex;
        flex-direction: column;
        gap: 1.5vh;
      }

      .footer .footer-section h3 {
        font-size: 1.3vw;
        margin-bottom: 1vh;
        color: #fff;
      }

      .footer .footer-section a,
      .footer .footer-section p {
        text-decoration: none;
        color: #B8C2CE;
        font-size: 1vw;
        transition: color 0.2s ease;
      }

      .footer .footer-section a:hover {
        color: #C4C3FF;
      }

      .footer .footer-section.cta {
        border-right: 3px solid #3533CD;
        padding-right: 2vw;
      }

      .footer .footer-section.cta h2 {
        font-size: 2vw;
        color: #C4C3FF;
      }

      .footer .footer-section.cta .button {
        background-color: #3533CD;
        color: #fff;
        padding: 1.5vh 2vw;
        border-radius: 0.5vw;
        text-align: center;
        font-size: 1.1vw;
        text-decoration: none;
        display: inline-block;
        transition: transform 0.3s ease, background-color 0.3s ease;
      }

      .footer .footer-section.cta .button:hover {
        transform: scale(1.05);
        background-color: #4542e0;
      }

      .footer .social-links {
        display: flex;
        gap: 1vw;
      }

      .footer .social-links a {
        color: #B8C2CE;
        transition: color 0.2s ease;
      }

      .footer .social-links a:hover {
        color: #C4C3FF;
      }

      .footer .social-links svg {
        width: 1.8vw;
        height: 1.8vw;
        fill: currentColor;
      }

      .footer .footer-bottom {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2vh;
        padding-top: 3vh;
        width: 100%;
        border-top: 1px solid #2a2a2a;
      }

      .footer .footer-logo img {
        height: 10vh;
      }

      .footer .copyright {
        font-size: 0.9vw;
        color: #B8C2CE;
      }

      .footer .copyright p {
        font-size: 0.9vw;
        color: #B8C2CE;
      }

      @media (max-width: 768px) {
        .footer {
          padding: 8vh 4vw 6vw 4vw !important;
          margin: 0 !important;
          width: 100% !important;
          max-width: 100vw !important;
          box-sizing: border-box !important;
        }

        .footer .footer-content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-template-rows: auto auto auto;
          gap: 6vh 6vw;
          padding: 0 !important;
          width: 100% !important;
          margin: 0 !important;
        }

        .footer .footer-section.cta {
          grid-column: 1 / -1;
          border-right: none;
          padding-right: 0;
          text-align: center;
        }

        .footer .footer-section {
          text-align: left;
          width: 100%;
        }

        .footer .footer-section h3 {
          font-size: 5vw;
          margin-bottom: 2vh;
        }

        .footer .footer-section a,
        .footer .footer-section p {
          font-size: 4vw;
        }

        .footer .footer-section.cta h2 {
          font-size: 8vw;
        }

        .footer .footer-section.cta .button {
          font-size: 4vw;
          padding: 2vh 6vw;
          border-radius: 2vw;
          max-width: 60vw;
          margin: 0 auto;
        }

        .footer .social-links {
          justify-content: flex-start;
          gap: 4vw;
        }

        .footer .social-links svg {
          width: 8vw;
          height: 8vw;
        }

        .footer .footer-logo img {
          height: 8vh;
        }

        .footer .copyright,
        .footer .copyright p {
          font-size: 3.5vw;
          text-align: center;
        }
      }
    </style>

    <footer class="footer">
      <div class="footer-content">
        <div class="footer-section cta">
          <h2>Explore the latest<br>insights & stories</h2>
          <a href="/" class="button">Visit Homepage</a>
        </div>
        <div class="footer-section">
          <h3>Quick Links</h3>
          <a href="/">Home</a>
          <a href="/magazine">Magazine</a>
          <a href="/business">Business</a>
          <a href="/technology">Technology</a>
        </div>
        <div class="footer-section">
          <h3>Categories</h3>
          <a href="/gcc">GCC</a>
          <a href="/sustainability">Sustainability</a>
          <a href="/semiconductor">Semiconductor</a>
        </div>
        <div class="footer-section social-section">
          <h3>Social Links</h3>
          <div class="social-links">
            <a href="#" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
              <svg fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
            </a>
            <a href="#" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
              <svg fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
            </a>
            <a href="#" target="_blank" rel="noopener noreferrer" aria-label="X (Twitter)">
              <svg fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>
            </a>
            <a href="#" target="_blank" rel="noopener noreferrer" aria-label="YouTube">
              <svg fill="currentColor" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            </a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <div class="footer-logo">
          <a href="/"><img src="/static/images/header_logo.png" alt="Brands Out Loud Logo" loading="lazy" width="150" height="100"></a>
        </div>
        <div class="copyright">
          <p>&copy; 2025 BRANDSOUTLOUD All Rights Reserved</p>
        </div>
      </div>
    </footer>
  """


async def get_faq_section():
    return """
    <style>
    .faq-container {
        font-family: 'Plus Jakarta Sans', sans-serif;
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
        background: #fafaff;
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

    <section class="faq-container py-4" id="faq">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="faq-grid">
                <div class="faq-header">
                    <h2 class="faq-title">Frequently Asked Questions</h2>
                    <p class="faq-description">
                        Find answers to common questions about Brands Out Loud's content, insights, and how we cover the latest in business and technology.
                    </p>
                    <a href="/" class="faq-cta">
                        <span>Explore more on our homepage</span>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M7 17L17 7M17 7H7M17 7V17"/>
                        </svg>
                    </a>
                </div>
                
                <div class="faq-list" id="faq-accordion">
                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">What topics does Brands Out Loud cover?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                We cover a wide range of topics including Business, Technology, GCC, Sustainability, and Semiconductor industries. Our articles provide in-depth insights, trends, and analysis to keep you informed about the latest developments.
                            </div>
                        </div>
                    </div>

                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">How often is new content published?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                We publish fresh content regularly, ensuring our readers always have access to the latest insights and stories across all our categories. Subscribe to our newsletter to stay updated.
                            </div>
                        </div>
                    </div>

                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">Can I contribute articles to Brands Out Loud?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                Yes! We welcome contributions from industry experts and thought leaders. Reach out to us through the homepage to learn more about our guest contribution guidelines and editorial process.
                            </div>
                        </div>
                    </div>

                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">Is the content free to read?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                All our blog articles are completely free to read. We also offer a downloadable PDF option for each article so you can save and read content offline at your convenience.
                            </div>
                        </div>
                    </div>

                    <div class="faq-item">
                        <button type="button" class="faq-toggle" aria-expanded="false">
                            <h3 class="faq-question">How can I advertise with Brands Out Loud?</h3>
                            <div class="faq-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M6 9l6 6 6-6"/>
                                </svg>
                            </div>
                        </button>
                        <div class="faq-content">
                            <div class="faq-answer">
                                We offer various advertising opportunities for brands looking to reach our engaged audience. Visit our "Advertise With Us" page or contact us directly for partnership details and media kit information.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const faqAccordion = document.getElementById('faq-accordion');
        if (!faqAccordion) return;

        faqAccordion.addEventListener('click', function (e) {
            const toggle = e.target.closest('.faq-toggle');
            if (!toggle) return;

            const item = toggle.closest('.faq-item');
            const content = item.querySelector('.faq-content');
            const isExpanded = toggle.getAttribute('aria-expanded') === 'true';

            faqAccordion.querySelectorAll('.faq-item').forEach(otherItem => {
                if (otherItem !== item) {
                    const otherToggle = otherItem.querySelector('.faq-toggle');
                    const otherContent = otherItem.querySelector('.faq-content');
                    
                    otherToggle.setAttribute('aria-expanded', 'false');
                    otherContent.style.maxHeight = '0px';
                }
            });

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
    """


async def get_cards(other_blogs: list):
    """Generate cards for other blogs."""
    cards_html = []
    for blog in other_blogs[:10]:
        blog_content = blog.get('blogContent', {})
        if isinstance(blog_content, str):
            try:
                blog_content = json.loads(blog_content)
            except json.JSONDecodeError:
                blog_content = {}
        
        image_url = blog_content.get('mainImageUrl', 'https://picsum.photos/seed/default/800/400')
        image_alt = blog_content.get('mainImageAlt', 'Blog Image')
        title = blog_content.get('blogTitle', 'Untitled')
        summary = blog_content.get('blogSummary', '')
        author = "Brands Out Loud"
        
        created_at = blog.get('created_at')
        if created_at:
            if hasattr(created_at, 'strftime'):
                date = created_at.strftime('%b %d, %Y')
            else:
                date = str(created_at)
        else:
            date = ''

        card_html = f"""<a href="/blog/{blog.get('slug', '')}" class="flex related-blog-card">
                <div class="card bg-white rounded-xl shadow-md overflow-hidden flex flex-col flex-1 hover:shadow-lg transition-shadow duration-300">
                    <div class="h-48 overflow-hidden flex-shrink-0">
                        <img src="{image_url}" alt="{image_alt}" class="w-full h-full object-cover" loading="lazy" width="400" height="200">
                    </div>
                    <div class="p-6 flex flex-col flex-grow">
                        <h3 class="text-xl font-bold text-gray-800 mb-2">{title}</h3>
                        <p class="text-gray-600 mb-4 flex-grow">{summary}</p>
                        <div class="flex items-center text-sm text-gray-500 mt-auto">
                            <span>{author}</span>
                            <span class="mx-2">&bull;</span>
                            <span>{date}</span>
                        </div>
                    </div>
                </div>
            </a>"""
        cards_html.append(card_html)
    
    return "\n".join(cards_html)


async def get_more_blogs_section(data: dict, other_blogs: list):
    template = r"""
    <style>
        .more_blogs {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .card {
            transition: transform 0.2s ease-in-out;
        }
        .card:hover {
            transform: translateY(-4px);
        }
        .see-more-btn {
            transition: all 0.3s ease;
            background-color: #3533CD;
        }
        .see-more-btn:hover {
            background-color: #2821a8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(53, 51, 205, 0.3);
        }
        
        .related-blogs-carousel-container {
            width: 100%;
            overflow: hidden;
            position: relative;
        }
        .related-blogs-carousel-wrapper {
            overflow: hidden;
        }
        .related-blogs-carousel {
            display: flex;
            gap: 1.5rem;
            transition: transform 0.5s ease-in-out;
            padding: 5px;
        }
        .related-blog-card {
            flex: 0 0 calc((100% - 3rem) / 3);
        }
        
        .related-carousel-arrow {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background-color: rgba(255, 255, 255, 0.8);
            border: 1px solid #ddd;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 10;
            transition: background-color 0.2s;
        }
        .related-carousel-arrow:hover {
            background-color: white;
        }
        .related-carousel-arrow.left {
            left: 10px;
        }
        .related-carousel-arrow.right {
            right: 10px;
        }
        .related-carousel-arrow svg {
            width: 20px;
            height: 20px;
        }
        
        @media (max-width: 1024px) {
            .related-blog-card {
                flex: 0 0 calc((100% - 1.5rem) / 2);
            }
        }
        @media (max-width: 768px) {
            .related-blog-card {
                flex: 0 0 100%;
            }
        }
    </style>
    
    <section class="py-12 px-4 more_blogs">
        <hr class="border-t border-black my-8 md:my-12 w-full md:w-[90%] lg:w-[80rem] mx-auto" />
        <div class="max-w-6xl mx-auto">
            <h2 class="text-4xl font-serif text-center mb-10 text-gray-800">Related Articles and Topics</h2>
            
            <div class="related-blogs-carousel-container">
                <button class="related-carousel-arrow left" id="related-carousel-arrow-left" aria-label="Previous related articles">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
                </button>
                <div class="related-blogs-carousel-wrapper">
                    <div class="related-blogs-carousel" id="related-blogs-carousel">
                        [[cards]]
                    </div>
                </div>
                <button class="related-carousel-arrow right" id="related-carousel-arrow-right" aria-label="Next related articles">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>
                </button>
            </div>

            <div class="flex justify-center mt-8">
                <a href="/" class="see-more-btn px-8 py-3 text-white font-medium rounded-lg inline-flex items-center gap-2">
                    See More Articles
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </a>
            </div>
        </div>
    </section>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const carousel = document.getElementById('related-blogs-carousel');
        if (!carousel) return;
        const items = carousel.querySelectorAll('.related-blog-card');
        const totalItems = items.length;
        const leftArrow = document.getElementById('related-carousel-arrow-left');
        const rightArrow = document.getElementById('related-carousel-arrow-right');
        function getVisibleCards() {
            if (window.innerWidth >= 1024) return 3;
            if (window.innerWidth >= 768) return 2;
            return 1;
        }
        function checkCarouselState() {
            const visibleCards = getVisibleCards();
            if (totalItems <= visibleCards) {
                leftArrow.style.display = 'none';
                rightArrow.style.display = 'none';
                return false;
            }
            leftArrow.style.display = 'flex';
            rightArrow.style.display = 'flex';
            return true;
        }
        if (!checkCarouselState()) return;
        let currentIndex = 0;
        function updateCarousel() {
            const visibleCards = getVisibleCards();
            const cardWidth = items[0].offsetWidth;
            const gap = parseFloat(window.getComputedStyle(carousel).gap) || 0;
            const offset = -currentIndex * (cardWidth + gap);
            carousel.style.transform = 'translateX(' + offset + 'px)';
            
            const maxIndex = totalItems - visibleCards;
            leftArrow.style.display = currentIndex > 0 ? 'flex' : 'none';
            rightArrow.style.display = currentIndex < maxIndex ? 'flex' : 'none';
        }
        function showNext() {
            const visibleCards = getVisibleCards();
            const maxIndex = totalItems - visibleCards;
            if (currentIndex < maxIndex) {
                currentIndex++;
                updateCarousel();
            }
        }
        function showPrev() {
            if (currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            }
        }
        leftArrow.addEventListener('click', showPrev);
        rightArrow.addEventListener('click', showNext);
        window.addEventListener('resize', () => {
            currentIndex = 0;
            checkCarouselState();
            updateCarousel();
        });
        updateCarousel();
    });
    </script>
    """
    cards_html = await get_cards(other_blogs)
    return template.replace("[[cards]]", cards_html)


async def get_blog_hero_section(data: dict):
    return f"""
    <style>
        @media (max-width: 768px) {{
            .mobile-breadcrumb {{
                margin-left: 0 !important;
                padding-left: 4vw !important;
                padding-right: 4vw !important;
                width: 100% !important;
                box-sizing: border-box !important;
                display: flex !important;
                justify-content: center !important;
            }}
            .mobile-breadcrumb .text-sm {{
                display: flex !important;
                justify-content: center !important;
                width: 100% !important;
            }}
            .mobile-breadcrumb .font-jakarta {{
                justify-content: center !important;
            }}
            .mobile-hero-article {{
                max-width: 100% !important;
                width: 100% !important;
                margin: 0 auto !important;
                padding: 0 !important;
            }}
            .mobile-hero-content {{
                width: 100% !important;
                margin-left: auto !important;
                margin-right: auto !important;
                padding-left: 4vw !important;
                padding-right: 4vw !important;
                box-sizing: border-box !important;
            }}
        }}
    </style>
    <article class="max-w-[1200px] mx-auto px-4">
    <nav class="mb-2 text-left mobile-breadcrumb mt-2 md:mt-8" aria-label="Breadcrumb">
        <div class="text-sm text-gray-600">
            <span class="font-jakarta font-medium flex items-center flex-wrap">
                <a href="/" class="flex items-center font-bold">Home</a>
                <svg class="w-4 h-4 mx-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
                <span class="flex items-center">{data.get('blogCategory', 'General')}</span>
                <svg class="w-4 h-4 mx-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
            </span>
        </div>
    </nav>
</article>
<article class="relative mobile-hero-article max-w-[1200px] mx-auto">
    <div class="relative w-full h-[300px] md:h-[478px]">
        <div class="absolute inset-0 bg-cover bg-center"></div>
        <img src="{data.get('mainImageUrl', 'https://picsum.photos/seed/default/1200/600')}" alt="Blog main image"
            class="w-full h-full object-cover mix-blend-multiply" fetchpriority="high" width="1200" height="600" />
    </div>
    <div
        class="relative bg-white mobile-hero-content w-full max-w-[1175px] h-auto mx-auto -mt-[40px] sm:-mt-[60px] md:-mt-[76px] p-4 sm:p-6 md:p-8 z-10">
        <h1
            class="font-jakarta font-medium text-[28px] sm:text-[34px] md:text-[42px] lg:text-[50px] leading-[1.2] md:leading-[1.25] capitalize text-black mb-3 md:mb-4 text-center hero-text">
            {data.get('blogTitle', 'Untitled Blog')}
        </h1>
        <div class="flex justify-center items-center gap-2 text-center mb-4">
            <p class="font-jakarta font-normal text-[11px] sm:text-[12px] md:text-[14px] leading-[100.9%] text-black">
                {data.get('blogDate', '')} </p>
        </div>
    </div>
    <p
        class="font-jakarta font-medium text-[18px] md:text-[22px] leading-[26px] md:leading-[30px] text-[#636363] text-center max-w-[1175px] mx-auto px-2 md:px-0">
        {data.get('blogSummary', '')}
    </p>
    <hr class="border-t border-black my-8 md:my-12 w-full md:w-[90%] lg:w-[80rem] mx-auto" />
</article>"""


async def generate_mobile_toc(data):
    """Generate a mobile Table of Contents HTML from structured data."""
    toc_sections = await _generate_toc_sections(data)

    complete_toc = f"""<div class="block lg:hidden mt-8" style="padding-left: 4vw; padding-right: 4vw; margin: 0;">
            <div class="relative toc-container p-5 bg-white rounded-xl border-gray-100">
                <h2 class="text-xl font-bold text-[#3533CD] mb-4 border-b pb-3">Table of Contents</h2>
                {toc_sections}
                <div class="mt-6 space-y-4 border-t pt-5">
                    <button
                        class="w-full h-[45px] bg-[#3533CD] rounded-xl flex items-center justify-center text-white font-jakarta font-medium text-[16px] leading-[120%] hover:bg-opacity-90 transition-colors shadow-md">
                        <i class="ph ph-download mr-2"></i>Download Article as PDF
                    </button>
                    <div class="flex items-center flex-wrap gap-3">
                        <div
                            class="relative inline-flex items-center justify-center gap-2 bg-[#3533CD] rounded-xl h-[45px] px-4 cursor-pointer hover:bg-opacity-90 transition-colors shadow-md">
                            <span class="text-white font-jakarta font-medium text-[16px] leading-[120%] text-center"
                                style="width: 7rem">
                                <i class="ph ph-share-network mr-2"></i>Share
                            </span>
                        </div>
                        <a href="#" class="whatsapp-share-btn inline-flex items-center justify-center cursor-pointer hover:opacity-80 transition-opacity" target="_blank" rel="noopener noreferrer">
                            <img src="/static/images/whatsapp_logo.png" alt="Share on WhatsApp" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
                        </a>
                        <a href="#" class="insta-share-btn inline-flex items-center justify-center cursor-pointer hover:opacity-80 transition-opacity" target="_blank" rel="noopener noreferrer">
                            <img src="/static/images/insta_logo.png" alt="Share on Instagram" style="width: 40px; height: 40px; border-radius: 12px; object-fit: cover;">
                        </a>
                    </div>
                </div>
            </div>
        </div>"""

    return complete_toc


async def _generate_toc_sections(data):
    """Generate the TOC sections common to both mobile and desktop versions."""
    headers = ["h1", "h2"]
    temp_list = [item for item in data if item.get("type") in headers]

    final_product = []
    sub_list = []
    base_template = None

    for item in temp_list:
        item_type = item.get("type")
        item_id = item.get("id")
        item_content = item.get("content")

        if not item_id or not item_content:
            continue

        if item_type == "h1":
            if base_template is not None:
                sub_categories = "\n".join(sub_list) if sub_list else ""
                final_section = base_template.replace(
                    "[[sub_categories]]", sub_categories
                )
                final_product.append(final_section)

            sub_list = []
            base_template = f"""<div class="mb-3 toc-section" data-section-id="{item_id}">
                        <a href="#{item_id}"
                            data-toggle-target="#sub-{item_id}"
                            class="toc-h2-link flex items-center justify-between mt-1 mb-3 no-underline text-gray-800 hover:text-[#3533CD] transition-colors duration-200 toc-link">
                            <div class="text-base font-medium">{item_content}</div>
                            <i class="ph ph-caret-down text-xs ml-1 toc-arrow transition-transform duration-300"></i>
                        </a>
                        <div id="sub-{item_id}"
                            class="toc-subcategories hidden pl-4 mb-3 space-y-2">
                            [[sub_categories]]
                        </div>
                    </div>"""

        elif item_type == "h2":
            sub_template = f"""                            <a href="#{item_id}"
                                class="flex items-center mt-1 no-underline text-gray-600 hover:text-[#3533CD] transition-colors duration-200 toc-link border-l-2 border-gray-200 pl-3 hover:border-[#3533CD]">
                                <div class="text-sm">{item_content}</div>
                            </a>"""
            sub_list.append(sub_template)

    if base_template is not None:
        sub_categories = "\n".join(sub_list) if sub_list else ""
        final_section = base_template.replace("[[sub_categories]]", sub_categories)
        final_product.append(final_section)

    return "\n".join(final_product)


async def generate_desktop_toc(data):
    """Generate a desktop/sidebar Table of Contents HTML from structured data."""
    toc_sections = await _generate_toc_sections(data)

    complete_toc = f"""<aside class="sticky top-8 h-8rem lg:order-1 self-start md:mt-[0rem] mt-[-57rem]">
                <div class="p-6 flex flex-col w-full rounded-xl bg-white max-w-[20rem] border-gray-100 hidden lg:block overflow-y- max-h-[calc(100vh-4rem)]"
                    style="scroll-behavior: smooth">
                    <h2 class="text-2xl font-bold text-[#3533CD] mb-6 border-b pb-3">Table of Contents</h2>
                    {toc_sections}
                    <div class="mt-6 space-y-4 border-t pt-5">
                        <button
                            class="w-full h-[45px] bg-[#3533CD] rounded-xl flex items-center justify-center text-white font-jakarta font-medium text-[16px] leading-[120%] hover:bg-opacity-90 transition-colors shadow-md">
                            <i class="ph ph-download mr-2"></i>Download Article as PDF
                        </button>
                        <div class="flex items-center flex-wrap gap-3">
                            <div
                                class="relative inline-flex items-center justify-center gap-2 bg-[#3533CD] rounded-xl h-[45px] px-4 cursor-pointer hover:bg-opacity-90 transition-colors shadow-md">
                                <span class="text-white font-jakarta font-medium text-[16px] leading-[120%] text-center"
                                    style="width: 7rem">
                                    <i class="ph ph-share-network mr-2"></i>Share
                                </span>
                            </div>
                            <a href="#" class="whatsapp-share-btn inline-flex items-center justify-center cursor-pointer hover:opacity-80 transition-opacity" target="_blank" rel="noopener noreferrer">
                                <img src="/static/images/whatsapp_logo.png" alt="Share on WhatsApp" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
                            </a>
                            <a href="#" class="insta-share-btn inline-flex items-center justify-center cursor-pointer hover:opacity-80 transition-opacity" target="_blank" rel="noopener noreferrer">
                                <img src="/static/images/insta_logo.png" alt="Share on Instagram" style="width: 40px; height: 40px; border-radius: 12px; object-fit: cover;">
                            </a>
                        </div>
                    </div>
                </div>
            </aside>"""

    return complete_toc


async def get_blog_content(data: list):
    content = []
    for i in data:
        item_type = i.get("type")
        item_content = i.get("content", "")
        item_id = i.get("id", "")
        if item_type == "text":
            content.append(
                f"""<p class="font-jakarta font-medium text-[15px] md:text-[16px] leading-[26px] md:leading-[30px] text-black" >{item_content}</p>"""
            )
        elif item_type == "h1":
            content.append(
                f"""<h1 id="{item_id}" class="font-jakarta font-bold text-[28px] md:text-[36px] leading-[32px] md:leading-[40px] text-black scroll-mt-20" >{item_content}</h1>"""
            )
        elif item_type == "h2":
            content.append(
                f"""<h2 id="{item_id}" class="font-jakarta font-medium text-[22px] md:text-[28px] leading-[28px] md:leading-[30px] text-black scroll-mt-20" >{item_content}</h2>"""
            )
        elif item_type == "h3":
            content.append(
                f"""<h3  class="font-jakarta font-medium text-[20px] md:text-[24px] leading-[26px] md:leading-[28px] text-black scroll-mt-20" >{item_content}</h3>"""
            )
        elif item_type == "h4":
            content.append(
                f"""<h4  class="font-jakarta font-medium text-[18px] md:text-[22px] leading-[24px] md:leading-[26px] text-black scroll-mt-20" >{item_content}</h4>"""
            )
        elif item_type == "h5":
            content.append(
                f"""<h5  class="font-jakarta font-medium text-[16px] md:text-[20px] leading-[22px] md:leading-[24px] text-black scroll-mt-20" >{item_content}</h5>"""
            )
        elif item_type == "h6":
            content.append(
                f"""<h6  class="font-jakarta font-medium text-[14px] md:text-[18px] leading-[20px] md:leading-[22px] text-black scroll-mt-20" >{item_content}</h6>"""
            )
        elif item_type == "image":
            if isinstance(item_content, dict):
                url = item_content.get('url', '')
                alt = item_content.get('alt', 'image')
                content.append(
                    f"""<div class="w-full h-[120px] sm:h-[160px] md:h-[236px] my-8 md:my-12"><img src="{url}" alt="{alt}" class="w-full h-full object-cover"/></div>"""
                )
    content_str = "\n".join(content)
    return f"""<section class="space-y-6 md:space-y-5 text-left order-1 lg:order-2 max-w-[59vw]">{content_str}</section>"""


async def get_blog_body(data: dict):
    hero_section = await get_blog_hero_section(data)
    dynamic_sections = data.get("dynamicSections", [])
    mobile_toc = await generate_mobile_toc(dynamic_sections)
    desktop_toc = await generate_desktop_toc(dynamic_sections)
    blog_content = await get_blog_content(dynamic_sections)

    return f"""
        <style>
            @media (max-width: 768px) {{
                .mobile-blog-grid {{
                    margin-left: 0 !important;
                    margin-right: 0 !important;
                    padding: 0 4vw !important;
                    width: 100% !important;
                    box-sizing: border-box !important;
                }}
            }}
        </style>
        {hero_section}
        {mobile_toc}
        <div class="mobile-blog-grid grid grid-cols-1 lg:grid-cols-[300px_minmax(0,1fr)] gap-8 mt-4 md:mt-8 max-w-[80rem] mx-auto px-2 md:px-0">
        {desktop_toc}
        {blog_content}
        </div>

"""


async def getHomepageStyleHeader(navbar_data=None):
    """Return the homepage-style header with desktop/mobile nav and dropdowns populated from navbar_data."""
    categories = [
        {"key": "business", "label": "Business", "icon": "ph-buildings"},
        {"key": "technology", "label": "Technology", "icon": "ph-gear"},
        {"key": "gcc", "label": "Gcc", "icon": "ph-globe"},
        {"key": "sustainability", "label": "Sustainability", "icon": "ph-leaf"},
        {"key": "semiconductor", "label": "Semiconductor", "icon": "ph-cpu"},
    ]

    if navbar_data is None:
        navbar_data = {}

    desktop_dropdowns = ""
    mobile_accordions = ""

    for cat in categories:
        cat_data = navbar_data.get(cat["key"], {})
        if isinstance(cat_data, dict):
            heading = cat_data.get("heading", cat["label"])
            posts = cat_data.get("posts", [])
        else:
            heading = cat["label"]
            posts = []

        desktop_items = ""
        mobile_items = ""
        for post in posts:
            title = post.get("title", "")
            image_url = post.get("image_url", "")
            slug = post.get("slug", "")
            desktop_items += f'''
                                <a href="/blog/{slug}" class="dropdown-item" data-category="{cat['key']}" data-id="{slug}">
                                    <img src="{image_url}" alt="{title}" class="dropdown-thumb">
                                    <div>
                                        <h4 class="dropdown-item-title line-clamp-2">{title}</h4>
                                    </div>
                                </a>'''
            mobile_items += f'''
                            <a href="/blog/{slug}" class="sub-menu-item" data-category="{cat['key']}"><img
                                    src="{image_url}" alt="{title}" class="sub-menu-thumb">
                                <div class="sub-menu-text">
                                    <h4 class="sub-menu-title line-clamp-2">{title}</h4>
                                </div>
                            </a>'''

        desktop_dropdowns += f'''
                    <div class="dropdown-container" data-category="{cat['key']}">
                        <a href="/{cat['key']}" class="category-link">{cat['label']}</a>
                        <div class="dropdown-content">
                            <h3 class="dropdown-heading">{heading}</h3>
                            <div class="dropdown-list">{desktop_items}
                                <div class="dropdown-divider">
                                    <div class="know-more-item"><a href="/{cat['key']}"><span class="know-more-text">Know More</span></a><i class="ph ph-arrow-right know-more-arrow"></i></div>
                                </div>
                            </div>
                        </div>
                    </div>'''

        mobile_accordions += f'''
                <div>
                    <a href="#" class="accordion-toggle mobile-menu-item" aria-expanded="false">
                        <div class="item-inner"><i class="ph {cat['icon']}" style="color:#fff;font-size:1.125rem"></i><span class="item-title">{cat['label']}</span></div>
                        <i class="ph ph-caret-down accordion-icon"></i>
                    </a>
                    <div class="accordion-content">
                        <div class="accordion-inner">{mobile_items}
                            <div class="sub-menu-divider"><a href="/{cat['key']}" class="know-more-mobile"><span class="know-more-mobile-text">Know More</span><i class="ph ph-arrow-right know-more-mobile-arrow"></i></a></div>
                        </div>
                    </div>
                </div>'''

    return f"""
    <header class="site-header">
        <div class="desktop-header">
            <a href="/"><img src="/static/images/header_logo.png" alt="Brands Out Loud Logo" class="header-logo"></a>
            <nav class="desktop-nav">
                <div class="top-nav-links">
                    <a href="/magazine" class="top-nav-link">Magazine</a>
                    <a href="/login" class="login-btn-desktop">Login / Register</a>
                </div>
                <div class="nav-divider"></div>
                <div class="category-nav">{desktop_dropdowns}
                </div>
            </nav>
        </div>

        <div class="mobile-header">
            <button id="mobile-menu-button" class="mobile-menu-btn" aria-label="Toggle Menu">
                <span class="hamburger-line"></span>
                <span class="hamburger-line"></span>
                <span class="hamburger-line"></span>
            </button>
            <div class="mobile-logo-wrap">
                <a href="/"><img src="/static/images/header_logo.png" alt="Brands Out Loud Logo" class="mobile-logo"></a>
            </div>
            <div class="mobile-search-wrap">
                <div class="mobile-search-inner">
                    <input type="text" placeholder="Search..." class="search-input">
                    <div class="search-icon"><i class="ph ph-magnifying-glass"></i></div>
                </div>
            </div>
        </div>

        <div id="mobile-menu" class="mobile-menu">
            <div>
                <div class="mobile-auth-section">
                    <a href="/login" class="login-btn-mobile">
                        <span class="login-btn-inner"><i class="ph ph-sign-in" style="font-size:1.125rem"></i><span>Login</span></span>
                    </a>
                </div>
                <a href="/magazine" class="mobile-menu-item">
                    <div class="item-inner"><i class="ph ph-book-open" style="color:#fff;font-size:1.125rem"></i><span class="item-title">Magazine</span></div>
                </a>{mobile_accordions}
            </div>
        </div>
    </header>
    """


async def getHomepageStyleFooter():
    """Return the homepage-style footer with full navigation, social links, and newsletter."""
    return """
    <footer class="site-footer">
        <div class="footer-top-row">
            <div class="footer-logo-wrap"><a href="/">
                    <div class="footer-logo" style="background-image:url(/static/images/header_logo.png)"></div>
                </a></div>
            <div class="footer-col">
                <div class="footer-col-heading">Quick Links</div>
                <ul class="footer-col-list">
                    <li><a href="/" class="footer-col-link">Home</a></li>
                    <li><a href="#" class="footer-col-link">About Us</a></li>
                    <li><a href="#" class="footer-col-link">Careers</a></li>
                    <li><a href="#" class="footer-col-link">Web Stories</a></li>
                    <li><a href="/magazine" class="footer-col-link">Magazine</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <div class="footer-col-heading">News</div>
                <ul class="footer-col-list">
                    <li><a href="/business" class="footer-col-link">Business</a></li>
                    <li><a href="/technology" class="footer-col-link">Technology</a></li>
                    <li><a href="/gcc" class="footer-col-link">GCC</a></li>
                    <li><a href="/sustainability" class="footer-col-link">Sustainability</a></li>
                    <li><a href="/semiconductor" class="footer-col-link">Semiconductor</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-divider"></div>
        <div class="footer-bottom-row">
            <div class="footer-social-col">
                <div class="footer-social-heading">Social Links</div>
                <div class="footer-social-icons">
                    <a href="#" aria-label="Instagram" class="footer-social-link"><svg class="footer-social-svg" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" />
                        </svg></a>
                    <a href="#" aria-label="Facebook" class="footer-social-link"><svg class="footer-social-svg" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                        </svg></a>
                    <a href="#" aria-label="X (Twitter)" class="footer-social-link"><svg class="footer-social-svg" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
                        </svg></a>
                    <a href="#" aria-label="YouTube" class="footer-social-link"><svg class="footer-social-svg" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                        </svg></a>
                    <a href="#" aria-label="LinkedIn" class="footer-social-link"><svg class="footer-social-svg" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                        </svg></a>
                </div>
            </div>
            <div class="footer-advertise-col">
                <a href="/advertise_with_us" class="footer-advertise-link">Advertise With Us</a>
            </div>
            <div class="footer-newsletter-col">
                <div class="footer-newsletter-heading">Subscribe to Newsletter</div>
                <form class="footer-newsletter-form">
                    <input type="email" placeholder="Enter your email" required class="footer-newsletter-input">
                    <button type="submit" class="footer-newsletter-submit"><img src="/static/images/subscribe_button.png" alt="Subscribe"></button>
                </form>
            </div>
        </div>
        <div class="footer-copyright-wrap">
            <div class="footer-copyright">&copy; 2025 BRANDSOUTLOUD All Rights Reserved</div>
        </div>
    </footer>
    """


EMPTY_BLOG_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth w-full">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="[[[meta_description]]]" />
    <title>[[[title]]]</title>
    <link rel="icon" type="image/png" href="/static/images/header_logo.png">
    
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="preconnect" href="https://cdn.tailwindcss.com" />
    <link rel="preconnect" href="https://unpkg.com" />
    
    <link rel="stylesheet" href="/static/css/zoom.css">
    <link rel="stylesheet" href="/static/css/homepage.css">
    <style>body { visibility: hidden; } .fouc-ready { visibility: visible !important; }</style>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@phosphor-icons/web@2.0.3" defer></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    
    <script>document.addEventListener('DOMContentLoaded', function() { document.body.classList.add('fouc-ready'); });</script>
    
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
        rel="stylesheet" />
    <link
        href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@600&family=Inter:wght@500&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,700&display=swap"
        rel="stylesheet" />
    <script>
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
                },
            },
        };
    </script>
    <style>
        @media screen and (max-width: 768px) {
            html, body {
                width: 100% !important;
                max-width: 100vw !important;
                overflow-x: hidden !important;
                margin: 0 !important;
                padding: 0 !important;
            }

            .hero-text {
                font-size: 28px !important;
                line-height: 36px !important;
            }

            .article-container {
                padding-left: 4vw !important;
                padding-right: 4vw !important;
                margin: 0 !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }

            .toc-container {
                padding: 10px !important;
                margin: 0 4vw !important;
                width: calc(100% - 8vw) !important;
                box-sizing: border-box !important;
            }

            section, article, div {
                max-width: 100vw !important;
            }
        }

        @import url("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@600&family=Inter:wght@500&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,700&display=swap");

        @font-face {
            font-family: "Helvetica Now Display";
            src: local("Helvetica Neue"), local("Helvetica"), local("Arial"),
                sans-serif;
            font-weight: 700;
        }

        @font-face {
            font-family: "Helvetica";
            src: local("Helvetica Neue"), local("Helvetica"), local("Arial"),
                sans-serif;
            font-weight: 400;
        }

        ::-webkit-scrollbar {
            display: none;
        }

        body {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }

        :root {
            --clr-dark-black: #121212;
            --clr-bdr-gray: #2a2a2a;
            --clr-white: #fff;
            --clr-primary: #3533CD;
            --clr-primary-light: #C4C3FF;
            --clr-gray-800: #1e1e1e;
            --clr-bol-purple: #3533CD;
            --clr-bol-purple-light: #C4C3FF;
            --clr-bol-black: #0D0D0D;
            --clr-bol-gray: #B8C2CE;
        }

        aside .p-6 {
            scrollbar-width: thin;
            scrollbar-color: #3533CD #f5f5f5;
            scroll-behavior: smooth;
            transition: all 0.3s ease;
        }

        .toc-container {
            scrollbar-width: thin;
            scrollbar-color: #3533CD #f5f5f5;
            scroll-behavior: smooth;
            transition: all 0.3s ease;
        }

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

        .toc-link {
            transition: color 0.3s ease, font-weight 0.2s ease,
                border-color 0.3s ease;
        }

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

        .line-clamp-2 {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

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

        .download-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 5000;
            padding: 20px;
            box-sizing: border-box;
        }

        .download-modal-overlay.show {
            display: flex;
        }

        .download-modal {
            background: #FBFAF7;
            border-radius: 16px;
            padding: 32px;
            max-width: 550px;
            width: 100%;
            position: relative;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            max-height: 90vh;
            overflow-y: auto;
        }

        .download-modal-close {
            position: absolute;
            top: 16px;
            right: 16px;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #666;
            padding: 4px;
            line-height: 1;
        }

        .download-modal-close:hover {
            color: #333;
        }

        .download-modal h2 {
            font-size: 24px;
            font-weight: 400;
            color: #1a1a1a;
            margin: 0 0 24px 0;
            padding-right: 30px;
        }

        .download-form-row {
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
        }

        .download-form-field {
            flex: 1;
        }

        .download-form-field.full-width {
            width: 100%;
        }

        .download-form-field input {
            width: 100%;
            padding: 16px;
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            font-size: 14px;
            background: #f5f5f0;
            box-sizing: border-box;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .download-form-field input:focus {
            outline: none;
            border-color: #3533CD;
            box-shadow: 0 0 0 3px rgba(53, 51, 205, 0.1);
        }

        .download-form-field input::placeholder {
            color: #999;
        }

        .download-form-field label {
            display: block;
            font-size: 14px;
            color: #333;
            margin-bottom: 6px;
        }

        .download-form-field .optional {
            color: #6b5b3e;
            font-size: 12px;
        }

        .download-modal-terms {
            font-size: 13px;
            color: #555;
            line-height: 1.6;
            margin: 20px 0;
        }

        .download-modal-terms a {
            color: #3533CD;
            text-decoration: none;
        }

        .download-modal-terms a:hover {
            text-decoration: underline;
        }

        .download-modal-submit {
            background: #1a1a1a;
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }

        .download-modal-submit:hover {
            background: #333;
        }

        .download-modal-submit:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .download-form-error {
            color: #e53935;
            font-size: 12px;
            margin-top: 4px;
            display: none;
        }

        .download-form-field.error input {
            border-color: #e53935;
        }

        .download-form-field.error .download-form-error {
            display: block;
        }

        @media screen and (max-width: 600px) {
            .download-form-row {
                flex-direction: column;
                gap: 12px;
            }
            
            .download-modal {
                padding: 24px;
                margin: 10px;
            }
            
            .download-modal h2 {
                font-size: 20px;
            }
        }
    </style>
</head>

<body data-zoom-container class="font-jakarta bg-white text-bol-black w-full max-w-[100vw] mx-auto bg-white overflow-x-hidden relative" style="margin: 0; padding: 0;">

    <div class="page-wrapper" style="overflow-x: visible; overflow: visible;">
        [[header_content]]

        <main id="main-content">
            [[total_body]]
        </main>

        [[footer_content]]
    </div>


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
        document.addEventListener("DOMContentLoaded", function () {
            const tocDesktop = document.querySelector("aside .p-6");
            const tocMobile = document.querySelector(".toc-container");
            const tocLinks = document.querySelectorAll(".toc-link");
            const sections = document.querySelectorAll("h1[id], h2[id], h3[id], p[id]");
            const activeColorClass = "text-[#3533CD]";
            const inactiveColorClass = "text-gray-800";
            const activeFontWeightClass = "font-bold";
            const inactiveFontWeightClass = "font-medium";
            const activeBorderClass = "border-[#3533CD]";
            const inactiveBorderClass = "border-gray-200";
            const tocToggleLinks = document.querySelectorAll(
                "a[data-toggle-target]"
            );
            tocToggleLinks.forEach((link) => {
                const arrowIcon = link.querySelector(".toc-arrow");
                const textDiv = link.querySelector("div");
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
            function activateTocLink() {
                let currentSectionId = "";
                let currentParentSectionId = "";
                const scrollPosition = window.scrollY;
                const offset = 150;
                let activeLink = null;
                sections.forEach((section) => {
                    const sectionTop = section.offsetTop;
                    if (scrollPosition >= sectionTop - offset) {
                        currentSectionId = section.getAttribute("id");
                        let parentH1 = null;
                        if (section.tagName === "H1") {
                            parentH1 = section;
                        } else {
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
                tocLinks.forEach((link) => {
                    const linkHref = link.getAttribute("href");
                    const linkTargetId = linkHref ? linkHref.substring(1) : null;
                    const isH1Link = link.classList.contains("toc-h2-link");
                    const parentTocSection = link.closest(".toc-section");
                    const parentSectionDataId = parentTocSection
                        ? parentTocSection.dataset.sectionId
                        : null;
                    link.classList.remove(activeFontWeightClass);
                    link.classList.add(inactiveFontWeightClass);
                    link.classList.replace(activeColorClass, inactiveColorClass);
                    if (!isH1Link) {
                        link.classList.replace(activeBorderClass, inactiveBorderClass);
                    }
                    if (linkTargetId === currentSectionId) {
                        link.classList.add(activeFontWeightClass);
                        link.classList.remove(inactiveFontWeightClass);
                        link.classList.replace(inactiveColorClass, activeColorClass);
                        if (!isH1Link) {
                            link.classList.replace(inactiveBorderClass, activeBorderClass);
                        }
                        activeLink = link;
                    }
                    else if (
                        isH1Link &&
                        parentSectionDataId === currentParentSectionId
                    ) {
                        link.classList.add(activeFontWeightClass);
                        link.classList.remove(inactiveFontWeightClass);
                    }
                });
                document.querySelectorAll(".toc-section").forEach((tocSection) => {
                    const sectionId = tocSection.dataset.sectionId;
                    const subcategoriesDiv =
                        tocSection.querySelector(".toc-subcategories");
                    const arrowIcon = tocSection.querySelector(".toc-arrow");
                    const isMobile = window.innerWidth < 1024;
                    if (subcategoriesDiv && arrowIcon && !isMobile) {
                        if (sectionId === currentParentSectionId) {
                            subcategoriesDiv.classList.remove("hidden");
                            arrowIcon.classList.add("rotate-180");
                        } else {
                            subcategoriesDiv.classList.add("hidden");
                            arrowIcon.classList.remove("rotate-180");
                        }
                    }
                });
                if (activeLink) {
                    if (tocDesktop && window.innerWidth >= 1024) {
                        const linkTop = activeLink.offsetTop;
                        const tocTop = tocDesktop.scrollTop;
                        const tocHeight = tocDesktop.clientHeight;
                        if (linkTop < tocTop || linkTop > tocTop + tocHeight - 50) {
                            tocDesktop.scrollTo({
                                top: linkTop - tocHeight / 3,
                                behavior: "smooth",
                            });
                        }
                    }
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
            activateTocLink();
            window.addEventListener("scroll", activateTocLink);
            
            setupDownloadAndShareButtons();
        });
        
        function setupDownloadAndShareButtons() {
            const allButtons = document.querySelectorAll('button');
            
            allButtons.forEach(button => {
                const downloadIcon = button.querySelector('i.ph-download');
                if (downloadIcon) {
                    button.addEventListener('click', handleDownloadClick);
                }
            });
            
            function handleDownloadClick(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const articleTitle = document.querySelector('.hero-text')?.textContent?.trim() || document.querySelector('h1')?.textContent?.trim() || 'Article';
                
                const mainImage = document.querySelector('article img[src*="pexels"], article img[src*="picsum"], article img[alt]');
                const mainImageUrl = mainImage?.src || '';
                const mainImageAlt = mainImage?.alt || articleTitle;
                
                const summaryP = document.querySelector('article > p.font-jakarta.font-medium');
                const summary = summaryP?.innerHTML || '';
                
                const contentSection = document.querySelector('section.space-y-6, section.order-1');
                const bodyContent = contentSection?.innerHTML || '';
                
                pendingDownloadData = {
                    articleTitle,
                    mainImageUrl,
                    mainImageAlt,
                    summary,
                    bodyContent
                };
                
                try {
                    var token = localStorage.getItem('bol_token');
                    if (token) {
                        performDownload();
                        return;
                    }
                } catch(err) {}
                
                showDownloadModal();
            }
            
            const shareIcons = document.querySelectorAll('i.ph-share-network');
            shareIcons.forEach(icon => {
                const button = icon.closest('div');
                if (button) {
                    button.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const articleTitle = document.querySelector('h1')?.textContent || 'Check out this article';
                        const articleUrl = window.location.href;
                        const shareText = articleTitle + ' - ' + articleUrl;
                        
                        if (navigator.share && window.isSecureContext) {
                            navigator.share({
                                title: articleTitle,
                                url: articleUrl
                            }).catch(err => {
                                fallbackToClipboard(shareText);
                            });
                        } else {
                            fallbackToClipboard(shareText);
                        }
                    });
                }
            });
            
            const whatsappBtns = document.querySelectorAll('.whatsapp-share-btn');
            whatsappBtns.forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const articleTitle = document.querySelector('h1')?.textContent || 'Check out this article';
                    const articleUrl = window.location.href;
                    const whatsappUrl = 'https://api.whatsapp.com/send?text=' + encodeURIComponent(articleTitle + ' - ' + articleUrl);
                    window.open(whatsappUrl, '_blank');
                });
            });
            
            const instaBtns = document.querySelectorAll('.insta-share-btn');
            instaBtns.forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const articleUrl = window.location.href;
                    if (navigator.clipboard && window.isSecureContext) {
                        navigator.clipboard.writeText(articleUrl).then(() => {
                            showNotification('Link copied! You can now share it on Instagram.');
                        }).catch(() => {
                            window.open('https://www.instagram.com/', '_blank');
                        });
                    } else {
                        window.open('https://www.instagram.com/', '_blank');
                    }
                });
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
                const shareUrl = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent(shareText);
                window.open(shareUrl, '_blank');
            }
            
            function showNotification(message) {
                const notification = document.createElement('div');
                notification.textContent = message;
                notification.style.cssText = 'position:fixed;top:20px;right:20px;background:#3533CD;color:white;padding:10px 20px;border-radius:5px;z-index:1000;font-size:14px;box-shadow:0 2px 10px rgba(0,0,0,0.2);';
                document.body.appendChild(notification);
                setTimeout(() => notification.remove(), 3000);
            }
        }
    </script>

    <div id="downloadModalOverlay" class="download-modal-overlay">
        <div class="download-modal">
            <button class="download-modal-close" onclick="hideDownloadModal()">&times;</button>
            <h2>Download Article as PDF</h2>
            <form id="downloadForm" onsubmit="submitDownloadForm(event)">
                <div class="download-form-row">
                    <div class="download-form-field" id="firstNameField">
                        <label>First/Given name</label>
                        <input type="text" id="downloadFirstName" placeholder="Enter your first name" required>
                        <div class="download-form-error">Please enter your first name</div>
                    </div>
                    <div class="download-form-field" id="lastNameField">
                        <label>Last/Family name <span class="optional">(optional)</span></label>
                        <input type="text" id="downloadLastName" placeholder="Enter your last name">
                    </div>
                </div>
                <div class="download-form-field full-width" id="emailField" style="margin-bottom: 16px;">
                    <label>Work Email</label>
                    <input type="email" id="downloadEmail" placeholder="name@example.com" required>
                    <div class="download-form-error">Please enter a valid email address</div>
                </div>
                <div class="download-form-row">
                    <div class="download-form-field" id="companyNameField">
                        <label>Company Name <span class="optional">(optional)</span></label>
                        <input type="text" id="downloadCompanyName" placeholder="Enter your company name">
                    </div>
                    <div class="download-form-field" id="mobileNumberField">
                        <label>Mobile Number <span class="optional">(optional)</span></label>
                        <input type="text" id="downloadMobileNumber" placeholder="Enter your mobile number">
                    </div>
                </div>
                <div class="download-modal-terms">
                    By submitting this form, you agree to the processing of the submitted personal data in accordance
                    with Brands Out Loud's Privacy Policy, including the transfer of data.
                </div>
                <div class="download-modal-terms">
                    By submitting this form, you agree to receive information from Brands Out Loud related to our content, events,
                    and updates. You may unsubscribe at any time.
                </div>
                <button type="submit" class="download-modal-submit" id="downloadSubmitBtn">Download now</button>
            </form>
        </div>
    </div>

    <script>
        let pendingDownloadData = null;

        function showDownloadModal() {
            const overlay = document.getElementById('downloadModalOverlay');
            if (overlay.parentElement !== document.body) {
                document.body.appendChild(overlay);
            }
            overlay.classList.add('show');
            document.body.style.overflow = 'hidden';
        }

        function hideDownloadModal() {
            const overlay = document.getElementById('downloadModalOverlay');
            overlay.classList.remove('show');
            document.body.style.overflow = '';
            document.getElementById('downloadForm').reset();
            document.querySelectorAll('.download-form-field').forEach(f => f.classList.remove('error'));
        }

        function validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }

        function performDownload() {
            if (!pendingDownloadData) return;
            
            const { articleTitle, mainImageUrl, mainImageAlt, summary, bodyContent } = pendingDownloadData;
            
            try {
                const printWindow = window.open('', '_blank');
                if (printWindow) {
                    printWindow.document.write(`
                        <html>
                            <head>
                                <title>${articleTitle}</title>
                                <style>
                                    @media print {
                                        body { font-family: Arial, sans-serif; margin: 40px; max-width: 800px; }
                                        img { max-width: 100%; height: auto; margin: 20px 0; }
                                        .main-image { width: 100%; max-height: 400px; object-fit: cover; margin-bottom: 20px; }
                                        h1 { color: #3533CD; font-size: 32px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #3533CD; }
                                        .summary { font-size: 18px; color: #636363; margin-bottom: 30px; line-height: 1.6; }
                                        h2 { color: #333; margin-top: 30px; font-size: 24px; }
                                        h3 { color: #333; margin-top: 20px; font-size: 20px; }
                                        p { line-height: 1.6; margin-bottom: 15px; }
                                    }
                                    body { font-family: Arial, sans-serif; margin: 40px; max-width: 800px; }
                                    img { max-width: 100%; height: auto; margin: 20px 0; }
                                    .main-image { width: 100%; max-height: 400px; object-fit: cover; margin-bottom: 20px; }
                                    h1 { color: #3533CD; font-size: 32px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #3533CD; }
                                    .summary { font-size: 18px; color: #636363; margin-bottom: 30px; line-height: 1.6; }
                                    h2 { color: #333; margin-top: 30px; font-size: 24px; }
                                    h3 { color: #333; margin-top: 20px; font-size: 20px; }
                                    p { line-height: 1.6; margin-bottom: 15px; }
                                </style>
                            </head>
                            <body>
                                ${mainImageUrl ? `<img src="${mainImageUrl}" alt="${mainImageAlt}" class="main-image" />` : ''}
                                <h1>${articleTitle}</h1>
                                ${summary ? `<div class="summary">${summary}</div>` : ''}
                                <div class="content">
                                    ${bodyContent}
                                </div>
                            </body>
                        </html>
                    `);
                    printWindow.document.close();
                    
                    setTimeout(() => {
                        printWindow.print();
                        printWindow.close();
                    }, 1000);
                } else {
                    fallbackDownloadFromModal(articleTitle, mainImageUrl, mainImageAlt, summary, bodyContent);
                }
            } catch (error) {
                fallbackDownloadFromModal(articleTitle, mainImageUrl, mainImageAlt, summary, bodyContent);
            }
            
            pendingDownloadData = null;
        }

        function fallbackDownloadFromModal(articleTitle, mainImageUrl, mainImageAlt, summary, bodyContent) {
            const htmlContent = `
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>${articleTitle}</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 40px; max-width: 800px; }
                            img { max-width: 100%; height: auto; margin: 20px 0; }
                            .main-image { width: 100%; max-height: 400px; object-fit: cover; margin-bottom: 20px; }
                            h1 { color: #3533CD; font-size: 32px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #3533CD; }
                            .summary { font-size: 18px; color: #636363; margin-bottom: 30px; line-height: 1.6; }
                            h2 { color: #333; margin-top: 30px; font-size: 24px; }
                            h3 { color: #333; margin-top: 20px; font-size: 20px; }
                            p { line-height: 1.6; margin-bottom: 15px; }
                        </style>
                    </head>
                    <body>
                        ${mainImageUrl ? `<img src="${mainImageUrl}" alt="${mainImageAlt}" class="main-image" />` : ''}
                        <h1>${articleTitle}</h1>
                        ${summary ? `<div class="summary">${summary}</div>` : ''}
                        <div class="content">
                            ${bodyContent}
                        </div>
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
        }

        async function submitDownloadForm(event) {
            event.preventDefault();
            
            const firstName = document.getElementById('downloadFirstName').value.trim();
            const lastName = document.getElementById('downloadLastName').value.trim();
            const email = document.getElementById('downloadEmail').value.trim();
            const companyName = document.getElementById('downloadCompanyName').value.trim();
            const mobileNumber = document.getElementById('downloadMobileNumber').value.trim();
            
            let hasError = false;
            
            document.querySelectorAll('.download-form-field').forEach(f => f.classList.remove('error'));
            
            if (!firstName) {
                document.getElementById('firstNameField').classList.add('error');
                hasError = true;
            }
            
            if (!email || !validateEmail(email)) {
                document.getElementById('emailField').classList.add('error');
                hasError = true;
            }
            
            if (hasError) return;
            
            const submitBtn = document.getElementById('downloadSubmitBtn');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Submitting...';
            submitBtn.disabled = true;
            
            try {
                const pdfLink = window.location.href;
                
                const response = await fetch('/api/pdf-download-form', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        first_name: firstName,
                        last_name: lastName,
                        email: email,
                        company_name: companyName,
                        mobile_number: mobileNumber,
                        pdf_link: pdfLink
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to submit form');
                }
                
                hideDownloadModal();
                performDownload();
                
            } catch (error) {
                hideDownloadModal();
                performDownload();
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        }

        document.getElementById('downloadModalOverlay').addEventListener('click', function(e) {
            if (e.target === this) {
                hideDownloadModal();
            }
        });
    </script>
    <script>
    (function() {
        var initialDPR = window.devicePixelRatio || 1;

        function applyZoomCorrection() {
            var mainContent = document.getElementById('main-content');
            if (!mainContent) return;

            var currentDPR = window.devicePixelRatio || 1;
            var zoomFactor = currentDPR / initialDPR;

            if (Math.abs(zoomFactor - 1) > 0.01) {
                var scale = 1 / zoomFactor;
                if ('zoom' in document.body.style) {
                    mainContent.style.zoom = scale;
                    mainContent.style.transform = '';
                    mainContent.style.transformOrigin = '';
                    mainContent.style.width = '';
                } else {
                    mainContent.style.transform = 'scale(' + scale + ')';
                    mainContent.style.transformOrigin = 'top center';
                    mainContent.style.width = (zoomFactor * 100) + '%';
                    mainContent.style.zoom = '';
                }
            } else {
                mainContent.style.zoom = '';
                mainContent.style.transform = '';
                mainContent.style.transformOrigin = '';
                mainContent.style.width = '';
            }
        }

        function watchZoom() {
            var mqString = '(resolution: ' + window.devicePixelRatio + 'dppx)';
            matchMedia(mqString).addEventListener('change', function() {
                applyZoomCorrection();
                watchZoom();
            }, { once: true });
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                applyZoomCorrection();
                watchZoom();
            });
        } else {
            applyZoomCorrection();
            watchZoom();
        }
    })();
    </script>
    <script src="/static/js/zoom.js"></script>
    <script src="/static/js/homepage.js"></script>
    <script src="/static/js/auth.js"></script>
</body>

</html>"""


async def create_blog_html(data: dict, other_blogs: list = []) -> str:
    """Build the full blog HTML page from data and related blogs."""
    navbar_data = await get_navbar_data()
    header_html = await getHomepageStyleHeader(navbar_data)
    footer_html = await getHomepageStyleFooter()

    l = []
    l.append(await get_blog_body(data))
    l.append(await get_more_blogs_section(data, other_blogs))
    l.append(await get_faq_section())

    html = EMPTY_BLOG_TEMPLATE.replace("[[header_content]]", header_html)
    html = html.replace("[[footer_content]]", footer_html)
    html = html.replace("[[total_body]]", "\n".join(l))
    
    blog_title = data.get('blogTitle', 'Brands Out Loud Blog')
    blog_summary = data.get('blogSummary', 'Read our latest insights on business, technology, and industry trends.')
    
    meta_description = blog_summary[:157] + '...' if len(blog_summary) > 160 else blog_summary
    
    html = html.replace("[[[title]]]", f"{blog_title} | Brands Out Loud")
    html = html.replace("[[[meta_description]]]", meta_description)

    return html


async def get_all_blogs():
    """Fetch all blogs from MongoDB with caching. Returns a dict keyed by slug for O(1) lookup."""
    current_time = time.time()
    
    if blog_cache["data"] and current_time < blog_cache["expires_at"]:
        blog_cache["expires_at"] = current_time + CACHE_TTL
        return blog_cache["data"]

    db_start_time = time.time()
    db = db_handler.get_db()
    collection = db["blogs"]
    
    all_blogs_list = await collection.find(
        {"isDeleted": {"$ne": True}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(length=None)
    
    db_elapsed = time.time() - db_start_time
    print(f"Database Fetch | All Blogs | Time: {db_elapsed:.4f}s")
    
    all_blogs = {blog.get("slug"): blog for blog in all_blogs_list if blog.get("slug")}
    
    blog_cache["data"] = all_blogs
    blog_cache["expires_at"] = current_time + CACHE_TTL
    
    return all_blogs


@router.get("/blog/{slug}", tags=["Pages"])
async def get_blog(slug: str):
    """Render a blog post page by its slug. Uses O(1) dict lookup by slug key."""
    try:
        all_blogs = await get_all_blogs()
        
        blog_record = all_blogs.get(slug)

        if not blog_record:
            raise HTTPException(status_code=404, detail=f"Blog post not found: {slug}")
        
        other_blogs = [blog for key, blog in all_blogs.items() if key != slug]
        
        blog_content_raw = blog_record.get('blogContent', {})
        blog_data = {}
        if blog_content_raw:
            if isinstance(blog_content_raw, str):
                try:
                    blog_data = json.loads(blog_content_raw)
                except json.JSONDecodeError:
                    print(f"[ERROR] Failed to decode blogContent for blog {slug}")
            elif isinstance(blog_content_raw, dict):
                blog_data = blog_content_raw
        
        blog_data['slug'] = blog_record.get('slug', slug)
        
        display_date = blog_record.get('date') or blog_record.get('created_at')
        if display_date:
            if hasattr(display_date, 'strftime'):
                blog_data['blogDate'] = display_date.strftime('%B %d, %Y')
            else:
                blog_data['blogDate'] = str(display_date)
        
        html_content = await create_blog_html(blog_data, other_blogs)
        
        return HTMLResponse(html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Blog rendering error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


# @router.post("/api/admin_blog_preview", tags=["Admin"])
# async def admin_blog_preview(request: Request):
#     """
#     Preview blog from admin panel.
#     Receives preview data from frontend and returns rendered HTML.
#     Currently commented out - not needed for the time being.
#     """
#     try:
#         data = await request.json()
#         return {
#             "status": "success",
#             "message": "Preview data received",
#             "data": await create_blog_html(data, [])
#         }
#     except Exception as e:
#         print(f"Error in admin_blog_preview: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
