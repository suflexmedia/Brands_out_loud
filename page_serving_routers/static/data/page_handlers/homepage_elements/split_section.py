def get_split_section(data: dict) -> str:
    # Extract left section data
    left_section_title = data.get("left_section_title", "Sustainability")
    left_section_articles = data.get("left_section_articles", [])

    # Extract right section data
    right_section_title = data.get("right_section_title", "Semiconductors")
    right_section_articles = data.get("right_section_articles", [])

    # Generate left section articles HTML
    left_articles_html = ""
    for article in left_section_articles:
        article_image = article.get("image_url", "")
        article_author = article.get("author", "")
        article_date = article.get("date", "")
        article_title = article.get("title", "")
        article_excerpt = article.get("excerpt", "")

        article_url = article.get("url", "#")
        left_articles_html += f"""
             <a href="{article_url}" class="block">
                 <article class="flex flex-col sm:flex-row gap-4 border-b border-white/30 pb-3 hover:opacity-80 transition-opacity">
                 <div class="w-full sm:w-1/3 aspect-video md:h-28 bg-cover bg-center rounded-md flex-shrink-0 bg-[url({article_image})]"></div>
                 <div class="flex flex-col justify-center sm:w-2/3">
                     <div class="font-jakarta font-medium text-[10px] text-white/60 mb-1">{article_author} - {article_date}</div>
                     <h3 class="font-jakarta font-normal text-base md:text-lg leading-snug text-white mb-1">{article_title}</h3>
                     <p class="font-jakarta font-normal text-xs leading-relaxed text-white/80 hidden sm:block">{article_excerpt}</p>
                 </div>
                 </article>
             </a>"""

        # Generate right section articles HTML
    right_articles_html = ""
    for article in right_section_articles:
        article_image = article.get("image_url", "")
        article_author = article.get("author", "")
        article_date = article.get("date", "")
        article_title = article.get("title", "")
        article_excerpt = article.get("excerpt", "")
        article_url = article.get("url", "#")

        right_articles_html += f"""
            <a href="{article_url}" class="block">
                <article class="flex flex-col sm:flex-row gap-4 border-b border-white/30 pb-3 hover:opacity-80 transition-opacity">
                <div class="w-full sm:w-1/3 aspect-video md:h-28 bg-cover bg-center rounded-md flex-shrink-0 bg-[url({article_image})]"></div> 
                <div class="flex flex-col justify-center sm:w-2/3">
                    <div class="font-jakarta font-medium text-[10px] text-white/60 mb-1">{article_author} - {article_date}</div> 
                    <h3 class="font-jakarta font-normal text-base md:text-lg leading-snug text-white mb-1">{article_title}</h3> 
                    <p class="font-jakarta font-normal text-xs leading-relaxed text-white/80 hidden sm:block">{article_excerpt}</p> 
                </div>
                </article>
            </a>"""

        SPLIT_SECTION_TEMPLATE = f"""
        <section class="w-full grid grid-cols-1 md:grid-cols-2 justify-center items-start gap-[5px] md:gap-4 mx-auto mt-4">
        
        <div class="w-full h-[1050px] md:h-[550px] relative overflow-hidden bg-gradient-to-tl from-[#3533CD] via-black to-black p-6">
             <h2 class="font-jakarta font-bold text-2xl md:text-3xl text-white mb-6">{left_section_title}</h2>
             <div class="flex flex-col gap-5">
             {left_articles_html}
             </div>
        </div>
        
         <div class="w-full h-[1050px] md:h-[550px] relative overflow-hidden bg-gradient-to-tl from-[#3533CD] via-black to-black p-6">
             <h2 class="font-jakarta font-bold text-2xl md:text-3xl text-white mb-6">{right_section_title}</h2>
             <div class="flex flex-col gap-5">
            {right_articles_html}
            </div>
        </div>
        </section>"""

    return SPLIT_SECTION_TEMPLATE
