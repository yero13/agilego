from string import Template


class CfgUtils:
    @staticmethod
    def substitute_params(cfg, params):
        str =  Template(cfg).safe_substitute(params)
        return str
