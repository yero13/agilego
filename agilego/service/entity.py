from flask_restful import Resource, request
from flask import jsonify
from service.constants import DbConstants, ParamConstants, MatchConstants
from bson.objectid import ObjectId
from service.validator import Validator
from db.data import Accessor
from utils.converter import Converter, Types
import json

CFG_ASSIGN_VALIDATION = './cfg/validation/assignment.json'


class Backlog(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_MULTI,
             Accessor.PARAM_KEY_MATCH_PARAMS: {
                 Accessor.OPERATOR_OR: [{ParamConstants.PARAM_TYPE: MatchConstants.TYPE_STORY},
                                        {ParamConstants.PARAM_TYPE: MatchConstants.TYPE_BUG}]}}))


class Sprint(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_SPRINT,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE}))


class SprintTimeline(Resource):
    def get(self):
        found = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_SPRINT_TIMELINE,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE})
        return (
        [] if (not found or not ParamConstants.PARAM_TIMELINE in found) else jsonify(found[ParamConstants.PARAM_TIMELINE]))


class ComponentList(Resource):
    def get(self):
        found = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.PROJECT_COMPONENTS,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE})
        return (
        [] if (not found or not ParamConstants.PARAM_COMPONENT in found) else found[ParamConstants.PARAM_COMPONENT])


class GroupList(Resource):
    def get(self):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.PROJECT_TEAM,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_MULTI})


class EmployeeList(Resource):
    def get(self):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.PROJECT_EMPLOYEES,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_MULTI})


class Group(Resource):
    def delete(self, group):
        # ToDo: move dependencies cleanup to separated class
        accessor = Accessor.factory(DbConstants.CFG_DB_SCRUM_API)
        accessor.delete({Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
                         Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_MULTI,
                         Accessor.PARAM_KEY_MATCH_PARAMS: {
                             ParamConstants.PARAM_GROUP: group}})
        return accessor.delete({Accessor.PARAM_KEY_COLLECTION: DbConstants.PROJECT_TEAM,
                                Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE,
                                Accessor.PARAM_KEY_MATCH_PARAMS: {
                                    ParamConstants.PARAM_GROUP: group}}), 204

    # ToDo: implement diff -u group_to_update vs existing group and trigger corresponding changes
    # ToDo: remove assignments if delete employee
    def post(self):
        group = request.get_json()
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).upsert(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.PROJECT_TEAM,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE,
             Accessor.PARAM_KEY_OBJECT: group,
             Accessor.PARAM_KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_GROUP: group[ParamConstants.PARAM_GROUP]}}), 201


class AssignmentList(Resource):
    def get(self):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_MULTI}))


class SubtaskList(Resource):
    def get(self, task_key):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_MULTI,
             Accessor.PARAM_KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_PARENT: task_key}}))


class TaskDetails(Resource):
    def get(self, task_key):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE,
             Accessor.PARAM_KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: task_key}}))


class SubtaskDetails(Resource):
    def get(self, subtask_key):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE,
             Accessor.PARAM_KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: subtask_key}}))


# ToDo: group/assignments services should be reviewed as they should trigger validations and KPIs (velocity, etc) review

class Assignment(Resource):
    def get(self, key, date, group, employee):
        return jsonify(Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE,
             Accessor.PARAM_KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: key,
                 ParamConstants.PARAM_DATE: date,
                 ParamConstants.PARAM_GROUP: group,
                 ParamConstants.PARAM_EMPLOYEE: employee}}))

    def post(self):
        assignment_details = request.get_json()
        assignment_details[ParamConstants.PARAM_DATE] = Converter.convert(assignment_details[ParamConstants.PARAM_DATE],
                                                                          Types.TYPE_DATE)

        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).upsert(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE,
             Accessor.PARAM_KEY_OBJECT: assignment_details,
             Accessor.PARAM_KEY_MATCH_PARAMS: {
                 ParamConstants.PARAM_ITEM_KEY: assignment_details[
                     ParamConstants.PARAM_ITEM_KEY],
                 ParamConstants.PARAM_DATE: assignment_details[
                     ParamConstants.PARAM_DATE],
                 ParamConstants.PARAM_GROUP: assignment_details[
                     ParamConstants.PARAM_GROUP],
                 ParamConstants.PARAM_EMPLOYEE: assignment_details[
                     ParamConstants.PARAM_EMPLOYEE]}}), 201

    def delete(self, assignment_id):
        # ToDo: delete assignment id (replace by combined id)
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).delete(
            {Accessor.PARAM_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             Accessor.PARAM_KEY_TYPE: Accessor.PARAM_TYPE_SINGLE,
             Accessor.PARAM_KEY_MATCH_PARAMS: {
                 '_id': ObjectId(assignment_id)}}), 204


class AssignmentValidation(Resource):
    def post(self):
        assignment_details = request.get_json()
        assignment_details[ParamConstants.PARAM_WHRS] = float(
            assignment_details[ParamConstants.PARAM_WHRS])  # ToDo: move typecast into configuration ?
        with open(CFG_ASSIGN_VALIDATION) as env_cfg_file:
            res = Validator(json.load(env_cfg_file, strict=False)).what_if(assignment_details)
        return res, 200 # ToDo: move cfg to constructor/cache
