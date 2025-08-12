import json
import asyncio
import time
from perplexity_search import set_payload, get_response, save_result
from crawl4ai_crawler import parallel_crawling
from llm_ask import generate_questions

def single_research(input):
    start_time = time.time()

    # Set payload and get response
    payload = set_payload("sonar", input, "academic")
    response = get_response(payload)
    response_content = response['choices'][0]['message']['content']
    print(f"\nResponse:\n{response_content}")

    # List search results
    search_results = response.get("search_results", [])
    print(f"\nTotal {len(search_results)} Search Results:")
    for search_result in search_results:
        print(json.dumps(search_result, indent=2, ensure_ascii=False))

    save_result(response, search_results)

    # Parallel crawling on search results
    asyncio.run(parallel_crawling(search_results))

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nSingle searching time: {elapsed_time:.2f} seconds\n")

    return response_content


start_time = time.time()

user_input = "What is dark vessel detection?"

index = 1
search_response_content = ""
questions = []

# TODO: 全自動化
while True:        
    if index == 1:
        questions = [user_input]
    else:
        questions = generate_questions(search_response_content)

    for question in questions:
        print(f"Question: {question}")
        search_response_content = single_research(question)

    index += 1
    if index > 2:
        break

end_time = time.time()
elapsed_time = end_time - start_time
print(f"\nResearch time: {elapsed_time:.2f} seconds\n")