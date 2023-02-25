import redis
from environs import Env

env = Env()
env.read_env()

username = env('REDIS_USERNAME')
password = env('REDIS_PASSWD')

redis = redis.Redis(
    host='redis-11457.c1.asia-northeast1-1.gce.cloud.redislabs.com',
    port=11457,
    username=username,
    password=password,
    decode_responses=True,
)
