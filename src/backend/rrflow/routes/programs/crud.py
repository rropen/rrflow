"""
CRUD for Program Document
"""
from typing import List
from rrflow.utils import program_selector
from fastapi import HTTPException
import rrflow.schemas as schemas
import rrflow.documents as documents
from rrflow.utility_classes import OID


def create_program(program_input: schemas.ProgramCreate) -> documents.Program:
    print('In create program crud')
    new_program = documents.Program(**program_input.dict())
    print('new program after creation dict')

    print(new_program)
    if new_program is None:
        raise HTTPException(status_code=500, detail="Error when creating/saving program!")

    return new_program


def update_program(update_data = schemas.ProgramUpdate, program_name: str = None, program_id: int = None) -> documents.Program:
    # testing id type
    program = program_selector(program_name, program_id)
    
    try:
        print(type(program.id))
    except:
        print(type(program._id))
        print(type(program._id) == OID)
    ###


    if update_data.flow_items:
        documents.Program.objects(name=program_name).update(add_to_set__flow_items=update_data.flow_items)
    
    if update_data.description:
        documents.Program.objects(name=program_name).update_one(set__description=update_data.description) 
    
    return program

def get_programs(skip, limit) -> List[documents.Program]:
    programs = documents.Program.objects[skip:limit+skip]
    return programs