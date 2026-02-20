def get_horizontal_ad_banner(data: dict) -> str:

    BANNER_TEMPLATE = f"""
    <a href="{data.get('href_url','')}" class="block w-full h-[120px] sm:h-[160px] md:h-[236px] mb-4 mt-4">
            <img src="{data.get('image_url','')}" alt="Advertisement" class="w-full h-full object-cover" />
        </a>
    """

    return BANNER_TEMPLATE


def get_1x1_ad_banner(data: dict) -> str:

    BANNER_TEMPLATE = f"""
    <a href="{data.get('href_url','')}" class="w-full md:w-1/2 h-80 md:h-auto bg-cover bg-center rounded-[15px] mt-4 md:mt-0 bg-[url({data.get('image_url','')})]"></a>
    """

    return BANNER_TEMPLATE
