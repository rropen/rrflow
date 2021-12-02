import pytest
import rrflow.documents as documents


def test_get_program_route(client, session, db):
    # TODO: Implement get program route testing
    program = documents.Program.objects().first()
    assert 1==2
    
def test_get_specific_program_route(client, session, db):
    # TODO: Implement get specific program route testing
    assert 1==2

def test_patch_program_update(client, session, db):
    # TODO: Implement patch program update route testing
    assert 1==2