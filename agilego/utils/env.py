import json
from db.accessor import DataAccessor

is_test = False

CFG_TEST_ENV_DB = 'jira-test-data'
CFG_TEST_ENV_PARAMS = 'env.params'
CFG_ENV = './cfg/env.json'


def get_env_params():
    if is_test:
        env_cfg = DataAccessor(CFG_TEST_ENV_DB).get({DataAccessor.CFG_KEY_COLLECTION: CFG_TEST_ENV_PARAMS,
                                                 DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE})
    else:
        with open(CFG_ENV) as env_cfg_file:
            env_cfg = json.load(env_cfg_file, strict=False)
    return env_cfg

