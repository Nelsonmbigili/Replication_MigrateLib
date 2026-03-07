from starlette.config import Config
from environs import Env

env = Env()
env.read_env()  # This loads the environment variables from the .env file

REDIS_HOST = env('REDIS_HOST', str='0.0.0.0')
REDIS_PORT = env('REDIS_PORT', int=6379)
REDIS_DB = env('REDIS_DB', int=0)
REDIS_KEY_PREFIX = env('REDIS_KEY_PREFIX', str='fastapi_pydiator:')

DISTRIBUTED_CACHE_IS_ENABLED = env("DISTRIBUTED_CACHE_IS_ENABLED", bool=True)
CACHE_PIPELINE_IS_ENABLED = env("CACHE_PIPELINE_IS_ENABLED", bool=False)
LOG_PIPELINE_IS_ENABLED = env("LOG_PIPELINE_IS_ENABLED", bool=True)
