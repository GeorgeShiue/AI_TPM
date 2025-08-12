import json
import asyncio
import time
import os
import shutil

from perplexity_search import set_payload, get_response, get_unique_search_results, save_response, save_search_results
from crawl4ai_crawler import parallel_crawling
from llm_ask import generate_questions

RESULT_DIR = "survey/result"
MD_DOCS_DIR = os.path.join(RESULT_DIR, "md_docs")
RESPONSE_MD_DIR = os.path.join(RESULT_DIR, "response.md")
SEARCH_RESULTS_JSON_DIR = os.path.join(RESULT_DIR, "search_results.json")

def single_research(input: str, search_mode: str):
    start_time = time.time()

    # Set payload and get response
    payload = set_payload("sonar", input, search_mode)
    response = get_response(payload)
    response_content = response['choices'][0]['message']['content']
    print(f"\nResponse:\n{response_content}")

    # List search results
    current_search_results = response.get("search_results", [])
    # print(f"\nTotal {len(current_search_results)} Search Results:")
    # for search_result in current_search_results:
    #     print(json.dumps(search_result, indent=2, ensure_ascii=False))

    # Get unique search results
    with open(SEARCH_RESULTS_JSON_DIR, "r", encoding="utf-8") as f:
        existing_search_results = json.load(f)
    unique_search_results = get_unique_search_results(current_search_results, existing_search_results)
    print(f"\nTotal {len(unique_search_results)} Unique Search Results:")
    for unique_search_result in unique_search_results:
        print(json.dumps(unique_search_result, indent=2, ensure_ascii=False))

    # Save response and search results
    save_response(input, response, current_search_results, RESPONSE_MD_DIR)
    save_search_results(existing_search_results, unique_search_results, SEARCH_RESULTS_JSON_DIR)
    print("\nResponse and search results saved successfully.\n")

    # Parallel crawling on search results
    asyncio.run(parallel_crawling(unique_search_results, MD_DOCS_DIR))

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nSingle searching time: {elapsed_time:.2f} seconds\n")

    return response_content

if os.path.exists(RESULT_DIR):
    shutil.rmtree(RESULT_DIR, ignore_errors=True)
os.makedirs(RESULT_DIR, exist_ok=True)

os.makedirs(MD_DOCS_DIR, exist_ok=True)
with open(RESPONSE_MD_DIR, "w", encoding="utf-8") as f:
    f.write("")
with open(SEARCH_RESULTS_JSON_DIR, "w", encoding="utf-8") as f:
    json.dump([], f, indent=2, ensure_ascii=False)

# * 使用者參數
user_input = "What is dark vessel detection?"
search_mode = "academic"
target_md_docs_count = 50

start_time = time.time()

questions = [user_input]
index = 1
for question in questions:
    print(f"Question {index}: {question}")
    search_response_content = single_research(input=question, search_mode=search_mode)
    questions.pop(0)

    new_questions = generate_questions(search_response_content)
    questions.extend(new_questions)
    print(f"\nNew Questions:")
    for new_question in new_questions:
        print(f" - {new_question}")
    print("\n" + "=" * 50 + "\n")

    index += 1
    # if index > 10:
    #     break

    md_docs_count = len(os.listdir(MD_DOCS_DIR))
    if md_docs_count >= target_md_docs_count:
        break

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Research time: {elapsed_time:.2f} seconds")

md_docs_count = len(os.listdir(MD_DOCS_DIR))
print(f"Total MD docs: {md_docs_count}")