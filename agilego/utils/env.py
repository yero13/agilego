import json
#from db.data import Accessor

is_test = False  # ToDo: replace by 'pydevd' in sys.modules

CFG_TEST_ENV_DB = 'jira-test-data'
CFG_TEST_ENV_PARAMS = 'env.params'
CFG_ENV = './cfg/env.json'


def get_env_params():
    # ToDo: move test env to file
 #   if is_test:
 #       env_cfg = Accessor(CFG_TEST_ENV_DB).get({Accessor.PARAM_KEY_COLLECTION: CFG_TEST_ENV_PARAMS,
 #                                                Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE})
 #   else:
    with open(CFG_ENV) as env_cfg_file:
        env_cfg = json.load(env_cfg_file, strict=False)
    return env_cfg

