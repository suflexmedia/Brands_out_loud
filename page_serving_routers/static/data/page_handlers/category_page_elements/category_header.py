def get_category_header_html(category_name: str) -> str:
    return f"""
    <section class="w-full bg-white px-4 sm:px-6 md:px-20 py-10" style="zoom: 0.78;">
            <h1 class="font-jakarta font-extrabold text-5xl md:text-6xl uppercase tracking-wider text-bol-purple">
                {category_name}</h1>
            <div class="mt-4 relative">
                <div class="w-full border-t border-gray-700"></div>
                <div class="absolute top-0 left-0 w-48 border-t-2 border-bol-purple"></div>
            </div>
        </section>
    """
