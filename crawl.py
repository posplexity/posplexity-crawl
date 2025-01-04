from src.main.crawl import process_crawl
from common.config.config import BASE_URL
from tqdm import tqdm
import os, json
import urllib.parse

def get_folder_and_filename(url: str) -> tuple[str, str]:
    """URL을 기반으로 저장할 폴더와 파일 이름을 결정"""
    try:
        decoded_url = urllib.parse.unquote(url)
    except:
        decoded_url = url
    
    if url.startswith(BASE_URL):
        path_part = decoded_url.replace(BASE_URL, "").strip("/")
    else:
        # 다른 도메인의 경우 도메인을 폴더명으로 사용
        parsed = urllib.parse.urlparse(decoded_url)
        domain = parsed.netloc.replace(".", "_")
        path_part = f"{domain}/{parsed.path.strip('/')}"
    
    # 긴 경로는 100자로 제한
    if len(path_part) > 100:
        path_part = path_part[:100]
    
    folder = path_part.split("/")[0]
    filename = path_part.replace("/", "_") + ".md"
    
    return folder, filename

def main(path:str):
    with open(path, "r") as f:
        urls = json.load(f)

    # TODO : REMOVE BEFORE PRODUCTION
    # urls = urls[500:600]
    crawled = process_crawl(urls=urls, key_selector="#primary")

    # 실패한 URL들을 저장할 리스트
    failed_urls = []

    for url, md in tqdm(zip(urls, crawled), total=len(urls)):
        if md is None or len(md) < 100:
            failed_urls.append(url)
            continue
            
        folder, filename = get_folder_and_filename(url)
        folder_path = os.path.join("./data/staged", folder)
        os.makedirs(folder_path, exist_ok=True)

        save_path = os.path.join(folder_path, filename)
        with open(save_path, "w", encoding="utf-8") as f: 
            f.write(md)

    # 실패한 URL들을 JSON 파일로 저장
    if failed_urls:
        failed_path = os.path.join("./data", "failed_urls.json")
        with open(failed_path, "w", encoding="utf-8") as f:
            json.dump(failed_urls, f, ensure_ascii=False, indent=2)
        print(f"\n크롤링 실패한 URL 수: {len(failed_urls)}")
        print(f"실패한 URL들이 {failed_path}에 저장되었습니다.")

if __name__ == "__main__":
    main("data/urls.json")  


