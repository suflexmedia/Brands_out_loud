def get_footer():
    FOOTER_TEMPLATE ="""<footer class="w-full bg-black px-4 sm:px-6 md:px-[111px] pt-[40px] md:pt-[70px] pb-[20px] md:pb-[30px] relative text-white">
                
        
        <div class="flex flex-row flex-wrap justify-around items-start gap-6 md:gap-16 mb-8 md:mb-[100px] pt-6 md:pt-0 text-center sm:text-left">

            
            <div class="w-auto flex flex-col items-center sm:items-start order-1 mb-6 sm:mb-0 flex-shrink-0">
                <a href="/"><div class="w-[80px] h-[80px] sm:w-[100px] sm:h-[100px] md:w-[161px] md:h-[161px] bg-contain bg-no-repeat bg-center sm:bg-left bg-[url(/static/images/header_logo.png)] mb-2 flex-shrink-0" loading="lazy"></div></a>
            </div>

            
            <div class="w-auto order-2 flex-shrink-0">
                <div class="font-helvetica font-bold text-sm md:text-base leading-[90%] text-[#8B8B8B] mb-3 md:mb-[19px] uppercase">Quick Links</div>
                <ul class="list-none p-0 m-0 space-y-2 md:space-y-[17px]">
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">Home</a></li>
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">About Us</a></li>
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">Careers</a></li>
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">Web Stories</a></li>
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">Magazine</a></li>
                </ul>
            </div>

            
            <div class="w-auto order-3 flex-shrink-0">
                <div class="font-helvetica font-bold text-sm md:text-base leading-[90%] text-[#8B8B8B] mb-3 md:mb-[20px] uppercase">News</div>
                <ul class="list-none p-0 m-0 space-y-2 md:space-y-[17px]">
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">Business</a></li>
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">Startup</a></li>
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">AI</a></li>
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">Entrepreneur</a></li>
                    <li><a href="#" class="font-helvetica font-bold text-xs sm:text-sm md:text-base leading-[90%] text-white no-underline hover:text-[#C4C3FF] uppercase">Events</a></li>
                </ul>
            </div>
        </div>

        <div class="border-t border-white/30 w-full my-[30px] md:my-[40px]"></div>

        
        <div class="flex flex-col md:flex-row justify-between items-center">
           
            
            <div class="block mb-6 md:mb-4 w-full md:w-auto text-center md:text-left">
                <div class="font-helvetica font-bold text-sm md:text-base leading-[90%] text-[#8B8B8B] mb-[12px] md:mb-[15px] uppercase">Social Links</div>
                <div class="flex justify-center md:justify-start space-x-4">
                    <a href="#" aria-label="Instagram" class="text-white hover:text-[#C4C3FF] transition-colors duration-200">
                        <svg class="w-5 h-5 md:w-6 md:h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
                        </svg>
                    </a>
                    <a href="#" aria-label="Facebook" class="text-white hover:text-[#C4C3FF] transition-colors duration-200">
                        <svg class="w-5 h-5 md:w-6 md:h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                        </svg>
                    </a>
                    <a href="#" aria-label="X (Twitter)" class="text-white hover:text-[#C4C3FF] transition-colors duration-200">
                        <svg class="w-5 h-5 md:w-6 md:h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                        </svg>
                    </a>
                    <a href="#" aria-label="YouTube" class="text-white hover:text-[#C4C3FF] transition-colors duration-200">
                        <svg class="w-5 h-5 md:w-6 md:h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                        </svg>
                    </a>
                    <a href="#" aria-label="LinkedIn" class="text-white hover:text-[#C4C3FF] transition-colors duration-200">
                        <svg class="w-5 h-5 md:w-6 md:h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                    </a>
                </div>
            </div>

            
            <div class="flex flex-col md:flex-row justify-between items-center gap-4 md:gap-[20px] flex-wrap mb-6 md:mb-[40px]">
                <a href="/advertise_with_us" class="font-jakarta font-bold text-sm md:text-base leading-[20px] text-white no-underline hover:text-[#C4C3FF] uppercase">Advertise With Us</a>
            </div>

            
            <div class="text-center md:text-left col-span-1 lg:col-span-1 flex flex-col items-center md:items-start">
                <div class="font-helvetica font-bold text-base leading-[90%] text-[#8B8B8B] mb-[20px] uppercase">Subscribe to Newsletter</div>
                
                <form class="flex flex-row items-stretch gap-2 w-full max-w-md sm:hidden">
                     <input type="email" placeholder="Enter your email" required class="flex-grow h-[40px] bg-white border-none rounded-[4px] px-[15px] text-black placeholder:text-gray-500 focus:ring-2 focus:ring-bol-purple" style="left: 1rem; position: relative;">
                     <input type="image" src="/static/images/subscribe_button.png" alt="Subscribe" class="h-[40px] w-auto cursor-pointer hover:opacity-90 transition duration-150 ease-in-out shrink-0" style="left: -1rem; position: relative;">
                 </form>
                 
                 <form class="hidden sm:flex sm:flex-row items-stretch gap-2 w-full max-w-md">
                     <input type="email" placeholder="Enter your email" required class="flex-grow h-[40px] bg-white border-none rounded-[4px] px-[15px] text-black placeholder:text-gray-500 focus:ring-2 focus:ring-bol-purple">
                     <input type="image" src="/static/images/subscribe_button.png" alt="Subscribe" class="h-[40px] w-auto cursor-pointer hover:opacity-90 transition duration-150 ease-in-out shrink-0" style="left: -2rem; position: relative;">
                 </form>
            </div>
        </div>

        
        <div class="block">
            <div class="border-t border-white/30 w-full my-[30px] md:my-[40px]"></div>
            <div class="w-full text-center font-helvetica font-bold text-xs md:text-base leading-[90%] text-white/70 mt-[20px]">
                © 2025 BRANDSOUTLOUD All Rights Reserved
            </div>
        </div>
    </footer>"""

    return FOOTER_TEMPLATE