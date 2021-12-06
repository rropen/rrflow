"""
CRUD for Program Document
"""
from typing import List
from mongoengine.queryset.transform import update
from rrflow.utils import program_selector
from fastapi import HTTPException
import rrflow.schemas as schemas
from rrflow.logger import create_logger
import rrflow.documents as documents
import rrflow.routes.flow_items.crud as flow_item_crud
from rrflow.utility_classes import OID

logger = create_logger(__name__)

# BUG: Making two empty programs consecutively will cause mongo to error out with duplicate null ids for flow-items
def create_program(program_input: schemas.ProgramCreate) -> documents.Program:
    new_program = documents.Program(**program_input.dict())
    new_program.save()

    if new_program is None:
        raise HTTPException(
            status_code=500, detail="Error when creating/saving program!"
        )

    return new_program


def update_program(
    update_data: schemas.ProgramUpdate, program: documents.Program
) -> documents.Program:
    if update_data.description:
        program.update(set__description=update_data.description)

    if update_data.name:
        program.update(set__name=update_data.name)

    program.reload()
    return program


def get_programs(skip, limit) -> List[documents.Program]:
    programs = documents.Program.objects[skip : limit + skip]
    return programs


def delete_program(program: documents.Program, admin_key):
    # TODO: Implement real authentication and verification
    verified = True
    if verified:
        program.delete()

    row = refresh_program(program)
    if row:
        logger.error("Item did not delete correctly")
        raise HTTPException(
            status_code=404, detail="Item did not delete correctly"
        )  # row didn't successfully delete or another one exists
    else:
        return True


def refresh_program(program: documents.Program) -> documents.Program:
    if program is None:
        return None
    try:
        return program_selector(program_id=program.id)
    except AttributeError:
        return None
    pass
