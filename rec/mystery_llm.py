"""
This module is used to authenticate the user for GoCaaS and get the token
"""
import os
import requests
import async_lru
import logging
from typing import Any

from mystery_api import aiohttp_post
from fastapi import HTTPException

def get_exact_aftermarket_domain_info(
    domain_name: str,
    api_key: str="mystbox",
    req_id: str=None,
    user_agent: str=None,
) -> dict:
    """
    Calls the Aftermarket Exact Match API to retrieve information about a specific domain
    from the aftermarket (afternic and auction) listings, such as afternic or auction, price, fast transfer, and auction/listing expiry date, ...
    Returns data if the domain is found, or an empty response otherwise.

    Sends a GET request to `/exact/{domainName}`.

    ### Path Parameters:
        - domain_name (str): The exact domain name to search for (e.g., "example.com").

    ### Headers:
        - X-GDFindAM-APIKey (str): API key used for authentication.
        - X-GDFindAM-ReqId (str): Unique request ID for tracing and debugging.
        - X-GDFindAM-UserAgent (str): User agent string describing the calling client.

    ### Returns:
        - dict: Parsed JSON response with domain details, conforming to `ExactResp` schema.

    ### Raises:
        - requests.HTTPError: If the request fails with a 4xx or 5xx status code.
    """
    AFTERMARKET_URL = "http://haproxy.uswest.prod.domain.gdg:8080/v4/aftermarket/find"
    url = f"{AFTERMARKET_URL}/exact/{domain_name}"
    headers = {
        "X-GDFindAM-APIKey": api_key,
        "X-GDFindAM-ReqId": req_id,
        "X-GDFindAM-UserAgent": user_agent,
    }
    headers = {k: v for k, v in headers.items() if v is not None}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as e:
        if response.status_code == 404:
            return {}
        else:
            raise e
    return response.json()


@async_lru.alru_cache(maxsize=1024)
async def llm_call_domain_info(domain_name):
    domain_details = get_exact_aftermarket_domain_info(domain_name)


    prompt = f"""
    You are a data analyst at GoDaddy. Your task is to generate a precise and professional analytical summary for a domain won by a GoDaddy customer as part of the Mystery Domain Box program.

You are provided with a single domain name: {domain_name} and following details (if any, traffic is in majestic, citation, flow, or backlink fields): {domain_details}

Your goal is to evaluate the domain across multiple key attributes using internal data available, such as traffic metrics, keyword value, structural features (e.g., SLD length), and branding potential.
  
  ## Output Format:
Return only the summary using the structured JSON format ith the keys as the attributes and the values as the corresponding summaries. No intro text or markdown formatting.


---

### Summary Template:

- **Domain Name**: 

- **Traffic & Engagement**:
                Briefly describe monthly traffic volume (if available), bounce rate, or past performance patterns. keep the most positive number with a positive tone
                _If data is unavailable, remove this field_

- **Keyword & SEO Value**:
                Comment on the relevance, popularity, and CPC value (if known) of the keywords used in the domain.
                Highlight SEO friendliness or competitive advantages in search.

- **SLD Structure & Length**:
          Discuss the second-level domain (SLD), its character count, clarity, and potential for typos.
          Mention if it's short, memorable, or dictionary-based.

- **Brandability & Positioning**:
                     Assess how easy the domain is to pronounce, spell, and remember.
                     Indicate if it sounds premium, trendy, trustworthy, or aligns with a niche market.

- **Trustworthiness & TLD**:
                        Evaluate the top-level domain (e.g., .com), historical usage, or security posture (HTTPS, no malicious history).

---

## Constraints:
- Do **not** include shopper ID or internal references.
- Do **not** speculate beyond what data supports.
- The tone should be clear, confident, and business-appropriate.
- Use concise sentences with meaningful insights (avoid fluff).
    """

    caas_promt = {
        "prompts": [
            # {
            #     "from": "system",
            #     "content": f"you are ",
            # },
            {
                "from": "user",
                "content": prompt,
            },
        ],
        "provider": "openai_chat",
        "providerOptions": {"model": "gpt-4o", "temperature": 0.5},
        # "isPrivate": True
    }

    with open(".jwt", "r") as f:
        token = f.read().strip()

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"sso-jwt {token}",
    }

    llm_url = "https://caas.api.dev-godaddy.com/v1/prompts"
    try:
        response = await aiohttp_post(llm_url, headers=headers, payload=caas_promt)
    except Exception as e:
        logging.error(f"Error in LLM call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in LLM call: {str(e)}")

    cost = response["data"]["cost"] * 100
    res = response["data"]["value"]["content"]

    return res


if __name__ == "__main__":
    domain_name = "dadm.com"
    print(get_exact_aftermarket_domain_info(domain_name))

    import asyncio
    res = asyncio.run(llm_call_domain_info(domain_name))
    print(res)