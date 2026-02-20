from ..general_elements import get_leadership_spotlight


def get_top_stories(data: dict):
    TOP_STORIES_TEMPLATE = f"""<section class="w-full py-4 md:py-6 px-4 md:px-8"> 
    <div class="flex flex-col md:flex-row gap-6 md:gap-4 max-w-7xl mx-auto">
        <div class="relative w-full h-[22rem] sm:h-[24rem] md:h-[32rem] md:flex-1">
            <a href="{data.get('url', '#')}" class="w-full h-full relative overflow-hidden block">
                <img src="{data.get('image_url','')}" alt="Image related to North Korea's nuclear program" class="w-full h-full object-cover">
                <div class="absolute left-[1rem] md:left-0 bottom-[6.5rem] sm:bottom-[10rem] md:bottom-[6rem] md:left-[2.5rem] z-10">
                    <div class="bg-[#3533CD] px-2 py-1 md:px-4 md:py-2">
                        <span class="font-roboto font-bold text-xs md:text-sm uppercase text-white">TOP STORIES</span>
                    </div>
                </div>
                <div class="absolute bottom-0 left-0 right-0 bg-white p-3 md:p-4 w-full md:max-w-3xl md:ml-8">
                    <h2 class="font-jakarta font-semibold text-lg md:text-xl leading-tight text-[#222222] mb-1 md:mb-2">{data.get('title')}</h2>
                    <p class="font-jakarta font-normal text-xs md:text-sm leading-relaxed text-[#555555]">{data.get('description','')}</p>
                </div>
            </a>
        </div>
        {get_leadership_spotlight()}
    </div>
</section>"""
    return TOP_STORIES_TEMPLATE
