import pytest
from rrflow.utils import program_selector
from fastapi import HTTPException


def test_program_selector(session, db):
    program = program_selector(program_name="test program 1")
    pid = program.id

    assert program
    assert program.name == "test program 1"

    program = program_selector(program_id=pid)
    assert program
    assert program.name == "test program 1"

    program = program_selector(program_name="test program 1", program_id=pid)
    assert program
    assert program.name == "test program 1"

    with pytest.raises(HTTPException) as ex:
        program = program_selector()
    assert ex.value.status_code == 404
    assert ex.value.detail == "No program selection criterion passed"

    with pytest.raises(HTTPException) as ex:
        program = program_selector(program_id="61b22e1b8cb8bfa88a6d084d")
    assert ex.value.status_code == 404
    assert (
        ex.value.detail
        == "No program found with the specified id: 61b22e1b8cb8bfa88a6d084d"
    )

    with pytest.raises(HTTPException) as ex:
        program_selector(program_name="Trash")
    assert ex.value.status_code == 404
    assert ex.value.detail == "No program found with the specified name: Trash"

    with pytest.raises(HTTPException) as ex:
        program_selector(program_name="Trash", program_id=pid)
    assert ex.value.status_code == 404
    assert (
        ex.value.detail
        == "Either the program_name and program_id do not match, or there is not a program with the specified details. Try passing just one of the parameters instead of both."
    )

    with pytest.raises(HTTPException) as ex:
        program_selector(
            program_name="test program 1", program_id="61b22e1b8cb8bfa88a6d084d"
        )  # extremely small chance this id actually gets generated and is correct
    assert ex.value.status_code == 404
    assert (
        ex.value.detail
        == "Either the program_name and program_id do not match, or there is not a program with the specified details. Try passing just one of the parameters instead of both."
    )
