from rrflow import utils
import fastapi
from fastapi import APIRouter, Depends, Query, Body
from fastapi.params import Depends
from typing import List
import rrflow.schemas   as schemas
import rrflow.documents as documents
import rrflow.routes.programs.crud as program_crud
from rrflow.utility_classes import OID

router = fastapi.APIRouter()

class CustomGetParams:
    """Custom parameter class for the GET programs route.

    skip = 0 & limit = 100 by default.
    This format enables a custom description field for each parameter that will display
    in the backend swagger docs.
    """

    def __init__(
        self,
        skip: int = Query(
            0,
            description="This parameter sets the number of programs to *skip* at the beginning of the listing.",
        ),
        limit: int = Query(
            1000,
            description="This parameter sets the maximum number of programs to display in the response.",
        ),
    ):
        self.skip = skip
        self.limit = limit

@router.post("/", response_model=schemas.ProgramDisplay)
def create_program(program_data: schemas.ProgramCreate):
    """
    Creates a program in the database
    """
    program = program_crud.create_program(program_data)

    return schemas.ProgramDisplay.from_doc(program)

@router.get("/")
def get_programs(params: CustomGetParams = Depends()) -> List[schemas.ProgramDisplay]:
    """
    ## Get Multiple Programs

    ---

    Query Parameters:

    - **skip**: sets the number of programs to *skip* at the beginning of the listing
    - **limit**: sets the maximum number of programs to display in the listing

    >When used together, *skip* and *limit* facilitate serverside pagination support.

    """
    
    program_docs = program_crud.get_programs(params.skip,params.limit)
    
    program_schemas = []
    for doc in program_docs:
        program_schemas.append(schemas.ProgramDisplay.from_doc(doc))
    
    return program_schemas

@router.get("/{program_id}", response_model=schemas.ProgramDisplay)
def get_program_by_id (program_id: OID):
    """
    Gets program from database with matching id
    """
    program = documents.Program.objects(id=program_id).first()
    return schemas.ProgramDisplay.from_doc(program)

@router.patch("/", response_model=schemas.ProgramDisplay)
def update_program(update_data: schemas.ProgramUpdate, program_name: str = None, program_id: OID = None): # update_data=Body(schemas.ProgramUpdate)):
    program = program_crud.update_program(update_data, program_name, program_id)
    return schemas.ProgramDisplay.from_mongo(program.to_mongo().to_dict())