from ...db_handler import get_blogs_by_category

def get_cards(category):
    print(f"Fetching blogs for category: {category}")
    blogs = get_blogs_by_category(category.upper())
    print(f"Fetched {len(blogs)} blogs for category '{category}'")
    xx = []
    for blog in blogs[:2]:
        mm = blog
        blog = blog.get("json_data", {})
        xx.append(f"""<a href="/blog/{mm['id']}" class="block">
    <div class="card bg-white rounded-xl shadow-md overflow-hidden flex-1 hover:shadow-lg transition-shadow duration-300">
        <!-- Card image -->
        <div class="h-48 overflow-hidden">
            <img src="{blog['mainImageUrl']}" alt="{blog['mainImageAlt']}" class="w-full h-full object-cover">
        </div>
        <!-- Card content -->
        <div class="p-6">
            <h3 class="text-xl font-bold text-gray-800 mb-2">{blog['blogTitle']}</h3>
            <p class="text-gray-600 mb-4">{blog['blogSummary']}</p>
            <div class="flex items-center text-sm text-gray-500 mb-3">
                <span>{blog['blogAuthor']}</span>
                <span class="mx-2">•</span>
                <span>{blog['blogDate']}</span>
            </div>
        </div>
    </div>
</a>""")
    return "\n".join(xx)
    


def get_more_blogs_section(data: dict):
    template = """
    <style>
        more_blogs {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f9fafb;
        }
        .card {
            transition: transform 0.2s ease-in-out;
        }
        .card:hover {
            transform: translateY(-4px);
        }
        .tag {
            transition: all 0.2s ease;
        }
        .tag:hover {
            background-color: #e2e8f0;
        }
    </style>
    
    <section class="py-12 px-4 more_blogs">
    <hr class="border-t border-black my-8 md:my-12 w-full md:w-[90%] lg:w-[80rem] mx-auto" />
    <div class="max-w-6xl mx-auto">
        <!-- Heading -->
        <h2 class="text-4xl font-serif text-center mb-10 text-gray-800">Related Articles and Topics</h2>
        
        <!-- Main content container -->
        <div class="flex flex-col lg:flex-row gap-6">
            <!-- Articles container - left side -->
            <div class="flex flex-col md:flex-row gap-6 lg:w-2/3">
                <!-- Cards -->
                [[cards]]
                

                
            </div>

            <!-- Topics container - right side -->
            <div class="lg:w-1/3 flex flex-wrap content-start gap-3">
                <a href="/business" class="tag px-4 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 font-medium hover:bg-gray-50">
                    Business
                </a>
                <a href="/technology" class="tag px-4 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 font-medium hover:bg-gray-50">
                    Technology
                </a>
                <a href="/gcc" class="tag px-4 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 font-medium hover:bg-gray-50">
                    Gcc
                </a>
                <a href="/sustainability" class="tag px-4 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 font-medium hover:bg-gray-50">
                    Sustainability
                </a>
                <a href="/semiconductor" class="tag px-4 py-3 bg-white border border-gray-200 rounded-lg text-gray-700 font-medium hover:bg-gray-50">
                    Semiconductor
                </a>
            </div>
        </div>
    </div>
</section>"""

    return template.replace("[[cards]]", get_cards(data.get("blogCategory")))