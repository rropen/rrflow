"""
CRUD for Program Document
"""
from typing import List

from mongoengine.queryset.transform import update
from rrflow.utils import program_selector
from fastapi import HTTPException
import rrflow.schemas as schemas
import rrflow.documents as documents
import rrflow.routes.flow_items.crud as flow_item_crud
from rrflow.utility_classes import OID

def create_program(program_input: schemas.ProgramCreate) -> documents.Program:
    new_program = documents.Program(**program_input.dict())
    new_program.save()

    if new_program is None:
        raise HTTPException(status_code=500, detail="Error when creating/saving program!")

    return new_program


def update_program(update_data = schemas.ProgramUpdate, program_name: str = None, program_id: OID = None) -> documents.Program:
    program = program_selector(program_name, program_id)
    
    if update_data.description:
        program.update(set__description=update_data.description) 
        
    if update_data.name:
        program.update(set__name=update_data.name)
    
    program.reload()
    return program

def get_programs(skip, limit) -> List[documents.Program]:
    programs = documents.Program.objects[skip:limit+skip]
    return programs