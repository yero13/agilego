import pandas as pd


class Aggregator:
    @staticmethod
    def aggregate(values, agg_field, agg_func, group_by=None):
        if len(values) == 0:
            return None
        else:
            if group_by:
                group_aggs = pd.DataFrame(values).groupby(group_by).agg({agg_field: [agg_func]})
                res = []
                for row in group_aggs.itertuples():
                    res.append({row[0]: row[1]})
                return res
            return pd.DataFrame(values).agg({agg_field: [agg_func]})[agg_field][agg_func]
