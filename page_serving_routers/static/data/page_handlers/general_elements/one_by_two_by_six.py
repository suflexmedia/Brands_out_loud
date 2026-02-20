def get_1_by_2_by_6_html(data: dict):
    # Extract main section data
    section_header = data.get("section_header", "AI")

    # Extract featured article data (large card)
    featured_article = data.get("featured_article", {})
    featured_image = featured_article.get("image_url", "")
    featured_category = featured_article.get("category", "")
    featured_author = featured_article.get("author", "")
    featured_date = featured_article.get("date", "")
    featured_title = featured_article.get("title", "")
    featured_read_time = featured_article.get("read_time", "")

    # Extract side articles data (2 cards)
    side_articles = data.get("side_articles", [])
    side_articles_html = ""

    for article in side_articles:
        side_articles_html += f"""
        <a href="{article.get('url', '#')}" class="block">
            <article class="bg-gray-50 flex-1 hover:bg-gray-100 transition-colors">
                <div class="mb-2 flex items-center">
                    <span class="inline-block px-2 py-0.5 text-xs font-medium bg-[#3533CD] text-white">{article.get('category', '')}</span>
                    <span class="ml-2 text-gray-500 text-xs flex items-center">
                        <span>{article.get('author', '')}</span>
                        <span class="mx-1">•</span>
                        <span>{article.get('date', '')}</span>
                    </span>
                </div>
                <h3 class="font-jakarta font-semibold text-lg text-gray-900 mb-2 truncate">
                    {article.get('title', '')}
                </h3>
                <img src="{article.get('image_url', '')}"
                    alt="{article.get('title', '')}" class="w-full h-[10.5rem] object-cover">
            </article>
        </a>"""

    # Extract small articles data (6 articles total)
    small_articles = data.get("small_articles", [])

    # Generate first row of small articles
    first_row_html = ""
    for article in small_articles[:3]:
        first_row_html += f"""
        <a href="{article.get('url', '#')}" class="block">
            <article class="flex gap-4 items-start hover:bg-gray-50 transition-colors p-2 rounded">
                <img src="{article.get('image_url', '')}" alt="{article.get('title', '')}"
                    class="w-16 h-16 object-cover flex-shrink-0">
                <div>
                    <div class="flex items-center">
                        <span class="text-xs font-medium text-[#3533CD]">{article.get('category', '')}</span>
                        <span class="ml-2 text-gray-500 text-xs">{article.get('author', '')} • {article.get('date', '')}</span>
                    </div>
                    <h4 class="font-jakarta font-semibold text-base mt-1 mb-1 text-gray-900 overflow-hidden"
                        style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                        {article.get('title', '')}
                    </h4>
                </div>
            </article>
        </a>"""

    # Generate second row of small articles
    second_row_html = ""
    for article in small_articles[3:6]:
        second_row_html += f"""
        <a href="{article.get('url', '#')}" class="block">
            <article class="flex gap-4 items-start hover:bg-gray-50 transition-colors p-2 rounded">
                <img src="{article.get('image_url', '')}" alt="{article.get('title', '')}"
                    class="w-16 h-16 object-cover flex-shrink-0">
                <div>
                    <div class="flex items-center">
                        <span class="text-xs font-medium text-[#3533CD]">{article.get('category', '')}</span>
                        <span class="ml-2 text-gray-500 text-xs">{article.get('author', '')} • {article.get('date', '')}</span>
                    </div>
                    <h4 class="font-jakarta font-semibold text-base mt-1 mb-1 text-gray-900 overflow-hidden"
                        style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                        {article.get('title', '')}
                    </h4>
                </div>
            </article>
        </a>"""

    return f"""
        <section class="w-full px-6 md:px-8 bg-white" style="padding-top: 1rem; padding-bottom: 2rem;">
            <div class="max-w-7xl mx-auto">
                <div class="flex justify-between items-center mb-8">
                    <div class="relative">
                        <h2 class="font-jakarta font-bold text-3xl text-[#0D0D0D]">
                            <!-- <section_5_header> -->{section_header}<!-- <section_5_header> --></h2>
                        <div class="absolute h-1 w-16 bg-[#3533CD] bottom-0 left-0"></div>
                    </div>
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                    <div class="lg:col-span-2 h-[500px]">
                        <a href="{featured_article.get('url', '#')}" class="block h-full">
                            <article class="group relative h-full hover:opacity-95 transition-opacity">
                                <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-10"></div>
                                <img src="{featured_image}"
                                    alt="{featured_title}" class="w-full h-full object-cover">
                                <div class="absolute left-0 top-6 z-20 flex items-center">
                                    <span
                                        class="inline-block px-3 py-1 ml-6 text-xs font-medium bg-[#3533CD] text-white">{featured_category}</span>
                                    <span class="ml-2 text-white/80 text-xs">{featured_author} • {featured_date}</span>
                                </div>
                                <div class="absolute inset-x-0 bottom-0 p-6 z-20">
                                    <h3 class="font-jakarta font-bold text-2xl text-white mb-2 truncate">
                                        {featured_title}
                                    </h3>
                                    <div class="flex items-center text-white/80 text-sm">
                                        <span>{featured_read_time}</span>
                                    </div>
                                </div>
                            </article>
                        </a>
                    </div>
                    <div class="lg:col-span-1 flex flex-col gap-6 h-[500px]">
                        {side_articles_html}
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {first_row_html}
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {second_row_html}
                </div>
            </div>
            <div class="md:mt-[1rem] md:ml-[38rem] md:mb-[-1rem]">
                <a href="#" class="font-jakarta text-sm text-[#3533CD] hover:underline flex items-center">
                    View All Articles
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-1" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                </a>
            </div>
        </section>
    """
