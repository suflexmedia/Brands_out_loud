
import json
import re
# Assuming these are in the same directory or accessible
from static.data.html_templates import BLOGS_TEMPLATE
from static.data.db_handler import get_leadership_details
from static.data.global_functions import *

from static.data.page_handlers.general_elements.header import *

def slugify(text):
    s = str(text).lower().strip()
    s = re.sub(r'[\s.&]+', '-', s)
    s = re.sub(r'[^\w-]', '', s)
    s = re.sub(r'--+', '-', s)
    if s.endswith("..."):
        s = s[:-3]
    s = s.strip('-')
    return s

def get_toc(json_data_full):
    # Simplified header template
    header_template = f'''<div class="mb-3 toc-section" data-section-id="[[section_id_slug]]">
            <a href="#[[section_id_slug]]" data-toggle-target="#[[sub_header_pointer]]" class="toc-h2-link flex items-center justify-between mt-1 mb-3 no-underline text-gray-800 hover:text-[#3533CD] transition-colors duration-200 toc-link">
                <div class="text-base font-medium">[[header]]</div>
                <i class="ph ph-caret-down text-xs ml-1 toc-arrow transition-transform duration-300"></i>
            </a>
            <div id="[[sub_header_pointer]]" class="toc-subcategories hidden pl-4 mb-3 space-y-2">
                [[subcategories]]
            </div>
        </div>'''

    # CORRECTED subheader_template
    subheader_template = '''<a href="#[[sub_section_slug]]" class="flex items-center mt-1 no-underline text-gray-600 hover:text-[#3533CD] transition-colors duration-200 toc-link border-l-2 border-gray-200 pl-3 hover:border-[#3533CD]">
                    <div class="text-sm">[[subheader]]</div>
                </a>'''

    dynamic_sections = json_data_full.get('dynamicSections', [])
    processed_headers = []
    current_header_details = None

    for section in dynamic_sections:
        if section['type'] in ['header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            header_content = section['content']
            header_slug = slugify(header_content)
            current_header_details = {
                'content': header_content,
                'slug': header_slug,
                'subheaders': []
            }
            processed_headers.append(current_header_details)
        elif section['type'] == 'subheader':
            if current_header_details:
                subheader_content = section['content']
                subheader_slug = slugify(subheader_content)
                current_header_details['subheaders'].append({
                    'content': subheader_content,
                    'slug': subheader_slug
                })

    toc_html_parts = []
    for header_detail in processed_headers:
        header_content = header_detail['content']
        header_slug = header_detail['slug']

        subcategories_html_list = []
        for sub_detail in header_detail['subheaders']:
            sub_html = subheader_template.replace('[[subheader]]', sub_detail['content'])
            sub_html = sub_html.replace("[[sub_section_slug]]", sub_detail['slug'])
            subcategories_html_list.append(sub_html)
        subcategories_str = '\n'.join(subcategories_html_list)

        header_html_part = header_template.replace('[[header]]', header_content)
        header_html_part = header_html_part.replace('[[subcategories]]', subcategories_str)
        header_html_part = header_html_part.replace('[[section_id_slug]]', header_slug)
        header_html_part = header_html_part.replace('[[sub_header_pointer]]', f'sub-{header_slug}')
        toc_html_parts.append(header_html_part)

    return '\n'.join(toc_html_parts)

def get_blog_content(json_data_full):
    # ... (this function's content remains unchanged)
    text_template = '''<p class="font-jakarta font-medium text-[15px] md:text-[16px] leading-[26px] md:leading-[30px] text-black" >
                [[textcontent]]
            </p>'''
    text_indented_template = '''<p class="font-jakarta font-medium text-[15px] md:text-[16px] leading-[26px] md:leading-[30px] text-black " >
                [[textcontent]]
            </p>'''
    h1_template = '''<h1 id="[[section_id]]" class="font-jakarta font-bold text-[28px] md:text-[36px] leading-[32px] md:leading-[40px] text-black scroll-mt-20" >
                [[h1content]]
            </h1>'''
    h2_template = '''<h2 id="[[section_id]]" class="font-jakarta font-medium text-[22px] md:text-[28px] leading-[28px] md:leading-[30px] text-black scroll-mt-20" >
                [[h2content]]
            </h2>'''
    h3_template = '''<h3 id="[[section_id]]" class="font-jakarta font-medium text-[20px] md:text-[24px] leading-[26px] md:leading-[28px] text-black scroll-mt-20" >
                [[h3content]]
            </h3>'''
    h4_template = '''<h4 id="[[section_id]]" class="font-jakarta font-medium text-[18px] md:text-[22px] leading-[24px] md:leading-[26px] text-black scroll-mt-20" >
                [[h4content]]
            </h4>'''
    h5_template = '''<h5 id="[[section_id]]" class="font-jakarta font-medium text-[16px] md:text-[20px] leading-[22px] md:leading-[24px] text-black scroll-mt-20" >
                [[h5content]]
            </h5>'''
    h6_template = '''<h6 id="[[section_id]]" class="font-jakarta font-medium text-[14px] md:text-[18px] leading-[20px] md:leading-[22px] text-black scroll-mt-20" >
                [[h6content]]
            </h6>'''
    image_template = '''<div class="w-full h-[120px] sm:h-[160px] md:h-[236px] my-8 md:my-12">
            <img src="[[imageurl]]" alt="[[imagealt]]" class="w-full h-full object-cover" />
          </div>'''
    subheader_paragraph_template = '''<p id="[[section_id]]" class="font-jakarta font-medium text-[15px] md:text-[16px] leading-[26px] md:leading-[30px] text-black mb-3 md:mb-4 scroll-mt-20 md:ml-[2rem]">
                <span class="font-semibold font-high text-[20px]">[[subheader_title]]<br/></span>
                [[subheader_body]]
            </p>'''
    output_html_parts = []
    sections = json_data_full.get('dynamicSections', [])
    idx = 0
    if sections and sections[0]['id'] == 'section_1' and sections[0]['content'] == json_data_full.get('blogSummary', ''):
        idx = 1
    in_subheader_group_div = False
    while idx < len(sections):
        section = sections[idx]
        section_type = section['type']
        if section_type not in ['subheader', 'subheader-text'] and in_subheader_group_div:
            output_html_parts.append("</div>")
            in_subheader_group_div = False
        if section_type == 'text':
            if section['id'] == 'section_3':
                output_html_parts.append(text_indented_template.replace('[[textcontent]]', section['content']))
            else:
                output_html_parts.append(text_template.replace('[[textcontent]]', section['content']))
            idx += 1
        elif section_type == 'h1':
            slug = slugify(section['content'])
            output_html_parts.append(h1_template.replace('[[h1content]]', section['content']).replace('[[section_id]]', slug))
            idx += 1
        elif section_type == 'h2':
            slug = slugify(section['content'])
            output_html_parts.append(h2_template.replace('[[h2content]]', section['content']).replace('[[section_id]]', slug))
            idx += 1
        elif section_type == 'h3':
            slug = slugify(section['content'])
            output_html_parts.append(h3_template.replace('[[h3content]]', section['content']).replace('[[section_id]]', slug))
            idx += 1
        elif section_type == 'h4':
            slug = slugify(section['content'])
            output_html_parts.append(h4_template.replace('[[h4content]]', section['content']).replace('[[section_id]]', slug))
            idx += 1
        elif section_type == 'h5':
            slug = slugify(section['content'])
            output_html_parts.append(h5_template.replace('[[h5content]]', section['content']).replace('[[section_id]]', slug))
            idx += 1
        elif section_type == 'h6':
            slug = slugify(section['content'])
            output_html_parts.append(h6_template.replace('[[h6content]]', section['content']).replace('[[section_id]]', slug))
            idx += 1
        elif section_type == 'header':
            slug = slugify(section['content'])
            output_html_parts.append(h2_template.replace('[[h2content]]', section['content']).replace('[[section_id]]', slug))
            idx += 1
        elif section_type == 'image':
            img_content = section.get('content', {})
            output_html_parts.append(image_template.replace('[[imageurl]]', img_content.get('url', '')).replace('[[imagealt]]', img_content.get('alt', '')))
            idx += 1
        elif section_type == 'subheader':
            if not in_subheader_group_div:
                output_html_parts.append("<div>")
                in_subheader_group_div = True
            subheader_title = section['content']
            subheader_slug = slugify(subheader_title)
            subheader_body_content = ""
            if (idx + 1 < len(sections) and
                sections[idx+1]['type'] == 'subheader-text' and
                sections[idx+1]['id'] == f"section_{int(section['id'].split('_')[1]) + 1}"):
                subheader_body_content = sections[idx+1]['content']
                idx_increment = 2
            else:
                idx_increment = 1
            p_html = subheader_paragraph_template.replace('[[section_id]]', subheader_slug)
            p_html = p_html.replace('[[subheader_title]]', subheader_title)
            p_html = p_html.replace('[[subheader_body]]', subheader_body_content)
            output_html_parts.append(p_html)
            idx += idx_increment
        elif section_type == 'subheader-text':
            if in_subheader_group_div:
                output_html_parts.append("</div>")
                in_subheader_group_div = False
            output_html_parts.append(text_indented_template.replace('[[textcontent]]', section['content']))
            idx += 1
        else:
            idx += 1
    if in_subheader_group_div:
        output_html_parts.append("</div>")
    return '\n'.join(output_html_parts)


def get_blog_html(demo_json_data):


    blogs_by_category = get_blogs_for_header(limit=3)

    checks = ['mainImageUrl', 'mainImageAlt', 'blogTitle', 'blogAuthor', 'blogDate', 'blogSummary']
    for check in checks:
        if check not in demo_json_data:
            raise ValueError(f"Missing required field: {check} in demo_json_data")

    seo_title = demo_json_data.get('seoTitle', '') or demo_json_data['blogTitle']
    seo_description = demo_json_data.get('seoMetaDescription', '') or demo_json_data['blogSummary']
    seo_canonical = demo_json_data.get('seoCanonicalUrl', '') or f"{demo_json_data.get('base_url', '')}/blog/{slugify(demo_json_data.get('blogTitle', ''))}"
    
    meta_tags = f'''<title>{seo_title}</title>
    <meta name="description" content="{seo_description}">
    <link rel="canonical" href="{seo_canonical}">'''
    
    base_blog = BLOGS_TEMPLATE.replace('[[seo_meta_tags]]', meta_tags)

    nav_links_html = desktop_menu_header_elements(blogs_by_category)
    base_blog = base_blog.replace('[[desktop_nav_links]]', nav_links_html)

    mobile_nav_links_html = mobile_menu_header_elements(blogs_by_category)
    base_blog = base_blog.replace('[[mobile_nav_links]]', mobile_nav_links_html)
    
    blog_category = demo_json_data.get('blogCategory', 'Uncategorized')
    base_blog = base_blog.replace('[[blog_category]]', blog_category)
    base_blog = base_blog.replace('[[main_page_image]]', demo_json_data['mainImageUrl'])
    base_blog = base_blog.replace('[[main_page_image_alt]]', demo_json_data['mainImageAlt'])
    base_blog = base_blog.replace('[[main_page_title]]', demo_json_data['blogTitle'])
    base_blog = base_blog.replace('[[author_name]]', demo_json_data['blogAuthor'])
    base_blog = base_blog.replace('[[publish_date]]', demo_json_data['blogDate'])
    base_blog = base_blog.replace('[[blog_summary]]', demo_json_data['blogSummary'])

    base_blog = base_blog.replace('[[ad_banner_beside_leaderhip_spotlight]]', demo_json_data['adBannerBesideUrl'])
    base_blog = base_blog.replace('[[link_to_ad_banner_beside_leadership_spotlight]]', demo_json_data['adBannerBesideHref'])
    

    base_blog = base_blog.replace('[[ad_banner_under_leadership_section]]', demo_json_data['adBannerBelowUrl'])
    base_blog = base_blog.replace('[[link_to_ad_banner_below_leadership_spotlight]]', demo_json_data['adBannerBelowHref'])
    
    
    business_cards = get_business_cards()
    base_blog = base_blog.replace('[[more_in_business_posts]]', business_cards)
    leader_details = get_leadership_details()
    base_blog = base_blog.replace('[[leadership_spotlight_image]]', leader_details['leader_image_url'])
    base_blog = base_blog.replace('[[leader_name]]', leader_details['leader_name'])
    base_blog = base_blog.replace('[[leader_designation]]', leader_details['leader_designation'])
    base_blog = base_blog.replace('[[leader_brief_description]]', leader_details['leader_desc'])
    base_blog = base_blog.replace('[[link_to_leadership_webstories]]', leader_details['web_stories_url'])
    if 'dynamicSections' not in demo_json_data:
        raise ValueError("Missing 'dynamicSections' in demo_json_data")
    toc = get_toc(demo_json_data)
    base_blog = base_blog.replace('[[table_of_contents_mobile_menu]]', toc)
    base_blog = base_blog.replace('[[table_of_contents_desktop_menu]]', toc)
    actual_blog_content = get_blog_content(demo_json_data)
    base_blog = base_blog.replace('[[actual_blog_content]]', actual_blog_content)
    
    base_blog = base_blog.replace('[blogs_by_category]', json.dumps(blogs_by_category))
    base_blog = base_blog.replace('[[breadcrumbs]]', breadcrumbs(blog_category))
    
    return base_blog