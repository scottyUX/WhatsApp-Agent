from upstash_redis import Redis
from dotenv import load_dotenv
import os
load_dotenv()

redis_url = os.getenv("KV_REST_API_URL")
redis_token = os.getenv("KV_REST_API_TOKEN")

r = Redis(url=redis_url,token=redis_token)

def add_list_to_cache(user_id: str, data_list: list,type: str):
    for data in data_list:
        add_redis_cache_media(user_id, data,type)

def add_redis_cache_media(user_id: str, data: str,type: str):
    key = f"{user_id}:{type}"
    existence = r.exists(key)
    r.rpush(key,data)
    if not existence:
        r.expire(key,2)
    add_redis_media_counter(user_id)
    print(f"Cache updated for {user_id}: {key} -> {data}")
    
def add_redis_media_counter(user_id: str):
    key = f"{user_id}:media_counter"
    r.incr(key)
    
def get_redis_media_counter(user_id: str):
    key = f"{user_id}:media_counter"
    counter = r.get(key)
    if counter:
        print(f"Media counter for {user_id}: {counter}")
        return int(counter)
    else:
        print(f"No media counter found for {user_id}")
        return 0
    
def delete_redis_media_counter(user_id: str):
    key = f"{user_id}:media_counter"
    r.delete(key)
    print(f"Media counter cleared for {user_id}: {key}")

def get_from_redis_cache(user_id: str, type: str):
    key = f"{user_id}:{type}"
    data = r.lrange(key,0,-1)
    delete_redis_media_counter(user_id)
    clear_redis_cache(user_id, type)
    if data:
        print(f"Cache hit for {user_id}: {key} -> {data}")
        return data
    else:
        print(f"Cache miss for {user_id}: {key}")
        return []

def clear_redis_cache(user_id: str, type: str):
    key = f"{user_id}:{type}"
    r.delete(key)
    print(f"Cache cleared for {user_id}: {key}")

if __name__ == "__main__":
    # Example usage
    user_id = "test_user"
    data1 = "test_data1"
    type = "image"
    data2 = "test_data2"
    add_redis_cache_media(user_id, data1,type)
    add_redis_cache_media(user_id, data2,type)
    get_from_redis_cache(user_id, type)
