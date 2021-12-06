from fastapi.exceptions import HTTPException
import pytest
import rrflow.documents as documents
import rrflow.routes.programs.crud as crud
from rrflow.utils import program_selector
from rrflow.schemas import ProgramCreate, ProgramUpdate


def test_program_create(session, db):
    input_dict = {
        "name": "test program",
        "description": "a description string",
        "flow_items:": [
            {
                "category": "feature",
                "active_state": True,
            }
        ],
    }

    response = crud.create_program(ProgramCreate(**input_dict))

    assert response.name == "test program"
    assert response.description == "a description string"
    assert response.flow_items == []

    input_dict = {
        "name": "test program 2",
        "description": "a new description string",
        "flow_items:": [
            {
                "category": "defect",
                "active_state": False,
            }
        ],
    }

    response = crud.create_program(ProgramCreate(**input_dict))

    assert response.name == "test program 2"
    assert response.description == "a new description string"
    assert response.flow_items == []


def test_program_update(session, db):
    program = documents.Program.objects(name="test program 1").first()

    input_dict = {
        "name": "a different name",
        "description": "a new description string",
        "flow_items:": [
            {
                "category": "defect",
                "active_state": False,
            }
        ],
    }
    updated_program = crud.update_program(ProgramUpdate(**input_dict), program)
    assert updated_program.name == "a different name"
    assert updated_program.description == "a new description string"
    assert updated_program.flow_items == program.flow_items


def test_get_programs(session, db):
    # Create 2 new programs for this test to test skip, limit
    input_dict = {
        "name": "test program",
        "description": "a description string",
    }
    documents.Program(**input_dict).save()
    input_dict = {
        "name": "another test program",
        "description": "a description string",
    }
    documents.Program(**input_dict).save()

    response = crud.get_programs(0, 100)
    assert len(response) == 3

    response = crud.get_programs(1, 2)
    assert len(response) == 2
    assert response[0].name == "test program"


def test_program_delete(session, db):
    program = documents.Program.objects(name="test program 1").first()
    response = crud.delete_program(program, "admin_key")

    assert response == True
    program = documents.Program.objects(name="test program 1").first()
    assert not program
