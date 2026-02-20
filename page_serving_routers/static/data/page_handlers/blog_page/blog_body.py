from .hero_section import get_blog_hero_section

def generate_mobile_toc(data):
    """
    Generate a mobile Table of Contents HTML from structured data.
    
    Args:
        data: List of dictionaries with 'id', 'type', and 'content' keys
    
    Returns:
        Complete HTML string for the mobile TOC
    """
    toc_sections = _generate_toc_sections(data)
    
    complete_toc = f"""<div class="block lg:hidden px-4 mt-8">
            <div class="relative toc-container p-5 bg-white rounded-xl border-gray-100">
                <h2 class="text-xl font-bold text-[#3533CD] mb-4 border-b pb-3">Table of Contents</h2>
                {toc_sections}
                <div class="mt-6 space-y-4 border-t pt-5">
                    <button
                        class="w-full h-[45px] bg-[#3533CD] rounded-xl flex items-center justify-center text-white font-jakarta font-medium text-[16px] leading-[120%] hover:bg-opacity-90 transition-colors shadow-md">
                        <i class="ph ph-download mr-2"></i>Download Article as PDF
                    </button>
                    <div class="flex items-center flex-wrap">
                        <div
                            class="relative inline-flex items-center justify-center gap-2 bg-[#3533CD] rounded-xl h-[45px] px-4 cursor-pointer hover:bg-opacity-90 transition-colors shadow-md">
                            <span class="text-white font-jakarta font-medium text-[16px] leading-[120%] text-center"
                                style="width: 7rem">
                                <i class="ph ph-share-network mr-2"></i>Share
                            </span>
                        </div>
                        <div class="flex space-x-3 ml-3">
                            <img src="/static/images/whatsapp_logo.png" alt="WhatsApp"
                                class="w-[35px] h-[35px] object-contain hover:opacity-80 transition-opacity" />
                            <img src="/static/images/insta_logo.png" alt="Instagram"
                                class="w-[35px] h-[35px] object-contain hover:opacity-80 transition-opacity" />
                        </div>
                    </div>
                </div>
            </div>
        </div>"""
    
    return complete_toc


def generate_desktop_toc(data):
    """
    Generate a desktop/sidebar Table of Contents HTML from structured data.
    
    Args:
        data: List of dictionaries with 'id', 'type', and 'content' keys
    
    Returns:
        Complete HTML string for the desktop TOC
    """
    toc_sections = _generate_toc_sections(data)
    
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
                        <div class="flex items-center flex-wrap">
                            <div
                                class="relative inline-flex items-center justify-center gap-2 bg-[#3533CD] rounded-xl h-[45px] px-4 cursor-pointer hover:bg-opacity-90 transition-colors shadow-md">
                                <span class="text-white font-jakarta font-medium text-[16px] leading-[120%] text-center"
                                    style="width: 7rem">
                                    <i class="ph ph-share-network mr-2"></i>Share
                                </span>
                            </div>
                            <div class="flex space-x-3 ml-3">
                                <img src="/static/images/whatsapp_logo.png" alt="WhatsApp"
                                    class="w-[35px] h-[35px] object-contain hover:opacity-80 transition-opacity" />
                                <img src="/static/images/insta_logo.png" alt="Instagram"
                                    class="w-[35px] h-[35px] object-contain hover:opacity-80 transition-opacity" />
                            </div>
                        </div>
                    </div>
                </div>
            </aside>"""
    
    return complete_toc


def _generate_toc_sections(data):
    """
    Helper function to generate the TOC sections that are common to both mobile and desktop versions.
    
    Args:
        data: List of dictionaries with 'id', 'type', and 'content' keys
    
    Returns:
        HTML string for the TOC sections only
    """
    # Filter for headers only
    headers = ['h1', 'h2']
    temp_list = [item for item in data if item['type'] in headers]
    
    final_product = []
    sub_list = []
    base_template = None
    
    for item in temp_list:
        if item['type'] == 'h1':
            # If we have a previous h1 section, finalize it
            if base_template is not None:
                sub_categories = '\n'.join(sub_list) if sub_list else ''
                final_section = base_template.replace('[[sub_categories]]', sub_categories)
                final_product.append(final_section)
            
            # Start new h1 section
            sub_list = []
            base_template = f"""<div class="mb-3 toc-section" data-section-id="{item['id']}">
                        <a href="#{item['id']}"
                            data-toggle-target="#sub-{item['id']}"
                            class="toc-h2-link flex items-center justify-between mt-1 mb-3 no-underline text-gray-800 hover:text-[#3533CD] transition-colors duration-200 toc-link">
                            <div class="text-base font-medium">{item['content']}</div>
                            <i class="ph ph-caret-down text-xs ml-1 toc-arrow transition-transform duration-300"></i>
                        </a>
                        <div id="sub-{item['id']}"
                            class="toc-subcategories hidden pl-4 mb-3 space-y-2">
                            [[sub_categories]]
                        </div>
                    </div>"""
        
        elif item['type'] == 'h2':
            # Add h2 as subcategory
            sub_template = f"""                            <a href="#{item['id']}"
                                class="flex items-center mt-1 no-underline text-gray-600 hover:text-[#3533CD] transition-colors duration-200 toc-link border-l-2 border-gray-200 pl-3 hover:border-[#3533CD]">
                                <div class="text-sm">{item['content']}</div>
                            </a>"""
            sub_list.append(sub_template)
    
    # Don't forget the last section
    if base_template is not None:
        sub_categories = '\n'.join(sub_list) if sub_list else ''
        final_section = base_template.replace('[[sub_categories]]', sub_categories)
        final_product.append(final_section)
    
    return '\n'.join(final_product)

def get_blog_content(data: dict):
    content = []
    for i in data:
        if i['type'] == 'text':
            content.append(f'''<p class="font-jakarta font-medium text-[15px] md:text-[16px] leading-[26px] md:leading-[30px] text-black" >{i['content']}</p>''')
        if i['type'] == 'h1':
            content.append(f'''<h1 id="{i['id']}" class="font-jakarta font-bold text-[28px] md:text-[36px] leading-[32px] md:leading-[40px] text-black scroll-mt-20" >{i['content']}</h1>''')
        if i['type'] == 'h2':
            content.append(f'''<h2 id="{i['id']}" class="font-jakarta font-medium text-[22px] md:text-[28px] leading-[28px] md:leading-[30px] text-black scroll-mt-20" >{i['content']}</h2>''')
        if i['type'] == 'h3':
            content.append(f'''<h3  class="font-jakarta font-medium text-[20px] md:text-[24px] leading-[26px] md:leading-[28px] text-black scroll-mt-20" >{i['content']}</h3>''')
        if i['type'] == 'h4':
            content.append(f'''<h4  class="font-jakarta font-medium text-[18px] md:text-[22px] leading-[24px] md:leading-[26px] text-black scroll-mt-20" >{i['content']}</h4>''')
        if i['type'] == 'h5':
            content.append(f'''<h5  class="font-jakarta font-medium text-[16px] md:text-[20px] leading-[22px] md:leading-[24px] text-black scroll-mt-20" >{i['content']}</h5>''')
        if i['type'] == 'h6':
            content.append(f'''<h6  class="font-jakarta font-medium text-[14px] md:text-[18px] leading-[20px] md:leading-[22px] text-black scroll-mt-20" >{i['content']}</h6>''')
        if i['type'] == 'image':
            content.append(f'''<div class="w-full h-[120px] sm:h-[160px] md:h-[236px] my-8 md:my-12"><img src="{i['content']['url']}" alt="{i['content']['alt']}" class="w-full h-full object-cover"/></div>''')
    content = "\n".join(content)
    return f"""<section class="max-w-[43rem] space-y-6 md:space-y-5 text-justify order-1 lg:order-2">{content}</section>"""
    

def get_blog_body(data:dict):
    return f"""
        {get_blog_hero_section(data)}
        {generate_mobile_toc(data['dynamicSections'])}
        <div class="grid grid-cols-1 lg:grid-cols-[300px_1fr] md:ml-[-16rem] gap-8 mt-4 md:mt-8 ml-0 mr-0" style="padding: 0 0.5rem">
        {generate_desktop_toc(data['dynamicSections'])}
        {get_blog_content(data['dynamicSections'])}
        </div>

"""
