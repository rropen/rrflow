"""
CRUD for Program Embedded Document
"""
from typing import List
from rrflow.utils import program_selector
import fastapi
import rrflow.schemas as schemas
import rrflow.documents as documents


def create_program(program_input: schemas.ProgramCreate) -> documents.Program:
    
    new_program = documents.Program(**program_input.dict())

    new_program.save()
    new_program = documents.Program(id=new_program.id)

    if new_program is None:
        raise fastapi.HTTPException(status_code=500, detail="Error when creating/saving program!")

    return new_program
