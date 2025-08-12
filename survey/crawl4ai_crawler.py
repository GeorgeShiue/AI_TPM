import shutil
import os
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import aiofiles
import re

# TODO: 處理可能爬到空白的情況
async def crawl_single_url(crawler, url, title):
    try:
        run_conf = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        result = await crawler.arun(url=url, config=run_conf)
        
        if result.success:
            # 處理檔名
            safe_filename = re.sub(r'[^\w\s-]', '', title).strip()[:100]
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            filename = f"survey/result/md_docs/{safe_filename}.md"
            
            # 使用 aiofiles 進行異步文件寫入
            async with aiofiles.open(filename, "w", encoding="utf-8") as f:
                await f.write(result.markdown.raw_markdown)
            
            return {"status": "success", "title": title, "url": url}
        else:
            return {"status": "failed", "title": title, "url": url, "error": result.error_message}
    except Exception as e:
        return {"status": "error", "title": title, "url": url, "error": str(e)}

async def parallel_crawling(search_results):
    if os.path.exists("survey/result/md_docs"):
        shutil.rmtree("survey/result/md_docs")
    os.makedirs("survey/result/md_docs", exist_ok=True)

    browser_conf = BrowserConfig(headless=True)
    
    async with AsyncWebCrawler(config=browser_conf) as crawler:
        # 建立所有爬取任務
        tasks = [
            crawl_single_url(crawler, sr['url'], sr['title']) 
            for sr in search_results
        ]
        
        # 並行執行所有任務
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理結果
        for result in results:
            if isinstance(result, dict):
                if result["status"] == "success":
                    print(f"✅ Saved: {result['title']}")
                else:
                    print(f"❌ Failed: {result['title']} - {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ Exception: {result}")



if __name__ == "__main__":
    import json
    from perplexity_search import set_payload, get_response, save_result

    import time
    start_time = time.time()
    
    payload = set_payload("sonar", "What is dark vessel detection?", "academic")
    response = get_response(payload)
    print(f"\nResponse:\n{response['choices'][0]['message']['content']}")

    search_results = response.get("search_results", [])
    print(f"\nTotal {len(search_results)} Search Results:")
    for search_result in search_results:
        print(json.dumps(search_result, indent=2, ensure_ascii=False))

    save_result(response, search_results)

    asyncio.run(parallel_crawling(search_results))

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nTotal elapsed time: {elapsed_time:.2f} seconds")