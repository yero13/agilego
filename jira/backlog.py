import json
from .request import Request, Field


class SprintBacklogRequest(Request):
    __CFG_SPRINT_BACKLOG_REQUEST = './cfg/sprint-backlog-request.json'
    __KEY_BACKLOG_ITEMS = 'issues'

    def __init__(self, login, pswd):
        with open(SprintBacklogRequest.__CFG_SPRINT_BACKLOG_REQUEST) as cfg_file:
            Request.__init__(self, json.load(cfg_file, strict=False), login, pswd, is_multipage=True)

    def _parse_response(self, response, out_data):
        backlog = {}
        self.__parse_field(response, self._response_cfg[SprintBacklogRequest.__KEY_BACKLOG_ITEMS], backlog)
        for issue in backlog[SprintBacklogRequest.__KEY_BACKLOG_ITEMS]:
            out_data.update({issue[Field.FIELD_KEY]:issue})
            self._logger.debug('issue: {}'.format(issue))
        return out_data

    def __parse_field(self, data, field_cfg, target, is_optional=False):
        field_type = field_cfg[Field.FIELD_TYPE]
        field_key = field_cfg[Field.FIELD_KEY] if Field.FIELD_KEY in field_cfg else None
        field_ext_id = field_cfg[Field.FIELD_EXT_ID] if Field.FIELD_EXT_ID in field_cfg else field_key
        #self._logger.debug('key: {} type: {}'.format(field_key, field_type))
        if field_type == Field.TYPE_ARRAY:
            target.update({field_ext_id: []})
            field_value = data[field_key]
            field_pattern = field_cfg[Field.FIELD_MATCH] if Field.FIELD_MATCH in field_cfg else None
            if Field.FIELD_SUBITEMS in field_cfg:
                subfield = next(iter(field_cfg[Field.FIELD_SUBITEMS].values()))  # only one field within array is allowed
                for item in field_value:
                    if Field.is_match(field_pattern, item):
                        self.__parse_field(item, subfield, target[field_ext_id])
            else:
                target[field_ext_id] = field_value
        elif field_type == Field.TYPE_OBJECT:
            is_explicit = field_cfg[Field.FIELD_EXPLICIT] if Field.FIELD_EXPLICIT in field_cfg else False
            is_optional = field_cfg[Field.FIELD_OPTIONAL] if Field.FIELD_OPTIONAL in field_cfg else False
            if field_key:
                try:
                    field_value = data[field_key]
                except KeyError:
                    if is_optional:
                        field_value = None
                    else:
                        raise
            else: # noname object
                field_value = data  # working with the same item
            if is_explicit:
                obj_exp = {}
                if isinstance(target, dict):  # add to object
                    target.update({field_ext_id: obj_exp})
                else:  # add to array
                    target.append(obj_exp)
            for subfield in field_cfg[Field.FIELD_SUBITEMS]:
                self.__parse_field(field_value, field_cfg[Field.FIELD_SUBITEMS][subfield],
                                   obj_exp if is_explicit else target, is_optional)
        else:  # other types
            try:
                field_value = data[field_key]
            except TypeError:
                if is_optional:
                    field_value = None
                else:
                    raise
            casted_value = Field.get_casted_value(field_type, field_value)
            #self._logger.debug('{}'.format(casted_value))
            if isinstance(target, dict):  # add to object
                target.update({field_ext_id: casted_value})
            else:  # add to array
                target.append(casted_value)
