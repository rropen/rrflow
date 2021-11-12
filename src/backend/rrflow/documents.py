"""
    Houses all mongoengine documents/embedded document templates.

    "Documents" are mongoengine document templates.
    "Schemas" are pydantic data shape models.
"""
from collections import defaultdict
from enum import Enum, unique

import fastapi
import mongoengine
import rrflow.database as database

#SRQ Difficulty Enum
class FlowItemCategory(str, Enum):
    FEAT     = "feature"
    DEFECT   = "defect"
    DEBT     = "debt"
    RISK     = "risk"

class FlowItem(mongoengine.EmbeddedDocument):
    flow_item_categroy = mongoengine.EnumField(FlowItemCategory)
    start_time = mongoengine.DateField()
    end_time   = mongoengine.DateField()
    sum_active = mongoengine.FloatField()
    activity_state = mongoengine.BooleanField()
    comments = mongoengine.StringField()
    last_modified_time = mongoengine.DateField() # not sure why we need this 


class Program(mongoengine.Document):
    program_name = mongoengine.StringField(required = True)
    program_desc = mongoengine.StringField(required = True)
    flow_items   = mongoengine.ListField(mongoengine.EmbeddedDocumentField(FlowItem))
    # flow_item_ids = mongoengine.ListField(mongoengine.ObjectIdField()) <--- A different way of doing it
