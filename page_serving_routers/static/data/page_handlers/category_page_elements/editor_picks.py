def get_editor_picks(articles: dict):

    # Generate articles HTML
    articles_html = ""
    for article in articles:
        article_image = article.get("image_url", "")
        article_author = article.get("author", "")
        article_date = article.get("date", "")
        article_title = article.get("title", "")
        article_excerpt = article.get("excerpt", "")

        articles_html += f"""
            <a href="{article.get('url', '#')}" class="flex flex-col md:flex-row gap-4 hover:opacity-80 transition-opacity">
                <div class="w-full md:w-1/2 h-[200px] md:h-auto">
                    <img src="{article_image}" alt="{article_title}"
                    class="rounded-md w-full h-full object-cover">
                </div>
                <div class="w-full md:w-1/2">
                    <span class="text-xs text-opacity-60 text-white font-medium">{article_author} - {article_date}</span>
                    <h2 class="text-lg font-normal leading-tight mt-2 text-white">{article_title}</h2>
                    <p class="text-xs leading-snug mt-4 text-white/70">{article_excerpt}</p>
                </div>
                </a>"""

    EDITOR_PICKS_TEMPLATE = f"""<section class="w-full py-8 bg-black text-white" style="margin-bottom: 2rem;">
            <div class="max-w-7xl mx-auto px-4">

                <div class="mb-6">
                    <h1 class="text-3xl font-extrabold text-white">Editor Picks</h1>
                    <div class="mt-4 relative">
                        <hr class="border-t border-gray-500 w-full" />
                        <hr class="border-t-2 border-white w-48 absolute top-0 left-0" />
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {articles_html}
                </div>
        </section>"""

    return EDITOR_PICKS_TEMPLATE
