"""
    Pydantic models of our mongoengine models.

    We are calling pydantic models "schemas" to reduce confusion
    since other SF apps use "schemas" to represent pydantic models.

    "Documents" are mongoengine documents.
    "Schemas" are pydantic data shape models.
"""
from typing import List, Optional
from datetime import datetime

import rrflow.documents as documents
from rrflow.utility_classes import OID, MongoModel

### FlowItem ###
class FlowItemBase(MongoModel):
    category:           Optional[documents.FlowItemCategory]
    start_time:         Optional[datetime]
    end_time:           Optional[datetime]
    sum_active:         Optional[float]
    active_state:     Optional[bool]
    comments:           Optional[str]
    last_state_change_date: Optional[datetime]

class FlowItem(FlowItemBase):
    program_id: Optional[OID]
    duration_open: Optional[int]
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
    duration_open: Optional[int]
    sum_active: Optional[float]
    active_state: Optional[bool]
    comments: Optional[str]
    last_state_change_date: Optional[datetime]
    program_id: Optional[OID]

    @staticmethod
    def from_doc(item_input: documents.FlowItem):
        input_dict = item_input.to_mongo().to_dict()
        return FlowItemDisplay.from_mongo(input_dict)

### Program ###
class ProgramBase(MongoModel):
    name: str
    description: str
    # flow_item_ids: List[OID] <-- A different way of doing it
    

class Program(ProgramBase):
    id: OID
    flow_items: Optional[List[FlowItem]]
    pass

class ProgramCreate(ProgramBase):
    pass

class ProgramUpdate(MongoModel):
    name: Optional[str]
    description: Optional[str]
    
class ProgramDisplay(MongoModel):
    id: OID
    name: str
    description: str
    flow_items: Optional[List[FlowItem]]

    @staticmethod
    def from_doc(item_input: documents.Program):
        input_dict = item_input.to_mongo().to_dict()
        
        disp_prog = ProgramDisplay.from_mongo(input_dict)        
        
        return disp_prog