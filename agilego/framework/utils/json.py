from datetime import date
from flask.json import JSONEncoder
from jsondiff import diff
from framework.utils.converter import Converter


class ExtJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return Converter.datetime2str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


class JSONUtils():
    DIFF_DELETE = '$delete'
    # ToDo: implement support of other operations

    def diff(a, b):
        delta = diff(a, b)
        if not a:
            return delta
        for item in delta:
            if isinstance(a[item], list):
                if delta[item] == []:
                    delta[item] = {JSONUtils.DIFF_DELETE : a[item]}
                elif isinstance(delta[item], dict):
                    for key in delta[item].keys():
                        if str(key) == JSONUtils.DIFF_DELETE:
                            delta_upd = {JSONUtils.DIFF_DELETE : []}
                            for i in delta[item][key]:
                                delta_upd[JSONUtils.DIFF_DELETE].append(a[item][i])
                                delta[item] = delta_upd
        return delta
