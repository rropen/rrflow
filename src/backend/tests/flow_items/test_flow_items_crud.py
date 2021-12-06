import pytest
from fastapi import HTTPException
from datetime import datetime, timezone
import rrflow.documents as documents
import rrflow.routes.flow_items.crud as crud
from rrflow.utils import program_selector
from rrflow.schemas import FlowItemCreate, FlowItemUpdate


def test_get_all(session, db):
    program = documents.Program.objects(name="test program 1").first()
    response = crud.get_all(skip=0, limit=100, program=program)
    assert len(response) == 8

    response = crud.get_all(skip=1, limit=2, program=program)
    assert len(response) == 2
    print(response)
    assert response[0].category == "feature"
    assert response[0].start_time == datetime.strptime(
        "2021-11-02T12:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"
    )
    assert response[0].end_time == datetime.strptime(
        "2021-11-05T12:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"
    )
    assert response[0].duration_open == 259200
    assert response[0].sum_active == 129600
    assert response[0].active_state == False
    assert response[0].comments == "Some comments"


def test_get_by_id(session, db):
    program = documents.Program.objects(name="test program 1").first()
    flow_item = program.flow_items[0]
    response = crud.get_by_id(flow_item.uid)
    assert response["category"] == "feature"
    assert response["start_time"] == datetime.strptime(
        "2021-11-01T12:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"
    )
    assert response["end_time"] == datetime.strptime(
        "2021-11-06T12:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z"
    )
    assert response["duration_open"] == 432000
    assert response["sum_active"] == 86400
    assert response["active_state"] == False
    assert response["comments"] == "some comments"
    with pytest.raises(HTTPException) as ex:
        crud.get_by_id(
            "61ae83ad3b5fdf66a1fa4b12"
        )  # NOTE: this has a extremely small likelihood of being an actual flow item id
    assert ex.value.status_code == 404


def test_create(session, db):
    program = program_selector(program_name="test program 1")
    flow_item_data = {
        "category": "debt",
        "start_time": "2021-11-02T12:00:00.000Z",
        "end_time": "2021-11-02T12:01:00.000Z",
        "sum_active": 2000,
        "active_state": True,
        "comments": "Some comments",
    }

    flow_item_schema = FlowItemCreate(**flow_item_data)
    response = crud.create_flow_item(flow_item_schema, program, "some_auth_token")

    assert response.category == "debt"
    assert response.start_time == datetime(
        2021, 11, 2, 12, 0, tzinfo=timezone.utc
    )  # Different than above because pydantic adds tzinfo when converting to schema
    assert response.sum_active == 2000
    assert response.active_state == False
    assert response.comments == "Some comments"
    assert response.end_time == datetime(2021, 11, 2, 12, 1, tzinfo=timezone.utc)
    assert response.duration_open == 60
    assert response.program_id != None


def test_delete(session, db):
    program = documents.Program.objects(name="test program 1").first()
    flow_item = program.flow_items[0]
    response = crud.delete_flow_item(flow_item.uid, "admin_key")
    assert response == True

    program.reload()
    zero_index_item = program.flow_items[0]
    assert flow_item.uid != zero_index_item.uid


def test_update(session, db):
    program = documents.Program.objects(name="test program 1").first()
    flow_item = program.flow_items[0]

    flow_item_update = {
        "category": "debt",
        "active_state": True,
    }

    flow_item_data = FlowItemUpdate(**flow_item_update)
    response = crud.update_flow_item(flow_item.uid, flow_item_data, "admin_key")

    assert response.category == "debt"
    assert response.end_time == None
    assert response.active_state == True
    assert response.last_state_change_date != flow_item.last_state_change_date

    program = documents.Program.objects(name="test program 1").first()
    flow_item = program.flow_items[0]
