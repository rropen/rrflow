import pytest
import rrflow.documents as documents


def test_get_all_route(client, session, db):
    response = client.get("/flowItems/", params={"program_name": "test program 1"})
    assert response.status_code == 200
    assert len(response.json()) == 8
    assert response.json()[0]["category"] == "feature"


def test_get_by_id_route(client, session, db):
    # TODO: Implement
    pass
    # assert 1==2


def test_post_create_route(client, session, db):
    response = client.post(
        "/flowItems/",
        params={"program_name": "test program 1"},
        json = {
                "category": "feature",
                "start_time": "2021-11-01T12:00:00.000z",
                "comments": "some comments"
            },
    )
    assert response.status_code == 200
    assert response.json()["category"] == "feature"
    assert response.json()["start_time"] == "2021-11-01T12:00:00.000z"
    assert response.json()["comments"] == "some comments"
    assert response.json()["id"]


def test_patch_update_route(client, session, db):
    patch_body = {"comments": "updated comment"}
    flow_item = documents.Program.objects(name="test program 1").flow_items[0]
    response = client.patch(
        "flowItems/", params={"flow_item_id": str(flow_item.uid)}, json=patch_body
    )
    assert response.status_code == 200
    assert response.json()["category"] == "feature"
    assert response.json()["description"] == "updated comment"

    updated_flow_item = documents.Program.objects(name="test program 1").flow_items[0]
    assert updated_flow_item.category == "feature"
    assert updated_flow_item.description == "updated comment"



def test_delete_route(client, session, db):
    # TODO: Implement
    flow_item = documents.Program.objects(name="test program 1").flow_items[0]
    response = client.delete(
        "flowItems/", params={"flow_item_id": str(flow_item.uid)}, header={"program_auth_token": "placeholder"}
    )
    assert response.status_code == 200
    assert response.json()["code"] == "success"
    assert response.json()["message"] == f"FlowItem {flow_item.uid} Deleted"


    test_flow_item = documents.Program.objects(name="test program 1").flow_items[0]
    assert test_flow_item.uid != flow_item.uid
