from ...db_handler import get_leadership_details

def get_leadership_spotlight():
    data = get_leadership_details()
    LEADERSHIP_SPOTLIGHT_TEMPLATE = f"""<div class="h-auto py-6 md:py-0 md:h-[32rem] w-full md:w-[25rem] md:shrink-0 bg-gradient-to-r from-[#3533CD] to-[#0A0A24] rounded-[15px] p-4 md:p-8 flex flex-col items-center justify-center text-center text-white">
            <h2 class="font-helvetica-now font-bold text-2xl md:text-4xl leading-tight mb-3 md:mb-4">Leadership Spotlight</h2>
            <div class="flex flex-col items-center gap-3 md:gap-4">
                <div class="w-[100px] h-[100px] sm:w-[120px] sm:h-[120px] md:w-[160px] md:h-[160px] bg-[url({data.get('leader_image_url','')})] bg-cover bg-center rounded-full shrink-0"></div>
                <div class="flex flex-col items-center">
                    <h3 class="font-jakarta font-normal text-lg sm:text-xl md:text-2xl leading-tight mb-1">{data.get('leader_name','')}</h3>
                    <p class="font-jakarta font-normal text-base md:text-lg leading-tight mb-2 md:mb-3">{data.get('leader_designation','')}</p>
                    <p class="font-jakarta font-normal text-sm md:text-base leading-relaxed mb-3 md:mb-4 max-w-xs md:max-w-sm">
                       {data.get('leader_desc','')}
                    </p>
                    <a href="{data.get('web_stories_url','')}" class="inline-block hover:opacity-90 transition-opacity">
                        <img src="/static/images/webstories_button.png" alt="Web Stories" class="w-[110px] h-[31px] md:w-[140px] md:h-[40px]">
                    </a>
                </div>
            </div>
        </div>"""
    return LEADERSHIP_SPOTLIGHT_TEMPLATE