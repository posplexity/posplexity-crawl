from common.config.config import PROMPT_BASE_PATH
from common.types.types import ImportantInformation
# from src.utils.utils import async_wrapper
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy

import logging as logger
import asyncio, json, os


async def walk(url: list[str], extraction_strategy: LLMExtractionStrategy):
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url=url[0],
            extraction_strategy=extraction_strategy,
            cache_mode=CacheMode.BYPASS
        )
    return result


def process_walk(depth: int, url: list[str], model: str="deepseek/deepseek-chat"):
    instruction = """
        You are an advanced web-crawling specialist. Your task is to look at the current webpage and identify any further pages that can be accessed from it—essentially the next level of depth. For each link on this page that leads to additional content, extract the link text (title) and the exact URL as it appears.

        Key points and requirements:
            1.	Immediate Depth Only: Do not perform a full multi-level graph traversal. Only collect links that are directly reachable from the current page.
        2.	Exact Titles: Preserve the exact text or label used for each link—no abbreviations or changes. Use the most relevant title for each link. (Do not use overly broad titles.)
        3.	Exact URLs: Capture the URL or href exactly as it is on the page.
        4.	Duplicates & Variations: If the same link appears more than once or if there are variations in the displayed text for the same link, record them separately.
        5.	Structured Output: Provide the data in a format (e.g., a list or JSON) that clearly shows each link’s text/title and its URL. If a link is nested within a particular section of the page, note that context briefly.
        6.  Exclude non-essential information such as English/Korean options, SNS links, LOGIN site, email-rejection, etc.

        Goal: To retrieve a concise but thorough list of links on the current webpage—each entry including the link text and the exact URL—enabling further analysis or crawl steps later on.
    """
    from pydantic import BaseModel, Field
    class ImportantInformationForPostech(BaseModel):
        title: str #= Field(..., description="Title of important information (postech students must know this)")
        links: str #= Field(..., description="Links of information (postech students must know this)")



    prompt_path = PROMPT_BASE_PATH + f"/depth_1.json" if depth == 1 else PROMPT_BASE_PATH + f"/depth_n.json"
    with open(prompt_path, "r") as f:
        prompt = json.load(f)["system_prompt"]

    # breakpoint()
    prompt = instruction

    extraction_strategy = LLMExtractionStrategy(
        provider=model,
        base_url="https://api.deepseek.com/v1",
        api_token=os.getenv("DEEPSEEK_API_KEY"),
        schema=ImportantInformationForPostech.schema(),
        extraction_type="schema",
        instruction=instruction
    )
    
    logger.info(f"Start walking for depth {depth}... / links : {len(url)}")
    walked_results = asyncio.run(walk(url=url, extraction_strategy=extraction_strategy))
    logger.info(f"End walking for depth {depth}...")

    return walked_results
