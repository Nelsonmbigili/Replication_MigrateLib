from environs import Env

env = Env()
env.read_env()  # Automatically loads environment variables from a .env file if it exists

REDIS_HOST = env.str('REDIS_HOST', '0.0.0.0')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_DB = env.int('REDIS_DB', 0)
REDIS_KEY_PREFIX = env.str('REDIS_KEY_PREFIX', 'fastapi_pydiator:')

DISTRIBUTED_CACHE_IS_ENABLED = env.bool("DISTRIBUTED_CACHE_IS_ENABLED", True)
CACHE_PIPELINE_IS_ENABLED = env.bool("CACHE_PIPELINE_IS_ENABLED", False)
LOG_PIPELINE_IS_ENABLED = env.bool("LOG_PIPELINE_IS_ENABLED", True)
