from copy import deepcopy
from na3x.db.data import Accessor, AccessParams
from na3x.utils.aggregator import Aggregator
from na3x.validation.validator import getter, comparator, Check
from logic.constants import DbConstants, ParamConstants


def get_linked_issues(key, link_type):
    filter = {'source': key, 'type': link_type}

    return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
        {AccessParams.KEY_MATCH_PARAMS: filter,
         AccessParams.KEY_COLLECTION: DbConstants.SCRUM_BACKLOG_LINKS,
         AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})


@getter
def get_linked_allocations(input, **params):
    LINK_TARGET = 'target'
    PARAM_FUNC = 'func'

    linked_issues = get_linked_issues(input[ParamConstants.PARAM_ITEM_KEY], params.get(ParamConstants.PARAM_TYPE))
    filter = []
    if len(linked_issues) > 0:
        for issue in linked_issues:
            filter.append({ParamConstants.PARAM_ITEM_KEY: issue[LINK_TARGET]})
        linked_allocations = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_MATCH_PARAMS: {AccessParams.OPERATOR_OR: filter},
            AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ALLOCATIONS,
            AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})
        agg_func = params.get(PARAM_FUNC)
        return Aggregator.agg_single_func(linked_allocations, ParamConstants.PARAM_DATE, agg_func, [ParamConstants.PARAM_ITEM_KEY])
    else:
        return None


@comparator
def schedule_conflict_too_late(to_validate, constraint, violation_cfg):
    res = []

    if constraint:
        for k, v in constraint.items():
            if v < to_validate:
                violation = deepcopy(violation_cfg)
                violation[Check.CFG_KEY_VIOLATION_MSG] = violation[Check.CFG_KEY_VIOLATION_MSG].format(k, v)
                res.append(violation)
    return None if len(res) == 0 else res



