from upstash_redis import Redis
from dotenv import load_dotenv
import os
load_dotenv()

redis_url = os.getenv("KV_REST_API_URL")
redis_token = os.getenv("KV_REST_API_TOKEN")

r = Redis(url=redis_url,token=redis_token)

async def add_list_to_cache(user_id: str, data_list: list,type):
    for data in data_list:
        await add_redis_cache(user_id, data,type)

async def add_redis_cache(user_id: str, data: str,type: str):
    key = f"{user_id}:{type}"
    existence = await r.exists(key)
    await r.rpush(key,data)
    if not existence:
        await r.expire(key,2)
    print(f"Cache updated for {user_id}: {key} -> {data}")

async def get_from_redis_cache(user_id: str, type: str):
    key = f"{user_id}:{type}"
    data = await r.lrange(key,0,-1)
    if data:
        print(f"Cache hit for {user_id}: {key} -> {data}")
        return data
    else:
        print(f"Cache miss for {user_id}: {key}")
        return []

if __name__ == "__main__":
    # Example usage
    user_id = "test_user"
    data1 = "test_data1"
    type = "image"
    data2 = "test_data2"
    add_redis_cache(user_id, data1,type)
    add_redis_cache(user_id, data2,type)
    get_from_redis_cache(user_id, type)
