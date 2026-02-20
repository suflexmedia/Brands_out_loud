import aiohttp
import re
import html
import asyncio
import random


async def get_bbc_news_async():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://feeds.bbci.co.uk/news/world/rss.xml') as response:
            text = await response.text()
            pattern = re.compile(r"<item>.*?</item>", re.DOTALL)
            xml_content = pattern.findall(text)[0]
            return {
                'title': html.unescape(re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', xml_content).group(1)),
                'description': html.unescape(re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', xml_content).group(1)),
                'link': re.search(r'<link>(.*?)</link>', xml_content).group(1),
                'pub_date': re.search(r'<pubDate>(.*?)</pubDate>', xml_content).group(1).split(', ')[1][:11],
                'media_url': re.search(r'<media:thumbnail width="(\d+)" height="(\d+)" url="(.*?)"/>', xml_content).group(3) if re.search(r'<media:thumbnail width="(\d+)" height="(\d+)" url="(.*?)"/>', xml_content) else None,
                'platform': 'BBC News',
            }

async def get_nyt_news_async():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml') as response:
            text = await response.text()
            pattern = re.compile(r"<item>.*?</item>", re.DOTALL)
            xml_content = pattern.findall(text)[0]
            return {
                'title': html.unescape(re.search(r'<title>(.*?)</title>', xml_content).group(1) if re.search(r'<title>(.*?)</title>', xml_content) else None),
                'description': html.unescape(re.search(r'<description>(.*?)</description>', xml_content).group(1) if re.search(r'<description>(.*?)</description>', xml_content) else None),
                'link': re.search(r'<link>(.*?)</link>', xml_content).group(1) if re.search(r'<link>(.*?)</link>', xml_content) else None,
                'pub_date': re.search(r'<pubDate>(.*?)</pubDate>', xml_content).group(1).split(', ')[1][:11],
                'media_url': re.search(r'<media:content.*?url="(.*?)"', xml_content).group(1) if re.search(r'<media:content.*?url="(.*?)"', xml_content) else None,
                'platform': 'New York Times',
            }

async def get_nbc_news_async():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://feeds.nbcnews.com/nbcnews/public/news') as response:
            text = await response.text()
            pattern = re.compile(r"<item>.*?</item>", re.DOTALL)
            xml_content = pattern.findall(text)[0]
            return {
                'title': html.unescape(re.search(r'<title>(.*?)</title>', xml_content).group(1) if re.search(r'<title>(.*?)</title>', xml_content) else None),
                'description': html.unescape(re.search(r'<description>(.*?)</description>', xml_content).group(1) if re.search(r'<description>(.*?)</description>', xml_content) else None),
                'link': re.search(r'<link>(.*?)</link>', xml_content).group(1) if re.search(r'<link>(.*?)</link>', xml_content) else None,
                'pub_date': re.search(r'<pubDate>(.*?)</pubDate>', xml_content).group(1).split(', ')[1][:11],
                'media_url': re.search(r'<media:thumbnail url="(.*?)"', xml_content).group(1) if re.search(r'<media:thumbnail url="(.*?)"', xml_content) else (re.search(r'<media:content url="(.*?)"', xml_content).group(1) if re.search(r'<media:content url="(.*?)"', xml_content) else None),
                'platform': 'NBC News',
            }

async def get_ndtv_news_async():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://feeds.feedburner.com/ndtvnews-top-stories') as response:
            text = await response.text()
            pattern = re.compile(r"<item>.*?</item>", re.DOTALL)
            xml_content = pattern.findall(text)[0]
            
            return {
                'title': html.unescape(re.search(r'<title>\s*<!\[CDATA\[\s*(.*?)\s*\]\]>\s*</title>', xml_content).group(1)) if re.search(r'<title>\s*<!\[CDATA\[\s*(.*?)\s*\]\]>\s*</title>', xml_content) else None,
                'description': html.unescape(re.search(r'<description>\s*<!\[CDATA\[\s*(.*?)\s*\]\]>\s*</description>', xml_content).group(1)) if re.search(r'<description>\s*<!\[CDATA\[\s*(.*?)\s*\]\]>\s*</description>', xml_content) else None,
                'link': html.unescape(re.search(r'<link>\s*<!\[CDATA\[\s*(.*?)\s*\]\]>\s*</link>', xml_content).group(1)) if re.search(r'<link>\s*<!\[CDATA\[\s*(.*?)\s*\]\]>\s*</link>', xml_content) else None,
                'pub_date': re.search(r'<pubDate><!\[CDATA\[(.*?)]]></pubDate>', xml_content).group(1).split(', ')[1][:11],
                'media_url': re.search(r'<media:content url="(.*?)"', xml_content).group(1) if re.search(r'<media:content url="(.*?)"', xml_content) else None,
                'platform': 'NDTV News',
            }



async def get_trending_news():
    tasks = [
        get_bbc_news_async(),
        get_nyt_news_async(),
        get_nbc_news_async(),
        get_ndtv_news_async()
    ]
    random.shuffle(tasks)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    mm = ''
    for i in results[:3]:
        temp = f"""<article class="flex flex-col md:flex-row gap-4 md:w-full border-b border-white/30 pb-3.5"> 
                <div class="w-full md:w-[289.2px] h-[150px] bg-cover bg-center rounded-[6px] bg-[url({i['media_url']})] flex-shrink-0"></div>
                <div class="flex flex-col justify-center">
                 <div class="w-auto md:w-[137.18px] h-[10px] font-jakarta font-medium text-[10px] leading-[1] text-white/60 mb-2">{i['platform']+" - "+i['pub_date']}</div>
                 <a href="{i['link']}" class="hover:underline">
                     <h3 class="w-auto md:w-auto h-auto font-jakarta font-normal text-lg leading-[136.9%] text-white mb-2">{i['title'] if len(i['title'])<85 else i['title'][:85]+"..."}</h3>
                 </a>
                 <p class="w-auto md:w-auto h-auto font-jakarta font-normal text-xs leading-[123.9%] text-white">{i['description'] if len(i['description'])<110 else i['description'][:110]+"..."}</p> 
                </div>
            </article>\n"""
        mm += temp
        print(i)
    return mm 

