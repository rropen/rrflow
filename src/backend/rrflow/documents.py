"""
    Houses all mongoengine documents/embedded document templates.

    "Documents" are mongoengine document templates.
    "Schemas" are pydantic data shape models.
"""
from enum import Enum
from bson import ObjectId
from rrflow.utility_classes import OID

import mongoengine
from mongoengine import QuerySet
import rrflow.database as database

# SRQ Difficulty Enum
class FlowItemCategory(str, Enum):
    FEAT = "feature"
    DEFECT = "defect"
    DEBT = "debt"
    RISK = "risk"


class FlowItem(mongoengine.EmbeddedDocument):
    uid = mongoengine.ObjectIdField(
        default=ObjectId, required=True, primary_key=True
    )  # NOTE: unique=True causes issues with consecutive empty program create
    category = mongoengine.EnumField(FlowItemCategory)
    start_time = mongoengine.DateTimeField()
    end_time = mongoengine.DateTimeField()
    duration_open = mongoengine.IntField()
    sum_active = mongoengine.FloatField()
    active_state = mongoengine.BooleanField()
    comments = mongoengine.StringField()
    last_state_change_date = mongoengine.DateTimeField()  # not sure why we need this
    program_id = mongoengine.ObjectIdField()


class Program(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    description = mongoengine.StringField(required=True)
    flow_items = mongoengine.EmbeddedDocumentListField(FlowItem)
    # flow_item_ids = mongoengine.ListField(mongoengine.ObjectIdField()) <--- A different way of doing it

    meta = {"db_alias": database.alias, "collection": "programs"}
