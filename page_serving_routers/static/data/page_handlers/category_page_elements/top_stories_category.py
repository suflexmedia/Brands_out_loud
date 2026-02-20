def get_top_stories_category(articles: dict):

    # Generate articles HTML
    articles_html = ""
    for article in articles:
        article_image = article.get("image_url", "https://picsum.photos/365/243")
        article_author = article.get("author", "")
        article_date = article.get("date", "")
        article_title = article.get("title", "")
        article_excerpt = article.get("excerpt", "")

        article_url = article.get("url", "#")
        articles_html += f"""
            <a href="{article_url}" class="flex flex-col group">
                <div class="w-full h-[250px] bg-cover bg-center mb-[15px] rounded-md"
                style="background-image: url('{article_image}')"></div>
                <div class="font-jakarta text-[10px] leading-[1.1] text-bol-black/60 mb-[6px]">{article_author} - {article_date}</div>
                <h3 class="font-jakarta font-normal text-lg leading-[136.9%] text-bol-black mb-[10px]">{article_title}</h3>
                <p class="font-jakarta text-xs leading-[123.9%] text-bol-black/70">{article_excerpt}</p>
            </a>"""

    TOP_STORIES_TEMPLATE = f"""<section class="relative w-full h-auto flex flex-col" style="max-width: 95%;">

            <div class="relative w-full h-[42px] mb-[25px]">
                <h2 class="absolute left-0 top-0 font-jakarta font-extrabold text-2xl leading-[30px] text-bol-purple">
                    Top Stories</h2>
                <div class="absolute left-0 top-[42px] w-full border-t border-[#393939]"></div>
                <div class="absolute left-0 top-[42px] w-[100px] border-t-2 border-bol-purple z-10"></div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-[30px] gap-y-[35px] w-full mt-8">
                {articles_html}
            </div>
        </section>"""

    return TOP_STORIES_TEMPLATE
