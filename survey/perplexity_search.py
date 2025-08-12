import os
import copy
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("SONAR_API_KEY")

api_url = "https://api.perplexity.ai/chat/completions"
headers = {
    "accept": "application/json",
    "authorization": f"Bearer {api_key}",
    "content-type": "application/json"
}

# Normal
normal_base_payload = {
    # "model": "sonar",
    "messages": [
        {"role": "system", "content":"""You are a helpful AI assistant.
Your task is to review all retrieved search results and synthesize them into a single, coherent answer.
Rules:
1. Base your answer only on the provided search results.
2. Merge overlapping information and resolve any contradictions using the most credible sources.
3. Present the answer in a clear, well-structured format with concise language.
4. If relevant, include key facts, dates, figures, and context to support the explanation.
5. If search results do not fully answer the question, explicitly state the missing information."""},
        # {"role": "user", "content": "What is dark vessel detection?"}
    ],
    "stream": False,
}

# Academic
academic_base_payload = {
    **normal_base_payload,
    "search_mode": "academic",
    "search_after_date_filter": "8/1/2023",
    "web_search_options": {"search_context_size": "high"},
    # "search_domain_filter": [
    #     "ieee.org",
    # ]
}

def set_payload(model: str, user_input: str, search_mode: str):
    if search_mode == "normal":
        payload = copy.deepcopy(normal_base_payload)
    elif search_mode == "academic":
        payload = copy.deepcopy(academic_base_payload)

    payload["model"] = model
    payload["messages"].append({"role": "user", "content": user_input})

    return payload

def get_response(payload:dict):
    try:
        response = requests.post(api_url, headers=headers, json=payload)

        # 檢查 HTTP 狀態碼
        if response.status_code != 200:
            print(f"HTTP Error {response.status_code}: {response.reason}")
            print(f"Response text: {response.text[:500]}")  # 顯示前500個字符
            return None
        
        # 檢查回應是否為空
        if not response.text.strip():
            print("Error: Empty response received")
            return None
        
        # 嘗試解析 JSON
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Response content: {response.text[:500]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None

def save_result(response, search_results):
    with open("survey/result/response.md", "w", encoding="utf-8") as f:
        f.write(response['choices'][0]['message']['content'])

    with open("survey/result/search_results.json", "w", encoding="utf-8") as f:
        json.dump(search_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import json

    payload = set_payload("sonar", "What is dark vessel detection?", "academic")

    print("Payload:")
    for key, value in payload.items():
        print(f"{key}: {value}")

    response = get_response(payload)
    print(f"\nResponse:\n{response['choices'][0]['message']['content']}")

    # citations = response.get("citations", [])
    # print(f"\nTotal {len(citations)} Citations:")
    # for citation in citations:
    #     print(citation)

    search_results = response.get("search_results", [])
    print(f"\nTotal {len(search_results)} Search Results:")
    for search_result in search_results:
        print(json.dumps(search_result, indent=2, ensure_ascii=False))