from rrflow.routes.flow_items import crud
from rrflow.logger import create_logger
from rrflow.config import get_settings
from rrflow.utility_classes import OID
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Path, Header, Depends
import logging
import rrflow.schemas as schemas
from rrflow.dependencies import Program_Params

app_settings = get_settings()

logger = create_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[schemas.FlowItemDisplay])
def get_flow_items(
    skip: int = 0, limit: int = 100, p_params: Program_Params = Depends()
):
    """
    ## Get FlowItems

    Get a list of all the FlowItems stored in the database.

    Query Parmeters:

    ---

    - **skip**: sets the number of items to skip at the beginning of the listing
    - **limit**: sets the max number of items to be displayed when called
    - **program_id**: specifying **program_id** returns only flow items in a given program
    - **program_name**: specifying **program_name** returns only flow items in a given program
    """
    flow_docs = crud.get_all(skip=skip, limit=limit, program=p_params.program)

    if not flow_docs:
        raise HTTPException(
            status_code=404, detail="FlowItems not found"
        )  # pragma: no cover

    flow_schemas = []
    for doc in flow_docs:
        flow_schemas.append(schemas.FlowItemDisplay.from_doc(doc))

    return flow_schemas


### VVV TODO: Makes no sense, embedded documents do not have IDs
@router.get("/{flow_item_id}")
def get_flow_item(flow_item_id: OID):
    """
    ## Get FlowItem by ID

    Get a specific FlowItem by specifying the ID in the path.

    ---

    Path Parameters:

    -**flow_item_id**: id of the flow item to be requested

    """
    flow_item = crud.get_by_id(flow_item_id)
    if not flow_item:
        logger.debug("FlowItem not found")
        raise HTTPException(
            status_code=404, detail="FlowItem not found"
        )  # pragma: no cover
    return schemas.FlowItemDisplay.from_doc(flow_item)


@router.post("/")
def create_flow_item(
    *,
    flow_item_data: schemas.FlowItemCreate,
    program_auth_token: str = Header(None),
    p_params: Program_Params = Depends()
):
    """
    ## Create FlowItem entry in db

    Create a new FlowItem in the database by specifying data in the request.

    ---

    Request Headers:

    - **program_auth_token**: authentication key to allow for major changes to occur to program data (specific to the FlowItem's program)

    ---

    Request Body Parameters:

    - **flow_item_category**: category for the flow item. Must be one of the following options:
        1. "Feat"
        2. "Defect"
        3. "Debt"
        4. "Risk"
    - **start_time**: sets the start time of the FlowItem
    - **end_time**: sets the end time of the FlowItem (could be merged date or closed date depending on metric needs for the specified FlowItem category)
    - **sum_active**: sum of time where the FlowItem was in the active state
    - **active_state**: boolean value for activity state (0 for inactive, 1 for active)
    - **comments**: string to hold comments about the FlowItem
    - **last_state_change_date**: datetime for when the item was last modified
    - **program_id**: sets program the FlowItem belongs to
    """

    # Creates the database row and stores it in the table
    print("in route")
    new_flow_item_success = crud.create_flow_item(
        flow_item_data, p_params.program, program_auth_token
    )
    print("past the crud")
    if new_flow_item_success:
        return schemas.FlowItemDisplay.from_doc(new_flow_item_success)
    else:
        logger.error("FlowItem not stored correctly")
        raise HTTPException(status_code=500, detail="Row not created")


@router.patch("/{flow_item_id}")
def update_flow_item(
    flow_item_id: OID,
    flow_item_data: schemas.FlowItemUpdate,
    program_auth_token: str = Header(None),
):
    """
    ## Update FlowItem

    Update an existing FlowItem in the database from the data provided in the request.

    ---

    Path Parameters:

    - **flow_item_id**: selects FlowItem being open

    ---

    Request Headers:

    - **program_auth_token**: authentication key to allow for major changes to occur to program data (specific to the FlowItem's program)

    ---

    Request Body Parameters:

    - **flow_item_category**: category for the flow item. Must be one of the following options:
        1. "Feat"
        2. "Defect"
        3. "Debt"
        4. "Risk"
    - **start_time**: sets the start time of the FlowItem
    - **end_time**: sets the end time of the FlowItem (could be merged date or closed date depending on metric needs for the specified FlowItem category)
    - **sum_active**: sum of time where the FlowItem was in the active state
    - **active_state**: boolean value for activity state (0 for inactive, 1 for active)
    - **comments**: string to hold comments about the FlowItem
    - **last_state_change_date**: datetime for when the item was last modified
    - **program_id**: sets program the FlowItem belongs to
    """
    updated_flow_item = crud.update_flow_item(
        flow_item_id, flow_item_data, program_auth_token
    )

    if update_flow_item:
        return {
            "code": "success",
            "id": str(updated_flow_item.uid),
        }
    else:
        logger.error("Updated flowitem not stored")
        return {"code": "error", "message": "Row not updated"}  # pragma: no cover


# Since  FlowItem has no name, use database id to delete item
@router.delete("/{flow_item_id}")
def delete_flow_item(flow_item_id: OID, program_auth_token: str = Header(None)):
    """
    ## Delete a FlowItem

    Pass a FlowItem database id value in the path and the FlowItem will be deleted from the database.

    ---

    Path Parameters:

    - **flow_item_id**: selects FlowItem being open

    ---

    Request Headers:

    - **program_auth_token**: authentication key to allow for major changes to occur to program data (specific to the FlowItem's program)
    """
    response = crud.delete_flow_item(flow_item_id, program_auth_token)

    if response:
        return {
            "code": "success",
            "message": "FlowItem {} Deleted".format(flow_item_id),
        }
    else:  # pragma: no cover
        logger.error("FlowItem not deleted")
        return {
            "code": "error",
            "message": "FlowItem not deleted or multiple FlowItems with same flow_item_id existed.",
        }
