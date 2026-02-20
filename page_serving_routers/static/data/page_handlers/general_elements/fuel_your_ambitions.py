def get_fuel_your_ambitions_html() -> str:

    FUEL_YOUR_AMBITIONS_TEMPLATE = f"""
    <section class="w-full aspect-[120/47] relative bg-contain bg-no-repeat bg-center bg-[url(/static/images/fuel_ambition.png)] mb-[-1rem]">
        
        <a href="/magazine_page" class="absolute bottom-[18%] left-[50%] -translate-x-1/2 w-[20%] max-w-[300px] hover:opacity-90 transition-opacity">
            <img src="/static/images/checkout_magazine_button.png" alt="Footer Action Button" class="block w-full h-auto">
        </a>
    </section>"""

    return FUEL_YOUR_AMBITIONS_TEMPLATE
