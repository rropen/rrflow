"""
    CRUD for the FlowItem Embedded Document
"""
from fastapi.exceptions import HTTPException
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


def get_all(*, skip: int = 0, limit: int = 1000, program: documents.Program):
    """Get all the flowItems and return them."""
    # TODO: functionality to return all flowItems for all programs

    if program:
        return program.flow_items[skip : skip + limit]

    # if not program:
    #     programs = documents.Program.objects()
    #     if len(programs) == 0:
    #         raise HTTPException(status_code=404, detail="No Programs found, therefore no FlowItems exist")

    #     item_list = []
    #     for program in programs:
    #         item_list.extend(program.flow_items)

    # return item_list[skip:skip+limit]


def get_by_id(flow_item_id):
    """Get a specified flowItem and return it."""

    # flow_item = documents.Program.objects(flow_items__match={"uid": flow_item_id})
    program = documents.Program.objects(flow_items__match={"uid": flow_item_id}).first()
    if program == None:
        raise HTTPException(
            status_code=404, detail="Flow_item with matching Id does not exist"
        )
    flow_item = (
        documents.Program.objects.get(pk=program.id)
        .flow_items.filter(uid=flow_item_id)
        .first()
    )

    return flow_item


def create_flow_item(flow_item_data, program: documents.Program, program_auth_token):
    """Take data from request and create a new flowItem in the database."""
    # TODO: auth step here
    flow_item_to_store = flow_item_data.dict()
    flow_item_to_store["program_id"] = program.id

    if flow_item_to_store["end_time"]:
        flow_item_to_store["duration_open"] = int(
            (
                flow_item_to_store["end_time"] - flow_item_to_store["start_time"]
            ).total_seconds()
        )
        if flow_item_to_store["duration_open"] < 0:
            raise AssertionError("Start time is later than end time")
        flow_item_to_store["active_state"] = False
    flow_item_db = documents.FlowItem(**flow_item_to_store)

    # Embed the FlowItem document to the correct program document
    # VVV TODO: Check that flow_item is not a duplicate
    program.flow_items.append(flow_item_db)
    program.save()

    return flow_item_db


def delete_flow_item(flow_item_id, program_auth_token):
    """Take a issueTitle and remove the row from the database."""
    flow_item = get_by_id(flow_item_id)

    program = documents.Program.objects(id=flow_item.program_id).first()
    if not program:  # pragma: no cover
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
    row = refresh_flow_item(flow_item, raise_404=False)
    if row:  # pragma: no cover
        logger.error("Item did not delete correctly")
        raise HTTPException(
            status_code=404, detail="Item did not delete correctly"
        )  # Row didn't successfully delete or another one exists
    else:
        return True  # We were successful


def update_flow_item(flow_item_id, flow_item_data, program_auth_token):
    """Take data from request and update an existing flowItem in the database."""

    flow_item = get_by_id(flow_item_id)

    program = documents.Program.objects(id=flow_item.program_id).first()
    if not program:  # pragma: no cover
        logger.debug("program not found")
        raise HTTPException(status_code=404, detail="program not found")
    # verified = verify_program_auth_token(
    # program_auth_token, intended_program.program_auth_token_hashed
    # )

    # VVV TODO: Real Authentication
    verified = True
    if verified:
        old_flow_item = flow_item

        flow_item_new_data = flow_item_data.dict(exclude_unset=True)

        flow_item_index = program.flow_items.index(flow_item)

        update_dict = {}

        # TODO: Increase coverage via thorough testing
        if "category" in flow_item_new_data:
            update_dict.update(
                {
                    f"set__flow_items__{flow_item_index}__category": flow_item_new_data[
                        "category"
                    ]
                }
            )
        if "start_time" in flow_item_new_data:
            update_dict.update(
                {
                    f"set__flow_items__{flow_item_index}__start_time": flow_item_new_data[
                        "start_time"
                    ]
                }
            )
        if "end_time" in flow_item_new_data:
            update_dict.update(
                {
                    f"set__flow_items__{flow_item_index}__end_time": flow_item_new_data[
                        "end_time"
                    ]
                }
            )
        if "sum_active" in flow_item_new_data:
            update_dict.update(
                {
                    f"set__flow_items__{flow_item_index}__sum_active": flow_item_new_data[
                        "sum_active"
                    ]
                }
            )
        if "active_state" in flow_item_new_data:
            update_dict.update(
                {
                    f"set__flow_items__{flow_item_index}__active_state": flow_item_new_data[
                        "active_state"
                    ]
                }
            )
        if "comments" in flow_item_new_data:
            update_dict.update(
                {
                    f"set__flow_items__{flow_item_index}__comments": flow_item_new_data[
                        "comments"
                    ]
                }
            )

        program.update(**update_dict)
        program.reload()

        if (
            program.flow_items[flow_item_index].active_state
            != old_flow_item.active_state
        ):
            program.update(
                **{
                    f"set__flow_items__{flow_item_index}__last_state_change_date": datetime.now()
                }
            )  # Stack Overflow
            program.reload()

            if program.flow_items[flow_item_index].active_state == False:
                if old_flow_item.last_state_change_date == None:
                    new_sum = (datetime.now() - program.flow_items[flow_item_index].start_time).total_seconds()
                elif old_flow_item.last_state_change_date:
                    new_sum = program.flow_items[flow_item_index].sum_active + (datetime.now() - old_flow_item.last_state_change_date).total_seconds()
                program.update(
                    **{f"set__flow_items__{flow_item_index}__sum_active": new_sum}
                )  # Stack Overflow
                
                program.reload()

            elif program.flow_items[flow_item_index].active_state == True:
                program.update(
                    **{f"set__flow_items__{flow_item_index}__end_time": None}
                )  # Stack Overflow
                program.reload()

        if (
            program.flow_items[flow_item_index].start_time
            and program.flow_items[flow_item_index].end_time
        ):
            program.update(
                **{
                    f"set__flow_items__{flow_item_index}__duration_open": int(
                        (
                            program.flow_items[flow_item_index].end_time
                            - program.flow_items[flow_item_index].start_time
                        ).total_seconds()
                    )
                }
            )
            program.update(
                **{f"set__flow_items__{flow_item_index}__active_state": False}
            )  # Stack Overflow
            program.reload()

    else:
        logger.warning("Attempted to access program with incorrect program auth token")
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    return program.flow_items[flow_item_index]


def refresh_flow_item(
    flow_item: documents.FlowItem, raise_404=True
) -> documents.FlowItem:  # pragma: no cover
    if flow_item is None:
        return None
    try:
        return get_by_id(flow_item.uid)
    except HTTPException:
        return None
