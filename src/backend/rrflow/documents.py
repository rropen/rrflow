"""
    Houses all mongoengine documents/embedded document templates.

    "Documents" are mongoengine document templates.
    "Schemas" are pydantic data shape models.
"""
from enum import Enum
from bson import ObjectId
from rrflow.utility_classes import OID

import mongoengine
import rrflow.database as database

#SRQ Difficulty Enum
class FlowItemCategory(str, Enum):
    FEAT     = "feature"
    DEFECT   = "defect"
    DEBT     = "debt"
    RISK     = "risk"

class FlowItem(mongoengine.EmbeddedDocument):
    _id = mongoengine.ObjectIdField(default=ObjectId())
    category = mongoengine.EnumField(FlowItemCategory)
    start_time = mongoengine.DateField()
    end_time   = mongoengine.DateField()
    sum_active = mongoengine.FloatField()
    active_state = mongoengine.BooleanField()
    comments = mongoengine.StringField()
    last_state_change_date = mongoengine.DateField() # not sure why we need this 
    program_id = mongoengine.ObjectIdField()


class Program(mongoengine.Document):
    name = mongoengine.StringField(required = True)
    description = mongoengine.StringField(required = True)
    flow_items   = mongoengine.EmbeddedDocumentListField(FlowItem)
    # flow_item_ids = mongoengine.ListField(mongoengine.ObjectIdField()) <--- A different way of doing it

    meta = {"db_alias": database.alias, "collection": "programs"}