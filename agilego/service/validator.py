from service.aggregator import Aggregator
from db.data import Accessor
from service.constants import DbConstants
import logging


class Validator:
    __CFG_KEY_CHECKS = 'checks'

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)

    def validate(self, obj_to_validate):
        return NotImplementedError

    def what_if(self, obj_to_validate):
        result = []
        for check in self.__cfg[Validator.__CFG_KEY_CHECKS]:
            self.__logger.info('Performing {} what-if validation against {}'.format(check, obj_to_validate))
            check_res = Validation(self.__cfg[Validator.__CFG_KEY_CHECKS][check]).what_if(obj_to_validate)
            if check_res:
                result.append(check_res)
        return None if len(result) == 0 else result


class Validation:
    CFG_KEY_VALIDATOR_TYPE = 'type'
    CFG_VALIDATOR_TYPE_LIMIT_EXCEED = 'limit.exceed'
    CFG_KEY_VIOLATION = 'violation'
    CFG_KEY_VIOLATION_SEVERITY = 'severity'
    CFG_KEY_VIOLATION_MSG = 'message'
    __CFG_KEY_VALIDATION_OBJ = 'obj_to_validate'
    __CFG_KEY_VALIDATION_FIELD = 'field_to_validate'
    __CFG_KEY_TARGET = 'target'
    __CFG_KEY_CONSTRAINT = 'constraint'
    __CFG_KEY_VALUE_TYPE = 'type'
    __CFG_VALUE_TYPE_AGG = 'aggregate'
    __CFG_VALUE_TYPE_CONSTANT = 'constant'
    __CFG_KEY_VALUE_CALC_CFG = 'cfg'
    __CFG_KEY_CALC_AGG_FUNC = 'agg.func'
    __CFG_KEY_CALC_AGG_FIELD = 'agg.field'
    __CFG_KEY_CALC_AGG_COLLECTION = 'agg.collection'
    __CFG_KEY_CALC_AGG_GROUP = 'agg.group'
    __CFG_KEY_CONSTANT_VALUE = 'value'

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)

    def validate(self, obj_to_validate):
        self.__logger.debug('Validate {}'.format(obj_to_validate))
#        target = self.__get_value(self.__cfg[ValidationCheck.__CFG_KEY_TARGET], obj_to_validate)
#        constraint = self.__get_value(self.__cfg[ValidationCheck.__CFG_KEY_CONSTRAINT], obj_to_validate)

    def what_if(self, obj_to_validate):
        err_cfg = self.__cfg[Validation.CFG_KEY_VIOLATION]
        self.__logger.debug('what if {}'.format(obj_to_validate))
        value_to_validate = obj_to_validate[self.__cfg[Validation.__CFG_KEY_VALIDATION_OBJ][Validation.__CFG_KEY_VALIDATION_FIELD]]
        constraint_value = self.__get_calc_value(self.__cfg[Validation.__CFG_KEY_CONSTRAINT], obj_to_validate)
        self.__logger.debug('constraint: {}'.format(constraint_value))
        target_value = self.__get_calc_value(self.__cfg[Validation.__CFG_KEY_TARGET], obj_to_validate)
        self.__logger.debug('target: {}'.format(target_value))
        current_value = self.__get_current_value(self.__cfg[Validation.__CFG_KEY_VALIDATION_OBJ], obj_to_validate)
        if self.__cfg[Validation.CFG_KEY_VALIDATOR_TYPE] == Validation.CFG_VALIDATOR_TYPE_LIMIT_EXCEED:
            current_value = 0 if not current_value else current_value
            self.__logger.debug('current value: {}'.format(current_value))
            target_value = 0 if not target_value else target_value
            if (target_value + value_to_validate - current_value) > constraint_value:
                return {Validation.CFG_KEY_VIOLATION_SEVERITY: err_cfg[Validation.CFG_KEY_VIOLATION_SEVERITY],
                        Validation.CFG_KEY_VIOLATION_MSG: err_cfg[Validation.CFG_KEY_VIOLATION_MSG]}

    def __get_calc_value(self, cfg, obj_to_validate):
        if cfg[Validation.__CFG_KEY_VALUE_TYPE] == Validation.__CFG_VALUE_TYPE_CONSTANT:
            return cfg[Validation.__CFG_KEY_CONSTANT_VALUE]
        elif cfg[Validation.__CFG_KEY_VALUE_TYPE] == Validation.__CFG_VALUE_TYPE_AGG:
            calc_cfg = cfg[Validation.__CFG_KEY_VALUE_CALC_CFG]
            return self.__get_aggregated_value(calc_cfg, obj_to_validate)

    def __get_aggregated_value(self, cfg, group_param_values):
        filter = {}
        group_params = cfg[Validation.__CFG_KEY_CALC_AGG_GROUP]
        for param in group_params:
            filter[param] = group_param_values[param]
        agg_collection = cfg[Validation.__CFG_KEY_CALC_AGG_COLLECTION]
        agg_func = cfg[Validation.__CFG_KEY_CALC_AGG_FUNC]
        agg_field = cfg[Validation.__CFG_KEY_CALC_AGG_FIELD]
        dataset = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_MATCH_PARAMS: filter,
             Accessor.PARAM_KEY_COLLECTION: agg_collection,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_MULTI})
        return Aggregator.aggregate(dataset, agg_field, agg_func)

    def __get_current_value(self, cfg, match_param_values):
        id = {}
        match_params = cfg[Accessor.PARAM_KEY_MATCH_PARAMS]
        for param in match_params:
            id[param] = match_param_values[param]
        res = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_MATCH_PARAMS: id,
             Accessor.PARAM_KEY_COLLECTION: cfg[Accessor.PARAM_KEY_COLLECTION],
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE})
        return None if not res else res[cfg[Validation.__CFG_KEY_VALIDATION_FIELD]]
