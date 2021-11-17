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
    flow_item = documents.FlowItem.objects(id=flow_item_id).first()
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
    flow_item = documents.FlowItem.objects(id=flow_item_id).first()
    if not flow_item:
        logger.debug("Item not found")
        raise HTTPException(status_code=404, detail="Item not found")

    intended_program = documents.Program.objects(id=flow_item.program_id).first()
    if not intended_program:
        logger.debug("program not found")
        raise HTTPException(status_code=404, detail="program not found")
    verified = verify_program_auth_token(
        program_auth_token, intended_program.program_auth_token_hashed
    )
    if verified:
        flow_item.delete()
    else:
        logger.warning("Attempted to access program with incorrect program auth token")
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check our work
    row = refresh_flow_item(flow_item)
    if row:
        logger.error("Item did not delete correctly")
        raise HTTPException(
            status_code=404, detail="Item did not delete correctly"
        )  # Row didn't successfully delete or another one exists
    else:
        return True  # We were successful


def update_flow_item(flow_item_id, flow_item_data, program_auth_token):
    """Take data from request and update an existing flowItem in the database."""
    flow_item = documents.FlowItem.objects(id=flow_item_id).first()
    if not flow_item:
        logger.debug("Item not found")
        raise HTTPException(status_code=404, detail="Item not found")

    # intended_program = documents.Program.objects(id=flow_item.program_id).first()
    intended_program = documents.Program.objects().first()
    if not intended_program:
        logger.debug("program not found")
        raise HTTPException(status_code=404, detail="program not found")
    verified = verify_program_auth_token(
        program_auth_token, intended_program.program_auth_token_hashed
    )

    if verified:
        flow_item_newdata = flow_item_data.dict(exclude_unset=True)
        flow_item.update(**flow_item_newdata) #not sure if this works yet
            
        if flow_item.start_time and flow_item.end_time:
            flow_item.update(duration_open = int((flow_item.end_time - flow_item.start_time).total_seconds()))

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

# def refresh_flow_item(flow_item: documents.FlowItem) -> documents.FlowItem:
    # if flow_item is None:
        # return None
    # return documents.FlowItem.objects(id=flow_item.id).first()