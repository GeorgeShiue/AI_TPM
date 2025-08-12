import json
import asyncio
import time
from perplexity_search import set_payload, get_response, save_result
from crawl4ai_crawler import parallel_crawling

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