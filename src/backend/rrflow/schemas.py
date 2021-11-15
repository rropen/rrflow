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

class FlowItemDisplay(FlowItemBase):
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
        input_dict = item_input.to_mongo().to_dict()
        return FlowItemDisplay.from_mongo(input_dict)

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

class ProgramUpdate(ProgramBase):
    name: Optional[str]
    description: Optional[str]
    flow_items: Optional[List[FlowItem]]
    
class ProgramDisplay(MongoModel):
    name: str
    description: str
    flow_items: List[FlowItem]

    @staticmethod
    def from_doc(item_input: documents.Program):
        input_dict = item_input.to_mongo().to_dict()
        
        disp_prog = ProgramDisplay.from_mongo(input_dict)        
        
        return disp_prog