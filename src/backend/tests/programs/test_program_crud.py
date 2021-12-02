import pytest
import rrflow.documents as documents


def test_program_create(session, db):
    program = documents.Program.objects().first()
    for item in program.flow_items:
        print(item.start_time)
    assert 1==2
    
def test_program_update(session, db):
    # TODO: Implement Program Update Crud Testing
    assert 1==2

def test_program_get_all(session, db):
    # TODO: Implement Program Get Crud Testing
    assert 1==2
    
def test_program_get_by_id(session, db):
    # TODO: Implement Program Get by Id Crud Testing
    assert 1==2

def test_program_delete(session, db):
    # TODO: Implement Program delete crud testing
    assert 1==2
