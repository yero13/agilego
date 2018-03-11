import pandas as pd
from framework.transformation.transformer import transformer
from logic.constants import DbConstants, ParamConstants
from copy import deepcopy


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
def filter_assignments_on_backlog(input, **params):
    res = []
    for assignment in input[DbConstants.SCRUM_ASSIGNMENTS]:
        for item in input[DbConstants.SCRUM_SPRINT_BACKLOG]:
            if assignment[ParamConstants.PARAM_ITEM_KEY] == item[ParamConstants.PARAM_ITEM_KEY]:
                res.append(assignment)
    return res


@transformer
def filter_assignments_on_employees(input, **params):
    res = []
    for assignment in input[DbConstants.SCRUM_ASSIGNMENTS]:
        for employee in input[DbConstants.PROJECT_EMPLOYEES]:
            if assignment[ParamConstants.PARAM_EMPLOYEE] == employee[ParamConstants.PARAM_EMPLOYEE_NAME]:
                res.append(assignment)
    return res


@transformer
def filter_team_on_employees(input, **params): # ToDo: fix capacity calculation
    EMPLOYEES = 'employees'

    res = []
    for group in input[DbConstants.PROJECT_TEAM]:
        n_group = deepcopy(group)
        for e_employee in n_group[EMPLOYEES]:
            employee_to_remove = True
            for n_employee in input[DbConstants.PROJECT_EMPLOYEES]:
                if n_employee[ParamConstants.PARAM_EMPLOYEE_NAME] == e_employee[ParamConstants.PARAM_EMPLOYEE_NAME]:
                    employee_to_remove = False
                    break
            if employee_to_remove:
                n_group[EMPLOYEES].remove(e_employee)
        res.append(n_group)
    return res
