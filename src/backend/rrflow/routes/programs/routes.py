from rrflow import utils
import fastapi
from fastapi import APIRouter, Depends, Query
from fastapi.params import Depends
from typing import List
import rrflow.schemas   as schemas
import rrflow.documents as documents
import rrflow.routes.programs.crud as program_crud

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

@router.post("/", response_model=schemas.Program)
def create_program(program_data: schemas.ProgramCreate):
    """
    Creates a program in the database
    """
    program = program_crud.create_program(program_data)

    return schemas.Program.from_mongo(program.to_mongo().to_dict())

@router.get("/", response_model=List[schemas.Program])
def get_programs(params: CustomGetParams = Depends()):
    """
    ## Get Multiple Programs

    ---

    Query Parameters:

    - **skip**: sets the number of programs to *skip* at the beginning of the listing
    - **limit**: sets the maximum number of programs to display in the listing

    >When used together, *skip* and *limit* facilitate serverside pagination support.

    """
    programs = documents.Program.objects[params.skip:params.limit]
    return programs

@router.get("/{program_id}", response_model=schemas.Program)
def get_program_by_id (program_id: str):
    """
    Gets program from database with matching id
    """
    return documents.Program(id=program_id)