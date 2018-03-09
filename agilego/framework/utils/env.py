import json

is_test = False

CFG_ENV = './cfg/env.json' # ToDo: move out framework
CFG_ENV_TEST = 'test'
CFG_ENV_PROD = 'prod'


def get_env_params():
    with open(CFG_ENV) as env_cfg_file:
        env_cfg = json.load(env_cfg_file, strict=False)
    return env_cfg[CFG_ENV_TEST if is_test else CFG_ENV_PROD]
