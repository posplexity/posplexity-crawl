"""
This example demonstrates how to run 10 concurrent tasks,
each of which processes its assigned URLs sequentially in one browser session,
and then saves the crawling result (markdown) to a file named by {title}.md 
(or fallback to the URL path if title is missing or "postech").

Additionally:
- We skip crawling if the MD file already exists (avoid re-crawling).
- We store the MD after each chunk in parallel execution.
"""

import asyncio
import json
import os
import re
from typing import List
from math import ceil

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# -----------------------------------------------------------------------------
# 1) 파일 이름 관련 유틸
# -----------------------------------------------------------------------------
def sanitize_filename(name: str) -> str:
    """
    파일 이름으로 사용할 수 없는 문자들을 '_' 로 치환
    Windows, macOS, Linux 등에서 문제가 될 수 있는 문자 처리.
    """
    return re.sub(r'[\\/:*?"<>|]+', '_', name)

def pick_filename(title: str, url: str) -> str:
    """
    1) title이 없거나 'postech' (대소문자 무관)이면,
       'https://...' 이후 부분을 파일명으로 사용.
    2) 그 외에는 title 사용.
    """
    if not title or title.strip().lower() == "postech":
        # URL에서 scheme(https://, http:// 등) 제거
        no_scheme = re.sub(r'^https?://', '', url, flags=re.IGNORECASE)
        filename = no_scheme
    else:
        filename = title

    return sanitize_filename(filename) + ".md"

def is_already_crawled(url: str) -> bool:
    """
    md_output 폴더 내에, URL에 해당하는 MD 파일이 이미 존재하면 True 반환
    """
    # 이 예제에서는 title을 강제로 ""(공백)으로 처리해서 URL 기반으로만 파일명을 만듭니다.
    # 혹은 crawl4ai에서 title을 미리 추출하지 않고, 재크롤링도 않고 싶다면
    # "fallback" 로직만 써도 무방합니다.
    filename = pick_filename("", url)  # title=""로 강제하여 URL 기반 파일명
    filepath = os.path.join("md_output", filename)
    return os.path.exists(filepath)

# -----------------------------------------------------------------------------
# 2) 크롤링 함수들 (예제)
# -----------------------------------------------------------------------------
async def crawl_parallel_with_sequential(urls: List[str], concurrency: int = 10):
    """
    10개의 동시(병렬) 크롤링 작업을 실행하되,
    각 작업(Chunk)은 자기 할당량의 URL을 '순차'로 처리.
    
    - 이미 md_output 폴더에 해당 URL의 파일이 있으면 크롤을 생략.
    - 크롤 결과는 {title or url}.md 형태로 즉시 저장.
    """

    print(f"\n=== Parallel Crawling with {concurrency} tasks, each sequential ===")

    browser_config = BrowserConfig(headless=True)
    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(),
    )

    # URL을 concurrency 덩어리로 나눔
    chunk_size = ceil(len(urls) / concurrency)
    chunks = []
    for i in range(0, len(urls), chunk_size):
        chunks.append(urls[i : i + chunk_size])

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    async def crawl_chunk_sequentially(chunk_urls: List[str], session_id: str):
        """
        한 CHUNK(배치) 안의 URL을 순차적으로 처리.
        이미 MD가 있으면 스킵.
        """
        results = []
        for url in chunk_urls:
            if is_already_crawled(url):
                print(f"[{session_id}] Already have MD for {url}, skipping...")
                # 결과에 None 넣어서 나중에 별도 처리해도 되지만, 여기서는 단순히 pass
                results.append((url, None))
                continue

            # 실제 크롤링
            result = await crawler.arun(
                url=url,
                config=crawl_config,
                session_id=session_id,
            )
            results.append((url, result))

            # 크롤 성공 시 바로 MD 저장
            if result and result.success:
                print(f"[{session_id}] Crawled {url} -> length={len(result.markdown_v2.raw_markdown)}")

                # 여기서는 title 대신 ""로 해서 URL기반 파일명만 사용
                filename = pick_filename("", url)
                os.makedirs("md_output", exist_ok=True)
                save_path = os.path.join("md_output", filename)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(result.markdown_v2.raw_markdown)
            else:
                print(f"[{session_id}] Failed {url}")

        return results

    try:
        # 10개 chunk를 병렬로 처리
        tasks = []
        for idx, chunk in enumerate(chunks):
            session_id = f"chunk_session_{idx}"
            task = asyncio.create_task(crawl_chunk_sequentially(chunk, session_id))
            tasks.append(task)

        # 모든 chunk 결과가 완료될 때까지 기다림
        chunk_results = await asyncio.gather(*tasks, return_exceptions=True)

        # (선택) chunk_results 안에 Exception이 있으면 로깅
        for idx, result in enumerate(chunk_results):
            if isinstance(result, Exception):
                print(f"Error in chunk {idx}: {result}")
            else:
                # result 는 [(url, SingleCrawlResult or None), ...]
                # 이미 저장 로직을 chunk 내부에서 수행했으므로
                # 여기서는 추가 로직이 필요 없다면 pass
                pass

    finally:
        await crawler.close()


# -----------------------------------------------------------------------------
# 3) 메인 함수: urls.json에서 로드 후 실행
# -----------------------------------------------------------------------------
async def main():
    with open("data/urls.json", "r", encoding="utf-8") as f:
        urls = json.load(f)
    
    # 원하는 만큼만 사용 가능 (예: 테스트로 50개)
    # urls = urls[:50]
    
    # 실행
    await crawl_parallel_with_sequential(urls, concurrency=10)


# -----------------------------------------------------------------------------
# 4) 실행부
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())