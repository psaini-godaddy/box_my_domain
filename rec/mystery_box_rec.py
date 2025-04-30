from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
app = FastAPI(title="MysteryBox rec api", version="0.1")

import asyncio
import async_lru
import aiohttp
import logging
import numpy as np
from scipy.optimize import root_scalar
import time

from aiohttp import ClientTimeout

# from utils import api
# from models import ShopperInfo
from fastapi import HTTPException


config = {
  "find_host": "http://haproxy.uswest.prod.domain.gdg:8004",
  "find_aftermarket_host": "http://haproxy.uswest.prod.domain.gdg:8080",
  "shoper_rec_host": "http://haproxy.uswest.prod.domain.gdg:8910",
  "pgen_host": "http://haproxy.uswest.prod.domain.gdg:8094"
}


async def aiohttp_post(url, headers=None, payload=None, timeout=ClientTimeout(total=10)):
    async with aiohttp.ClientSession(timeout=timeout, raise_for_status=True) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            return await response.json()

async def aiohttp_get(url, headers=None, timeout=ClientTimeout(total=10)):
    async with aiohttp.ClientSession(timeout=timeout, raise_for_status=True) as session:
        async with session.get(url, headers=headers) as r:
            return await r.json()


@async_lru.alru_cache(maxsize=1024, ttl=86400)
async def run_pgen(
    query,
    shopper_id: int | str,
    limit: int = 25,
    mode: str = "fastvec",
):
    prices = {"ai": 89.99, "com": 11.99, "org": 9.99, "net": 12.99}

    find_query = (
        config["pgen_host"]
        + "/v1/pgen/getRecommendations?api_key=hackathon&mode={mode}&query={query}&shopper_id={shopper}&num_results={limit}"
    )

    fq = find_query.format(
        query=query,
        shopper=shopper_id,
        mode=mode,
        limit=limit,
    )
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    try:
        response = await aiohttp_get(fq, headers)
    except Exception as e:
        logging.error(f"Error in Find call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in pgen call: {str(e)}")

    doms = {}
    for c in response:
        dom = c["domain"]
        if not recommendation_check(dom, "pgen"):
            continue
        tld = dom.split(".")[-1]
        if tld not in prices:
            continue
        doms[dom] = prices[tld]
    return doms


@async_lru.alru_cache(maxsize=1024, ttl=86400)
async def run_find_api(
    query,
    shopper_id: int | str,
    limit: int = 25,
    skip_ads: bool = True,
    max_price=None
):
    find_query = (
        config["find_host"]
        + "/v3/name/find?q={query}&server_currency={server_currency}&pagination_size={limit}&user_shopper_id={shopper}"
        "&user_country_site={country_site_code}&user_language={device_language_setting_code}"
        "&geo_country_code={country_code}"
    )

    if skip_ads:
        find_query += "&debug_config=no_ads%3Bno_logging"
    else:
        find_query += "&debug_config=no_logging"

    if max_price is not None:
        find_query += f"&max_price={max_price}"

    fq = find_query.format(
        query=query,
        shopper=shopper_id,
        limit=limit,
        server_currency="USD",
        country_site_code="www",
        device_language_setting_code="en-us",
        country_code="us"
    )
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-GDFind-APIKey": "find_portfolio_rec",
    }
    try:
        response = await aiohttp_get(fq, headers)
    except Exception as e:
        logging.error(f"Error in Find call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Find call: {str(e)}")

    doms = {}
    spins = response["domains"]
    for c in spins:
        if not recommendation_check(c["fqdn"], c["match_source"]):
            continue
        if c.get("is_ad", False) and skip_ads:
            continue

        if "salePrice" in c["price_info"] and c['domain_source'] not in ["premium", "auctions"]:
            lp = c["price_info"]["salePrice"]
        elif "listPrice" in c["price_info"] and c['domain_source'] in ["premium", "auctions"]:
            lp = c["price_info"]["listPrice"]
        else:
            lp = None
        if lp == 78.9:
            lp = None

        if lp is None:
            if c["inventory"] in ["available_for_registration", "extensions"]:
                lp = 11.99
            else:
                continue
        doms[c["fqdn"]] = lp
    exact = response["exact_domain"]
    if exact["is_purchasable"]:
        if "price" in exact:
            doms[exact["fqdn"]] = exact["price"]
    return doms

def recommendation_check(domain: str, match_source: str = "") -> bool:
    """
    Check if the domain meets certain recommendation criteria
    Args:
        domain (str): The domain to check
    Returns:
        bool: True if the domain meets the criteria, False otherwise
    """
    # Example criteria: domain should not contain numbers and should be less than 42 characters
    if len(domain) > 42:
        return False
    if domain.count("-") >= 3:
        return False
    if "apireseller" in domain and "-" in domain:
        return False
    if match_source.startswith("pgen"):
        if "domain" in domain:
            return False
        if "number" in domain:
            return False
        if "numeric" in domain:
            return False
    return True

@async_lru.alru_cache(maxsize=1024, ttl=86400)
async def run_shopper_rec(shopper_id: int | str, mode: str = "find_conversational"):

    conv_query = (
        config["shoper_rec_host"] + "/v1/recommendation?shopper_id={shopper_id}&find_api={mode}&limit=20"
    )
    cq = conv_query.format(
        shopper_id=shopper_id.strip().lower(),
        mode=mode.strip().lower(),
    )
    headers = {
        "Content-Type": "application/json",
    }
    try:
        cresponse = await aiohttp_get(
            cq,
            headers=headers,
        )
    except Exception as e:
        logging.error(f"Error in Conv call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Conv call: {str(e)}")

    doms = {}
    for c in cresponse["detailed_results"]:
        if not recommendation_check(c["domain"]):
            continue
        if c["type"] in ["auction", "premium"] and "price" not in c:
            continue
        doms[c["domain"]] = c.get("list_price", 11.99)  # simply assume the price is 11.99 for primary names if no pricing info
    return doms

@async_lru.alru_cache(maxsize=1024, ttl=86400)
async def run_aftermarket_api(
    query,
    shopper_id: int | str,
    limit: int = 20
):
    aftermarket_query = (
        config["find_aftermarket_host"]
        + "/v4/aftermarket/find/recommend?query={query}&shopperId={shopper}&paginationSize={count}&useSemanticSearch=true"
    )
    headers = {
        "Content-Type": "application/json",
    }

    aq = aftermarket_query.format(query=query, shopper=shopper_id, count=limit)
    try:
        aresponse = await aiohttp_get(aq, headers=headers)
    except Exception as e:
        logging.error(f"Error in Aftermarket call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Aftermarket call: {str(e)}")

    doms = {}
    for c in aresponse["results"]:
        if not recommendation_check(c["fqdn"]):
            continue
        else:
            if "afternic" in c:
                price = c["afternic"]["buy_now_price"]
            else:
                price = c["auction"]["auction_price"]
            doms[c["fqdn"]] = price
    return doms

@async_lru.alru_cache(maxsize=1024, ttl=86400)
async def run_conversational_api(query, shopper_id: int | str):

    conv_query = (
        config["find_host"] + "/v4/name/recommend?"
        "req_id={req_id}&user_country_site={country_site_code}&user_language={device_language_setting_code}"
        "&geo_country_code={country_code}"
        "&server_currency={server_currency}&"
        "user_shopper_id={shopper_id}&debug_config=no_logging"
    )
    cq = conv_query.format(
        req_id=int(time.time()) * 1000,
        shopper_id=shopper_id,
        server_currency="USD",
        country_site_code="www",
        device_language_setting_code="en-us",
        country_code="us",
    )
    headers = {
        "Content-Type": "application/json",
        "X-GDFind-APIKey": "find_portfolio_rec",
    }
    try:
        cresponse = await aiohttp_post(
            cq,
            payload={"search_query": query},
            headers=headers,
        )
    except Exception as e:
        logging.error(f"Error in Conv call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Conv call: {str(e)}")

    doms = {}

    for c in cresponse["recommended_domains"]:
        if not recommendation_check(c["fqdn"], c["domain_source"]):
            continue
        dtype = c.get("inventory", "primary")
        if dtype not in ["premium", "auction", "registry_premium", "primary"]:
            dtype = "primary"

        if "price_info" in c and "salePrice" in c["price_info"]:
            doms[c['fqdn']] = c["price_info"]["salePrice"]
        else:
            if dtype == "primary":
                doms[c['fqdn']] = 11.99
            else:
                continue

    return doms


def compute_probabilities(A, target_avg, tol=1e-9, max_expand=100):
    A = np.asarray(A, float)
    min_val, max_val = A.min(), A.max()
    if not (min_val <= target_avg <= max_val):
        raise ValueError("target_avg must be in [min(A), max(A)]")

    def softmax(lam):
        z = lam * A
        z -= z.max()         # shift for numerical stability
        e = np.exp(z)
        return e / e.sum()

    def mean_diff(lam):
        return softmax(lam).dot(A) - target_avg

    # If uniform distribution already meets target_avg
    if abs(A.mean() - target_avg) < tol:
        return np.ones_like(A) / len(A)

    # Bracket λ based on whether we need to increase or decrease the mean
    if A.mean() < target_avg:
        lo, hi = 0.0, 1.0
        while mean_diff(hi) < 0 and max_expand:
            hi *= 2
            max_expand -= 1
    else:
        lo, hi = -1.0, 0.0
        while mean_diff(lo) > 0 and max_expand:
            lo *= 2
            max_expand -= 1

    sol = root_scalar(mean_diff, bracket=[lo, hi], method='brentq', xtol=tol)
    return softmax(sol.root)


def select_with_target_average(doms, target):
    prices = list(doms.values())
    if target > max(prices):
        target = max(prices)
    probs = compute_probabilities(prices, target)
    probs_cumsum = np.cumsum(probs)
    probs_cumsum[-1] = 1.0  # Ensure the last value is exactly 1
    selected_index = np.searchsorted(probs_cumsum, np.random.rand())
    selected_domain = list(doms.keys())[selected_index]
    return selected_domain

@app.get("/v1/mystery_box_rec")
async def mystery_box_rec(price: int, search_query: str = "", shopper_id: str = "", target_margin=0.2) -> dict:
    """
    Function to suggest a mystery box domain based on a search query or shopper ID.

    :param price: The price of the mystery box
    :param search_query: The search query for the mystery box. one of shopper_id or search_query must be provided
    :param shopper_id: The ID of the shopper. one of shopper_id or search_query must be provided
    :return: A dictionary containing the domain recommendation and its price
    """

    if not search_query and not shopper_id:
        raise ValueError("Either search_query or shopper_id must be provided.")

    if not search_query:
        domains_source = ["shopper_rec_find_conv", "shopper_rec_aftermarket", "pgen_s3"]
    else:
        domains_source = ["aftermarket", "pgen"]
        if len(search_query) > 30:
            domains_source.append("find_conv")
        else:
            domains_source.append("find")

    q_start_time = time.time()
    tasks = []
    for source in domains_source:
        logging.info(f"Gettting domains from: {source} for shopper: {shopper_id} OR query: {search_query}")
        if source == "shopper_rec_find_conv":
            tasks.append(run_shopper_rec(shopper_id, "find_conversational"))
        elif source == "shopper_rec_find_aftermarket":
            tasks.append(run_shopper_rec(shopper_id, "aftermarket"))
        elif source == "aftermarket":
            tasks.append(run_aftermarket_api(search_query, shopper_id))
        elif source == "find_conv":
            tasks.append(run_conversational_api(search_query, shopper_id))
        elif source == "pgen_s3":
            tasks.append(run_pgen(search_query, shopper_id, mode="s3"))
        elif source == "pgen":
            tasks.append(run_pgen(search_query, shopper_id))
        elif source == "find":
            tasks.append(run_find_api(search_query, shopper_id, limit=40))

    api_res = await asyncio.gather(*tasks, return_exceptions=True)
    # run_time["find_api_time"] = time.time() - q_start_time

    res = {}
    for r in api_res:
        if isinstance(r, dict):
            res.update(r)

    res = {k: v for k, v in res.items() if v>0}
    min_price = min(res.values())
    target_return_val = price * (1 - float(target_margin))
    if min_price > target_return_val:
        find_res = await run_find_api(search_query, shopper_id, max_price=target_return_val, limit=100)
        find_res = {k: v for k, v in find_res.items() if v > 0 and k not in res}
        if min(find_res.values()) > target_return_val:
            raise HTTPException(status_code=500, detail="No domains found within the target price range.")
        res.update(find_res)

    selected_domain = select_with_target_average(res, target_return_val)
    return {"domain": selected_domain, "price": res[selected_domain]}


if __name__ == "__main__":
    # import asyncio
    # result = asyncio.run(run_shopper_rec(shopper_id="131567403"))
    # print("shopper_rec: ", result)
    #
    # result1 = asyncio.run(run_aftermarket_api(query="test", shopper_id="131567403"))
    # print("aftermarket_api: ", result1)
    #
    # result2 = asyncio.run(run_conversational_api(query="test", shopper_id="131567403"))
    # print("conversational_api: ", result2)
    #
    # res = asyncio.run(mystery_box_rec(price=25, search_query="test"))
    #
    # print("mystery_box_rec for query test: ", res)
    #
    # res = asyncio.run(mystery_box_rec(price=25, shopper_id="11111510"))
    # print("mystery_box_rec for shopper_id 11111510: ", res)

    # result2 = asyncio.run(run_find_api(query="pizza", shopper_id="131567403"))
    # print("find_api: ", result2)
    #
    # result2 = asyncio.run(run_find_api(query="pizza", shopper_id="131567403", max_price=13))
    # print("find_api: ", result2)

    # result2 = asyncio.run(run_pgen(query="pizza", shopper_id="131567403"))
    # print("pgen: ", result2)
    #
    # result2 = asyncio.run(run_pgen(query="pizza", shopper_id="131567403", mode="s3"))
    # print("pgen s3: ", result2)

    import uvicorn

    uvicorn.run(
        "mystery_box_rec:app",
        host="0.0.0.0",
        port=8005,
        workers=1
    )