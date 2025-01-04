from common.config.config import PROMPT_BASE_PATH, BASE_URL
# from src.utils.utils import async_wrapper
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy

import logging as logger
import asyncio

async def crawl(links: str, key_selector: str):
    async with AsyncWebCrawler(verbose=True, headless=False) as crawler:
        task = [
            crawler.arun(
                url=link,
                cache_mode=CacheMode.BYPASS,
                css_selector=key_selector if link.startswith(BASE_URL) else None,
                timeout=600000
            )
            for link in links
        ]
        result = []
        for t in task:
            result.append(await t)
        return result
        result = await asyncio.gather(*task)
    result = [r.markdown for r in result]
    return result

def process_crawl(urls: list[str], key_selector: str):
    result = asyncio.run(crawl(links=urls, key_selector=key_selector))
    return result
