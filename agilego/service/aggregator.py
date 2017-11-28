from pandas import DataFrame


class Aggregator:
    FUNC_SUM = 'sum'

    @staticmethod
    def aggregate(values, agg_field, agg_func):
        if len(values) == 0:
            return None
        else:
            return DataFrame(values).agg({agg_field: [agg_func]})[agg_field][agg_func]

