def get_1_by_3_html(data: dict):
    # Extract left section data
    left_section_image_url = data.get('left_section_image_url', '')
    left_section_title = data.get('left_section_title', '')
    left_section_author = data.get('left_section_author', '')
    left_section_date = data.get('left_section_date', '')
    left_section_url = data.get('url', '')
    
    # Extract right section data
    right_section_header = data.get('right_section_header', '')
    right_section_articles = data.get('right_section_articles', [])
    
    # Generate articles HTML
    articles_html = ""
    for article in right_section_articles:
        article_image = article.get('image_url', '')
        article_author = article.get('author', '')
        article_date = article.get('date', '')
        article_title = article.get('title', '')
        article_excerpt = article.get('excerpt', '')
        article_url = article.get('url', '')
        
        articles_html += f"""
        <article class="flex flex-col md:flex-row gap-4 md:w-full border-b border-white/30 pb-3.5"> 
            <a href="{article_url}" class="w-full md:w-[289.2px] h-[150px] bg-cover bg-center rounded-[6px] bg-[url({article_image})] flex-shrink-0"></a>
            <div class="flex flex-col justify-center">
                <div class="w-auto md:w-[137.18px] h-[10px] font-jakarta font-medium text-[10px] leading-[1] text-white/60 mb-2">{article_author} - {article_date}</div>
                <a href="{article_url}"><h3 class="w-auto md:w-auto h-auto font-jakarta font-normal text-lg leading-[136.9%] text-white mb-2">{article_title}</h3></a>
                <p class="w-auto md:w-auto h-auto font-jakarta font-normal text-xs leading-[123.9%] text-white">{article_excerpt}</p> 
            </div>
        </article>"""

    ONE_BY_THREE_HTML_TEMPLATE = f"""<section class="w-full h-auto relative overflow-hidden my-5 md:my-0 mb-4"> 
        <div class="absolute inset-0 w-full h-full bg-gradient-to-br from-[#3533CD] via-black to-black md:bg-[linear-gradient(125.25deg,_#3533CD_0.4%,_#000000_47.94%)] rounded-none md:rounded-[6px]"></div>
        <div class="relative w-full h-full z-10 p-4 md:p-0 grid grid-cols-1 md:grid-cols-2 md:gap-0"> 
            
            <div class="relative w-full h-auto md:h-full"> 
                <a href="{left_section_url}" class="relative w-[26rem] md:w-full h-[30rem] mt-[-1rem] md:mt-[0px] md:h-[40.5rem] -mx-4 md:mx-0 md:absolute md:inset-0 bg-cover bg-center rounded-none bg-[url({left_section_image_url})] block"> 
                    
                    <div class="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/80 via-black/50 to-transparent rounded-b-none"></div> 
                    
                    <div class="absolute bottom-4 left-4 right-4 md:bottom-6 md:left-6 md:right-6 z-10"> 
                        <div class="font-dm font-normal text-sm leading-[1.1] text-white md:text-[18px] mb-1">{left_section_author} - {left_section_date}</div>
                        <h2 class="font-jakarta font-bold text-xl leading-tight capitalize text-white md:text-[32px] md:leading-[40px]">{left_section_title}</h2>
                    </div>
                </a>
            </div>

            <div class="flex flex-col gap-4 md:p-8"> 
                <h2 class="w-auto md:w-[100%] h-auto md:h-[38px] font-jakarta font-bold text-2xl md:text-[28px] leading-[38px] text-white pb-4">{right_section_header}</h2>
                {articles_html}
            </div>
        </div>
    </section>"""
    
    return ONE_BY_THREE_HTML_TEMPLATE
