import asyncio
import time

cache = {}
cache_lock = asyncio.Lock()

async def add_to_cache(user_id,data,type):
    timestamp = time.time()
    async with cache_lock:
        if user_id not in cache:
            cache[user_id] = {}
        if type not in cache[user_id]:
            cache[user_id][type] = []
        cache[user_id][type].append((timestamp,data))
        print(f"Cache updated for {user_id}: {cache[user_id]}")

async def get_from_cache(user_id,type):
    async with cache_lock:
        if user_id in cache and type in cache[user_id]:
            return cache[user_id][type]
        else:
            return None

def clear_cache(user_id):
    current_time = time.time()
    if user_id in cache:
        for type in list(cache[user_id].keys()):
            cache[user_id][type] = [
                (timestamp, data) for timestamp, data in cache[user_id][type]
                if current_time - timestamp <= 1
            ]
            if not cache[user_id][type]:
                del cache[user_id][type]
        if not cache[user_id]:
            del cache[user_id]