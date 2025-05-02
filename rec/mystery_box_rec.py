import subprocess

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Query
import asyncio
import logging
import numpy as np
from scipy.optimize import root_scalar
import time
import random
import uuid

from contextlib import asynccontextmanager

from mystery_api import run_shopper_rec, run_aftermarket_api, run_conversational_api, run_find_api, run_pgen
from mystery_llm import llm_call_domain_info


scheduler = AsyncIOScheduler()

session_ids = {}  # contains session_id: pool, results, remaining_rolls, total_rolls, price, margin

async def run_bash_commands_and_reload_env():
    bash_commands = """
    source ~/.zshrc
    adev
    env | grep AWS > .env
    python3 mystery_get_token.py
    """
    subprocess.run(["bash", "-c", bash_commands], check=True)
    # load_dotenv(dotenv_path=".env", override=True)
    # print("AWS_ACCESS_KEY_ID:", os.getenv("AWS_ACCESS_KEY_ID"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_bash_commands_and_reload_env()
    scheduler.add_job(run_bash_commands_and_reload_env, "interval", minutes=10)
    scheduler.start()
    print("Scheduler started.")

    yield

    # Shutdown actions
    scheduler.shutdown()
    print("Scheduler shut down.")


app = FastAPI(title="MysteryBox rec api", version="0.2", lifespan=lifespan)


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

def roll(doms, price, margin):
    # todo: solve edge cases of rolling causing all domain pricing > target or all < target depleted (by pulling more from apis)
    target_return_val = price * (1 - float(margin))
    selected_domain = select_with_target_average(doms, target_return_val)
    selected_domain_price = doms[selected_domain]
    trial_products = [
        "website_builder",
        "online_store_builder",
        "digital_marketing_tools",
        "godaddy_pro",
        ""
    ]
    trial_product = random.choice(trial_products)
    pool = {k: v for k, v in doms.items() if k != selected_domain}
    return pool, selected_domain, selected_domain_price, trial_product

@app.get("/v1/mystery_box_rec")
async def mystery_box_rec(session_id: str=Query(
                                default="",
                                title="Session_id of a box",
                                description="The session ID. For a re-roll, the session ID must be provided, other params can be empty",
                            ),
                          price: int=Query(
                                default=25,
                                title="Price of the mystery box",
                                description="The price of the mystery box"
                            ),
                          search_query: str = Query(
                                default="",
                                title="Search query for the mystery box",
                                description="The search query for the mystery box. one of shopper_id or search_query must be provided"
                            ),
                          shopper_id: str = Query(
                                default="",
                                title="Shopper ID",
                                description="The ID of the shopper. one of shopper_id or search_query must be provided"
                            ),
                          target_margin: float=Query(
                                default=0.1,
                                title="Target margin",
                                description="The target margin for the mystery box"
                            ),

    ) -> dict:
    """
    Function to suggest a mystery box domain based on a search query or shopper ID.
    """

    """
    :param session_id: The session ID. For a re-roll, the session ID must be provided, other params can be empty
    :param price: The price of the mystery box
    :param search_query: The search query for the mystery box. one of shopper_id or search_query must be provided
    :param shopper_id: The ID of the shopper. one of shopper_id or search_query must be provided
    :return: A dictionary containing the domain recommendation and its price
    """

    global session_ids
    if session_id != "" and session_id in session_ids:  # re-roll
        session_data = session_ids[session_id]
        remaining_rolls = session_data.get("remaining_rolls", 0)
        if remaining_rolls > 0:
            pool, domain, domain_price, trial_product = roll(session_data["pool"], session_data["price"], session_data["margin"])
            session_ids[session_id]['pool'] = pool
            session_ids[session_id]['remaining_rolls'] = remaining_rolls - 1
            res = {"domain": domain, "price": domain_price, "trial_product": trial_product,
                     "session_id": session_id, "remaining_rolls": remaining_rolls - 1}
            session_ids[session_id]['results'].append(res)
            return res
        else:
            return session_data['results'][-1]

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

    pool, selected_domain, selected_domain_price, trial_product = roll(res, price, target_margin)
    if session_id == "":
        session_id = str(uuid.uuid4())

    if int(price) <= 15:
        remaining_rolls = 0
    elif int(price) <= 25:
        remaining_rolls = 2
    else:
        remaining_rolls = 4

    res = {"domain": selected_domain, "price": selected_domain_price, "trial_product": trial_product,
           "session_id": session_id, "remaining_rolls": remaining_rolls}
    session_ids[session_id] = {"pool": pool,
                               "results": [res],
                               "remaining_rolls": remaining_rolls,
                               "total_rolls": remaining_rolls,
                               "price": price,
                               "margin": target_margin}

    return res

@app.get("/v1/llm_domain_info")
async def llm_domain_info(domain: str):
    """
    Function to get domain info using LLM.

    :param domain: The domain name
    :return: A dictionary containing the domain info
    """
    if not domain:
        raise ValueError("Domain name must be provided.")

    res = await llm_call_domain_info(domain)
    return {"domain": domain, "info": res}


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