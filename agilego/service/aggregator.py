import pandas as pd
from utils.converter import Types


class Aggregator:
    @staticmethod
    def aggregate(values, agg_field, field_type, agg_func):
        if len(values) == 0:
            return None
        else:
            df = pd.DataFrame(values)
            if field_type in [Types.TYPE_INT, Types.TYPE_FLOAT]:
                df[agg_field] = df[agg_field].apply(pd.to_numeric)
            elif field_type == Types.TYPE_DATE:
                df[agg_field] = df[agg_field].apply(pd.to_datetime)
            return df.agg({agg_field: [agg_func]})[agg_field][agg_func]

