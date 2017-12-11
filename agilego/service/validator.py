from service.aggregator import Aggregator
from db.data import Accessor
from service.constants import DbConstants, ParamConstants
import logging
import abc
from utils.converter import Converter


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
            check_res = Validation.factory(self.__cfg[Validator.__CFG_KEY_CHECKS][check]).what_if(obj_to_validate)
            if check_res:
                if type(check_res) == dict:
                    result.append(check_res)
                else:
                    result.extend(check_res)
        return None if len(result) == 0 else result


class Validation:
    __CFG_KEY_VALIDATOR_TYPE = 'type'
    __CFG_VALIDATOR_TYPE_LIMIT_EXCEED = 'limit.exceed'
    __CFG_VALIDATOR_TYPE_DATE_OVERDUE = 'date.overdue'
    __CFG_VALIDATOR_TYPE_SCHEDULE_INTEGRITY = 'schedule.integrity'
    __CFG_VALIDATOR_TYPE_SETS_INTERSECTION = 'sets.intersection'
    _CFG_KEY_VIOLATION = 'violation'
    _CFG_KEY_VIOLATION_SEVERITY = 'severity'
    _CFG_KEY_VIOLATION_MSG = 'message'
    _CFG_KEY_INPUT = 'input'
    _CFG_KEY_TARGET = 'target'
    _CFG_KEY_CONSTRAINT = 'constraint'
    _CFG_KEY_EXTRACT = 'extract'
    __CFG_KEY_OBJECT = 'object'
    __CFG_KEY_EXTRACT_FIELD = 'extract.field'
    __CFG_KEY_FIELD_TYPE = 'field.type'
    __CFG_KEY_DEFAULT = 'default'
    __CFG_KEY_CONSTANT = 'constant'
    __CFG_KEY_CONSTANT_VALUE = 'value'
    __CFG_KEY_CALC = 'calculate'
    __CFG_KEY_CALC_FUNC = 'calc.func'
    __CFG_CALC_AGG_SUM = 'agg.sum'
    __CFG_KEY_CALC_AGG_FIELD = 'agg.field'
    __CFG_KEY_CALC_AGG_COLLECTION = 'agg.collection'
    __CFG_KEY_CALC_AGG_GROUP = 'agg.group'

    @staticmethod
    def factory(cfg):
        type = cfg[Validation.__CFG_KEY_VALIDATOR_TYPE]
        if type == Validation.__CFG_VALIDATOR_TYPE_LIMIT_EXCEED:
            return LimitExceedValidation(cfg)
        elif type == Validation.__CFG_VALIDATOR_TYPE_DATE_OVERDUE:
            return DateOverdueValidation(cfg)
        elif type == Validation.__CFG_VALIDATOR_TYPE_SCHEDULE_INTEGRITY:
            return ScheduleIntegrityValidation(cfg)
        elif type == Validation.__CFG_VALIDATOR_TYPE_SETS_INTERSECTION:
            return SetsIntersectionValidation(cfg)
        else:
            raise NotImplementedError('Not supported request type - {}'.format(type))

    def __init__(self, cfg):
        self._cfg = cfg
        self._logger = logging.getLogger(__class__.__name__)
        self._err_cfg = self._cfg[Validation._CFG_KEY_VIOLATION]

    @abc.abstractmethod
    def validate(self, obj_to_validate):
        return NotImplemented

    @abc.abstractmethod
    def what_if(self, obj_to_validate):
        return NotImplemented

    @staticmethod
    def __get_default_value(cfg):
        res = cfg[Validation.__CFG_KEY_DEFAULT] if Validation.__CFG_KEY_DEFAULT in cfg else None
        if res and (Validation.__CFG_KEY_FIELD_TYPE in cfg):
            res = Converter.convert(res, cfg[Validation.__CFG_KEY_FIELD_TYPE])
        return res

    @staticmethod
    def __get_casted_value(input, cfg):
        return Converter.convert(input, cfg[Validation.__CFG_KEY_FIELD_TYPE]) if Validation.__CFG_KEY_FIELD_TYPE in cfg else input

    @staticmethod
    def __calc(cfg, group_param_values):
        filter = {}
        group_params = cfg[Validation.__CFG_KEY_CALC_AGG_GROUP]
        for param in group_params:
            filter[param] = group_param_values[param]
        agg_collection = cfg[Validation.__CFG_KEY_CALC_AGG_COLLECTION]
        agg_func = cfg[Validation.__CFG_KEY_CALC_FUNC]
        agg_field = cfg[Validation.__CFG_KEY_CALC_AGG_FIELD]
        agg_field_type = cfg[Validation.__CFG_KEY_FIELD_TYPE]
        dataset = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_MATCH_PARAMS: filter,
             Accessor.PARAM_KEY_COLLECTION: agg_collection,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_MULTI})
        res = Aggregator.aggregate(dataset, agg_field, agg_field_type, agg_func)
        return res if res else Validation.__get_default_value(cfg)

    @staticmethod
    def __extract(cfg, match_param_values):
        id = {}
        match_params = cfg[Accessor.PARAM_KEY_MATCH_PARAMS]
        for param in match_params:
            id[param] = match_param_values[param]
        res = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_MATCH_PARAMS: id,
             Accessor.PARAM_KEY_COLLECTION: cfg[Accessor.PARAM_KEY_COLLECTION],
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE})
        if not res:
            return Validation.__get_default_value(cfg)
        elif res[cfg[Validation.__CFG_KEY_EXTRACT_FIELD]] is None:
            return Validation.__get_default_value(cfg)
        else:
            return Validation.__get_casted_value(res[cfg[Validation.__CFG_KEY_EXTRACT_FIELD]], cfg)

    @staticmethod
    def _get(cfg, obj_to_validate):
        if Validation.__CFG_KEY_OBJECT in cfg:
            return Validation.__get_casted_value(
                obj_to_validate[cfg[Validation.__CFG_KEY_OBJECT][Validation.__CFG_KEY_EXTRACT_FIELD]], cfg[Validation.__CFG_KEY_OBJECT])
        if Validation.__CFG_KEY_CONSTANT in cfg:
            return cfg[Validation.__CFG_KEY_CONSTANT][Validation.__CFG_KEY_CONSTANT_VALUE]
        if Validation._CFG_KEY_EXTRACT in cfg:
            return Validation.__extract(cfg[Validation._CFG_KEY_EXTRACT], obj_to_validate)
        if Validation.__CFG_KEY_CALC in cfg:
            return Validation.__calc(cfg[Validation.__CFG_KEY_CALC], obj_to_validate)


class DependentValidation(Validation):
    _CFG_KEY_DEPENDENT = 'dependent'


class LimitExceedValidation(DependentValidation):
    def validate(self, obj_to_validate):
        return NotImplemented

    def what_if(self, obj_to_validate):
        constraint_value = self._get(self._cfg[Validation._CFG_KEY_CONSTRAINT], obj_to_validate)
        current_value = self._get(self._cfg[Validation._CFG_KEY_TARGET], obj_to_validate)
        input_value = self._get(self._cfg[Validation._CFG_KEY_INPUT], obj_to_validate)
        dependent_value = self._get(self._cfg[DependentValidation._CFG_KEY_DEPENDENT], obj_to_validate)
        if (dependent_value + input_value - current_value) > constraint_value:
            return {Validation._CFG_KEY_VIOLATION_SEVERITY: self._err_cfg[Validation._CFG_KEY_VIOLATION_SEVERITY],
                    Validation._CFG_KEY_VIOLATION_MSG: self._err_cfg[Validation._CFG_KEY_VIOLATION_MSG].format(constraint_value)}


class DateOverdueValidation(Validation):
    def validate(self, obj_to_validate):
        return NotImplemented

    def what_if(self, obj_to_validate):
        constraint_value = self._get(self._cfg[Validation._CFG_KEY_CONSTRAINT], obj_to_validate)
        input_value = self._get(self._cfg[Validation._CFG_KEY_INPUT], obj_to_validate)
        if input_value > constraint_value:
            return {Validation._CFG_KEY_VIOLATION_SEVERITY: self._err_cfg[Validation._CFG_KEY_VIOLATION_SEVERITY],
                    Validation._CFG_KEY_VIOLATION_MSG: self._err_cfg[Validation._CFG_KEY_VIOLATION_MSG].format(constraint_value)}


class ScheduleIntegrityValidation(DependentValidation):
    def validate(self, obj_to_validate):
        return NotImplemented

    def what_if(self, obj_to_validate):
        res = []
        input_value = self._get(self._cfg[Validation._CFG_KEY_INPUT], obj_to_validate)
        dependencies = self._get(self._cfg[DependentValidation._CFG_KEY_DEPENDENT], obj_to_validate)
        for dependency in dependencies:
            constraint_value = self._get(self._cfg[Validation._CFG_KEY_CONSTRAINT], {ParamConstants.PARAM_ITEM_KEY: dependency})
            if constraint_value < input_value:
                res.append(
                    {Validation._CFG_KEY_VIOLATION_SEVERITY: self._err_cfg[Validation._CFG_KEY_VIOLATION_SEVERITY],
                     Validation._CFG_KEY_VIOLATION_MSG: self._err_cfg[Validation._CFG_KEY_VIOLATION_MSG].format(
                         dependency, constraint_value)})
        return res if len(res) > 0 else None


class SetsIntersectionValidation(DependentValidation):
    def validate(self, obj_to_validate):
        return NotImplemented

    def what_if(self, obj_to_validate):
        constraint_set = self._get(self._cfg[Validation._CFG_KEY_CONSTRAINT], obj_to_validate)
        dependent_set = self._get(self._cfg[DependentValidation._CFG_KEY_DEPENDENT], obj_to_validate)
        return None if len(dependent_set) == 0 or len(set(constraint_set).intersection(dependent_set)) > 0 else {
            Validation._CFG_KEY_VIOLATION_SEVERITY: self._err_cfg[Validation._CFG_KEY_VIOLATION_SEVERITY],
            Validation._CFG_KEY_VIOLATION_MSG: self._err_cfg[Validation._CFG_KEY_VIOLATION_MSG].format(dependent_set)}
