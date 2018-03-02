import json
from flask import jsonify
from flask_restful import Resource, request
from framework.db.data import Accessor, AccessParams
from framework.utils.converter import Converter, Types
from framework.validation.validator import Validator
from logic.constants import DbConstants, ParamConstants, MatchConstants
from logic.gantt import BaselineGantt

CFG_ASSIGN_VALIDATION = './cfg/validation/assignment.json' # ToDo: load on start up


class Backlog(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI,
             AccessParams.KEY_MATCH_PARAMS: {
                 AccessParams.OPERATOR_OR: [{ParamConstants.PARAM_TYPE: MatchConstants.TYPE_STORY},
                                        {ParamConstants.PARAM_TYPE: MatchConstants.TYPE_BUG}]}}))


class Sprint(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE}))


class SprintTimeline(Resource):
    def get(self):
        found = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_TIMELINE,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE})
        return (
        [] if (not found or not ParamConstants.PARAM_TIMELINE in found) else jsonify(found[ParamConstants.PARAM_TIMELINE]))


class ComponentList(Resource):
    def get(self):
        found = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_COMPONENTS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE})
        return (
        [] if (not found or not ParamConstants.PARAM_COMPONENT in found) else found[ParamConstants.PARAM_COMPONENT])


class GroupList(Resource):
    def get(self):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_TEAM,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})


class EmployeeList(Resource):
    def get(self):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_EMPLOYEES,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})


class Group(Resource):
    def delete(self, group):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).delete(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_TEAM, AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {ParamConstants.PARAM_GROUP: group}}), 204

    def post(self):
        group = request.get_json()
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).upsert(
            {AccessParams.KEY_COLLECTION: DbConstants.PROJECT_TEAM,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_OBJECT: group,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_GROUP: group[ParamConstants.PARAM_GROUP]}}), 201


class AssignmentList(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI}))


class SubtaskList(Resource):
    def get(self, task_key):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_PARENT: task_key}}))


class TaskDetails(Resource):
    def get(self, task_key):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: task_key}}))


class SubtaskDetails(Resource):
    def get(self, subtask_key):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: subtask_key}}))


# ToDo: group/assignments services should be reviewed as they should trigger validations and KPIs (velocity, etc) review

class Assignment(Resource):
    def get(self, key, date, group, employee):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: key,
                 ParamConstants.PARAM_DATE: date,
                 ParamConstants.PARAM_GROUP: group,
                 ParamConstants.PARAM_EMPLOYEE: employee}}))

    def post(self):
        assignment_details = request.get_json()
        assignment_details[ParamConstants.PARAM_WHRS] = Converter.convert(assignment_details[ParamConstants.PARAM_WHRS],
                                                                          Types.TYPE_FLOAT)
        assignment_details[ParamConstants.PARAM_DATE] = Converter.convert(assignment_details[ParamConstants.PARAM_DATE],
                                                                          Types.TYPE_DATE)

        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).upsert(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_OBJECT: assignment_details,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: assignment_details[
                     ParamConstants.PARAM_ITEM_KEY],
                 ParamConstants.PARAM_DATE: assignment_details[
                     ParamConstants.PARAM_DATE],
                 ParamConstants.PARAM_GROUP: assignment_details[
                     ParamConstants.PARAM_GROUP],
                 ParamConstants.PARAM_EMPLOYEE: assignment_details[
                     ParamConstants.PARAM_EMPLOYEE]}}), 201

    def delete(self, key, date, group, employee):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).delete(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: key,
                 ParamConstants.PARAM_DATE: Converter.convert(date, Types.TYPE_DATE),
                 ParamConstants.PARAM_GROUP: group,
                 ParamConstants.PARAM_EMPLOYEE: employee}}), 204


class AssignmentValidation(Resource):
    def post(self):
        assignment_details = request.get_json()
        assignment_details[ParamConstants.PARAM_WHRS] = float(assignment_details[ParamConstants.PARAM_WHRS])  # ToDo: move typecast into configuration ?
        assignment_details[ParamConstants.PARAM_DATE] = Converter.convert(assignment_details[ParamConstants.PARAM_DATE],
                                                                          Types.TYPE_DATE)
        with open(CFG_ASSIGN_VALIDATION) as validation_cfg_file:
            res = Validator(json.load(validation_cfg_file, strict=False)).validate(assignment_details) # ToDo: load once on start-up api

        return res, 200 # ToDo: move cfg to constructor/cache


class GanttTasks(Resource):
    def get(self):
        return jsonify(BaselineGantt().tasks)


class GanttLinks(Resource):
    def get(self):
        return jsonify(BaselineGantt().links)
