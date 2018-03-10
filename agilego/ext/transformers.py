import pandas as pd
from framework.transformation.transformer import transformer
from logic.constants import DbConstants, ParamConstants


@transformer
def dates2range(input, **params):
    PARAM_FIELD_STARTDATE = 'field.startDate'
    PARAM_FIELD_ENDDATE = 'field.endDate'
    PARAM_FIELD_RANGE = 'field.range'

    return {params.get(PARAM_FIELD_RANGE): pd.date_range(input[params.get(PARAM_FIELD_STARTDATE)],
                                                         input[params.get(PARAM_FIELD_ENDDATE)]).tolist()}


@transformer
def sec2hrs(input, **params):
    PARAM_FIELDS = 'fields'

    fields = params.get(PARAM_FIELDS)
    for field in fields:
        for row in input:
            row[field] = row[field]/3600 if row[field] else None
    return input


@transformer
def filter_assignments(input, **params):
    res = []
    for assignment in input[DbConstants.SCRUM_ASSIGNMENTS]:
        for item in input[DbConstants.SCRUM_SPRINT_BACKLOG]:
            if assignment[ParamConstants.PARAM_ITEM_KEY] == item[ParamConstants.PARAM_ITEM_KEY]:
                res.append(assignment)
    return res
