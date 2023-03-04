import redis
from environs import Env

env = Env()
env.read_env()

host = env('HOST')
port = env('PORT')
username = env('REDIS_USERNAME')
password = env('REDIS_PASSWD')

redis = redis.Redis(
    host=host,
    port=port,
    username=username,
    password=password,
    decode_responses=True,
)
