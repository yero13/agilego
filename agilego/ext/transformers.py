import pandas as pd
import networkx as nx
from na3x.transformation.transformer import transformer
from na3x.utils.converter import Converter
from logic.constants import DbConstants, ParamConstants
from copy import deepcopy
from logic.gantt import Task, Link


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


@transformer
def gantt_links(input, **params):
    graph = nx.DiGraph()
    for link in input:
        link_type = link[Link.LINK_TYPE]
        link_source = link[Link.LINK_SOURCE]
        link_target = link[Link.LINK_TARGET]
        if link_type == Link.LINK_BLOCKS:
            graph.add_edge(link_source, link_target)
        elif link_type == Link.LINK_BLOCKED and (link_target, link_source) not in graph.edges:
            graph.add_edge(link_target, link_source)

    res = []
    for edge in graph.edges:
        link = {Link.LINK_ID: '{}->{}'.format(edge[0], edge[1]),
                Link.LINK_SOURCE: edge[0], Link.LINK_TARGET: edge[1], Link.LINK_TYPE: 2}
        res.append(link)
    return res


@transformer
def gantt_tasks(input, **params):
    graph = nx.DiGraph()
    for link in input[DbConstants.GANTT_LINKS]:
        graph.add_edge(link[Link.LINK_SOURCE], link[Link.LINK_TARGET])
    ext = []
    for node in graph.nodes:
        is_ext = True
        for item in input[DbConstants.SCRUM_SPRINT_BACKLOG]:
            if node == item[ParamConstants.PARAM_ITEM_KEY]:
                is_ext = False
                break
        if is_ext:
            ext.append(node)
    res = []
    for item in input[DbConstants.SCRUM_SPRINT_BACKLOG]:
        res.append(Task.create_task(item[ParamConstants.PARAM_ITEM_KEY]))
    if len(ext) > 0:
        res.append(Task.create_fake_task(Task.TASK_EXT, 'External dependencies'))
        for task in ext:
            res.append(Task.create_fake_task(task, task, Task.TASK_EXT))
    return res


@transformer
def merge_plan_vs_actual(input, **params):
    INPUT_PLAN = 'plan.issues'
    INPUT_ACTUAL = 'actual.issues.status'

    plan_df = pd.DataFrame.from_records(input[INPUT_PLAN])
    actual_df = pd.DataFrame.from_records(input[INPUT_ACTUAL])
    res = Converter.df2list(
        plan_df.merge(actual_df, right_on=ParamConstants.PARAM_ITEM_KEY, left_on=ParamConstants.PARAM_ITEM_KEY,
                      suffixes=('_plan', '_actual'), indicator=True, how='outer'))
    return res
