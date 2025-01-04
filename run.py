from common.config.config import BASE_URL, POSTECH_HEADER
from src.main.walk import process_walk
from src.main.crawl import process_crawl
import os

def main(entry_url: str, max_depth: int):
    for i in range(1, max_depth+1):
        depth_dir = f"data/depth{i}"
        os.makedirs(depth_dir, exist_ok=True)

    result = process_walk(depth=1, url=[entry_url])
    breakpoint()
    result = process_crawl(url=[entry_url], key_selector="#primary")

    for depth in range(1, max_depth+1):
        depth_dir = f"data/depth{depth}"
        with open(f"{depth_dir}/result.md", "w") as f:
            f.write(result[depth-1])
    

    # for depth in range(2, max_depth+1):

    breakpoint()

def progress(urls: list[str]):
    """
    walking이 제대로 동작하지 않는 동안, parsing을 테스트하기 위한 함수
    """

    tmp = process_crawl(urls=urls, key_selector=None)
    tmp[0].replace(POSTECH_HEADER, "")
    with open("test2.md", "w") as f:
        f.write(tmp[0])

    breakpoint()

    for url, result in zip(urls, results):
        path_part = url.replace(BASE_URL, "").strip("/")
        folder = path_part.split("/")[0]
        filename = path_part.replace("/", "_") + ".md"
        
        folder_path = os.path.join("./data/staged", folder)
        os.makedirs(folder_path, exist_ok=True)
        
        save_path = os.path.join(folder_path, filename)
        save_path="/Users/huhchaewon/posplexity-crawl/data/staged/test.md"
        with open(save_path, "w", encoding="utf-8") as f: f.write(result)

    print("all processed")

if __name__ == "__main__":
    # urls = [c["links"] for c in crawled]
    urls = ["https://www.postech.ac.kr/academics/?p_id=59574#content"]
    progress(urls=urls)

    