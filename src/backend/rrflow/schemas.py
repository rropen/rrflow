"""
    Pydantic models of our mongoengine models.

    We are calling pydantic models "schemas" to reduce confusion
    since other SF apps use "schemas" to represent pydantic models.

    "Documents" are mongoengine documents.
    "Schemas" are pydantic data shape models.
"""
from typing import List, Optional
from enum import Enum, IntEnum
from datetime import date, datetime

import rrflow.documents as documents
from rrflow.utility_classes import OID, MongoModel

### FlowItem ###
class FlowItemBase(MongoModel):
    category:           Optional[documents.FlowItemCategory]
    start_time:         Optional[datetime]
    end_time:           Optional[datetime]
    sum_active:         Optional[float]
    activity_state:     Optional[bool]
    comments:           Optional[str]
    last_modified_time: Optional[datetime]

class FlowItem(FlowItemBase):
    pass

class FlowItemCreate(FlowItemBase):
    pass

class FlowItemUpdate(FlowItemBase):
    pass

class FlowItemDisplay(MongoModel):
    id: OID
    category: Optional[documents.FlowItemCategory]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    sum_active: Optional[float]
    activity_state: Optional[bool]
    comments: Optional[str]
    last_modified_time: Optional[datetime]

    @staticmethod
    def from_doc(item_input: documents.FlowItem):
        return(FlowItem(item_input.to_mongo().to_dict()))

### Program ###
class ProgramBase(MongoModel):
    name: str
    description: str
    flow_items: List[FlowItem]
    # flow_item_ids: List[OID] <-- A different way of doing it
    

class Program(ProgramBase):
    pass

class ProgramCreate(ProgramBase):
    pass
