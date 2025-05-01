from fastapi import HTTPException
import async_lru
import aiohttp
import logging
import time
from aiohttp import ClientTimeout

config = {
  "find_host": "http://haproxy.uswest.prod.domain.gdg:8004",
  "find_aftermarket_host": "http://haproxy.uswest.prod.domain.gdg:8080",
  "shoper_rec_host": "http://haproxy.uswest.prod.domain.gdg:8910",
  "pgen_host": "http://haproxy.uswest.prod.domain.gdg:8094"
}


async def aiohttp_post(url, headers=None, payload=None, timeout=ClientTimeout(total=15)):
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