"""
    CRUD for the FlowItem Embedded Document
"""
from fastapi.exceptions import HTTPException
from pydantic.networks import HttpUrl
from rrflow.utils import verify_program_auth_token, program_selector
import logging
from rrflow.config import get_settings
from rrflow.logger import create_logger
import rrflow.documents as documents
import rrflow.schemas as schemas
from bson import ObjectId

from datetime import datetime

app_settings = get_settings()


logger = create_logger(__name__)


def get_all(
    skip: int = 0,
    limit: int = 1000,
    program_id: int = None,
    program_name: str = None,
):
    """Get all the flowItems and return them."""

    program = program_selector(program_name, program_id)
    
    if program:
        return program.flow_items[skip:skip+limit]

    if not program:
        programs = documents.Program.objects()
        if len(programs) == 0:
            raise HTTPException(status_code=404, detail="No Programs found, therefore no FlowItems exist")

        item_list = []
        for program in programs:
            item_list.extend(program.flow_items) 

    return item_list[skip:skip+limit]


def get_by_id(flow_item_id):
    """Get a specified flowItem and return it."""

    # flow_item = documents.Program.objects(flow_items__match={"uid": flow_item_id})
    program = documents.Program.objects(flow_items__match={"uid": flow_item_id}).first()
    flow_item = documents.Program.objects.get(pk=program.id).flow_items.filter(uid=flow_item_id).first()
    
    if flow_item:
        return flow_item
    if not flow_item:
        logger.debug("Item not found")
        raise HTTPException(status_code=404, detail="Item not found")


def create_flow_item(flow_item_data, program_id, program_auth_token):
    """Take data from request and create a new flowItem in the database."""
    intended_program = documents.Program.objects(id=program_id).first()
    #TODO: auth step here
    if not intended_program:
        logger.debug("program not found")
        raise HTTPException(status_code=404, detail="program not found")

    flow_item_to_store = flow_item_data.dict() 
    flow_item_to_store["program_id"] = program_id
    flow_item_db = documents.FlowItem(**flow_item_to_store)
    
    # Embed the FlowItem document to the correct program document
    # VVV TODO: Check that flow_item is not a duplicate
    intended_program.flow_items.append(flow_item_db)
    intended_program.save()

    return flow_item_db


def delete_flow_item(flow_item_id, program_auth_token):
    """Take a issueTitle and remove the row from the database."""
    flow_item = get_by_id(flow_item_id)
    if not flow_item:
        logger.debug("Item not found")
        raise HTTPException(status_code=404, detail="Item not found")

    program = documents.Program.objects(id=flow_item.program_id).first()
    if not program:
        logger.debug("program not found")
        raise HTTPException(status_code=404, detail="program not found")
    # verified = verify_program_auth_token(
    #     program_auth_token, program.program_auth_token_hashed
    # )

    # VVV TODO: Real Authentication
    verified = True
    if verified:
        # flow_item.delete()
        program.flow_items.remove(flow_item)
        program.save()
    else:
        logger.warning("Attempted to access program with incorrect program auth token")
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check our work
    row = refresh_flow_item(flow_item)
    print(row)
    if row:
        logger.error("Item did not delete correctly")
        raise HTTPException(
            status_code=404, detail="Item did not delete correctly"
        )  # Row didn't successfully delete or another one exists
    else:
        return True  # We were successful


def update_flow_item(flow_item_id, flow_item_data, program_auth_token):
    """Take data from request and update an existing flowItem in the database."""
    # flow_item = documents.FlowItem.objects(id=flow_item_id).first()
    flow_item = get_by_id(flow_item_id)

    program = documents.Program.objects(id=flow_item.program_id).first()
    if not program:
        logger.debug("program not found")
        raise HTTPException(status_code=404, detail="program not found")
    # verified = verify_program_auth_token(
        # program_auth_token, intended_program.program_auth_token_hashed
    # )

    # VVV TODO: Real Authentication
    verified = True
    if verified:
        old_flow_item = flow_item
        print(old_flow_item)

        flow_item_new_data = flow_item_data.dict(exclude_unset=True)
        
        flow_item_index = program.flow_items.index(flow_item)

        # update_dict = {
        #     f'set__flow_items__{flow_item_index}__category'     :    flow_item_new_data["category"],
        #     f'set__flow_items__{flow_item_index}__start_time'   :    flow_item_new_data["start_time"],
        #     f'set__flow_items__{flow_item_index}__end_time'     :    flow_item_new_data["end_time"],
        #     f'set__flow_items__{flow_item_index}__sum_active'   :    flow_item_new_data["sum_active"],
        #     f'set__flow_items__{flow_item_index}__active_state' :    flow_item_new_data["active_state"],
        #     f'set__flow_items__{flow_item_index}__comments'     :    flow_item_new_data["comments"],
        #     f'set__flow_items__{flow_item_index}__last_state_change_date' :flow_item_new_data["last_state_change_date"],
        #     f'set__flow_items__{flow_item_index}__program_id'   :    flow_item_new_data["program_id"],
        # }

        update_dict = {}

        print(flow_item_new_data)
        if "category" in flow_item_new_data:
            update_dict.update({f'set__flow_items__{flow_item_index}__category'     :    flow_item_new_data["category"]})
        if "start_time" in flow_item_new_data:
            update_dict.update({f'set__flow_items__{flow_item_index}__start_time'   :    flow_item_new_data["start_time"]})
        if "end_time" in flow_item_new_data:
            update_dict.update({f'set__flow_items__{flow_item_index}__end_time'     :    flow_item_new_data["end_time"]})
        if "duration_open" in flow_item_new_data:
            update_dict.update({f'set__flow_items__{flow_item_index}__duration_open':    flow_item_new_data["duration_open"]})
        if "sum_active" in flow_item_new_data:
            update_dict.update({f'set__flow_items__{flow_item_index}__sum_active'   :    flow_item_new_data["sum_active"]})
        if "active_state" in flow_item_new_data:
            update_dict.update({f'set__flow_items__{flow_item_index}__active_state' :    flow_item_new_data["active_state"]})
        if "comments" in flow_item_new_data:
            update_dict.update({f'set__flow_items__{flow_item_index}__comments'     :    flow_item_new_data["comments"]})
        if "last_state_change_date" in flow_item_new_data:
            update_dict.update({f'set__flow_items__{flow_item_index}__last_state_change_date' :flow_item_new_data["last_state_change_date"]})
        if "program_id" in flow_item_new_data:
            update_dict.update({f'set__flow_items__{flow_item_index}__program_id'   :    flow_item_new_data["program_id"]})
            
        program.update(**update_dict)

        if flow_item.start_time and flow_item.end_time:
            program.update(**{f'set__flow_items__{flow_item_index}__duration_open' : int((flow_item.end_time - flow_item.start_time).total_seconds())})
            program.update(**{f'set__flow_items__{flow_item_index}__active_state' : False}) # Stack Overflow
            # flow_item.update(duration_open = int((flow_item.end_time - flow_item.start_time).total_seconds()))
            # flow_item.update(active_state = False)

        if flow_item.active_state != old_flow_item.active_state:
            program.update(set__flow_items__S__last_state_change_date = datetime.now()) # Stack Overflow
            # flow_item.update(last_state_change_date = datetime.now())

            if flow_item.active_state == False:
                new_sum = flow_item.sum_active + (datetime.now() - old_flow_item.last_state_change_date)
                program.update(set__flow_items__S__sum_active = new_sum) # Stack Overflow

    else:
        logger.warning("Attempted to access program with incorrect program auth token")
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # return updated item
    new_item = refresh_flow_item(flow_item)
    if new_item:
        return new_item  # updated record
    else:
        logger.error("Item did not store correctly")
        raise HTTPException(status_code=404, detail="Item did not store correctly")

def refresh_flow_item(flow_item: documents.FlowItem) -> documents.FlowItem:
    if flow_item is None:
        return None
    try:
        return get_by_id(flow_item.uid)
    except AttributeError:
        return None