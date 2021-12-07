import pytest
import rrflow.documents as documents
from datetime import datetime


def test_get_all_route(client, session, db):
    response = client.get("/flowItems/", params={"program_name": "test program 1"})
    assert response.status_code == 200
    assert len(response.json()) == 8
    assert response.json()[0]["category"] == "feature"


def test_get_by_id_route(client, session, db):
    flow_item = documents.Program.objects(name="test program 1").first().flow_items[0]
    response = client.get(
        f"/flowItems/{flow_item.uid}", params={"program_name": "test program 1"}
    )
    assert response.status_code == 200
    assert response.json()["category"] == "feature"
    assert response.json()["start_time"] == "2021-11-01T12:00:00"
    assert response.json()["end_time"] == "2021-11-06T12:00:00"
    assert response.json()["duration_open"] == 432000


def test_post_create_route(client, session, db):
    response = client.post(
        "/flowItems/",
        json={
            "category": "feature",
            "start_time": "2021-11-01T12:00:00",
            "comments": "some comments",
        },
        headers={"program_auth_token": "placeholder"},
        params={"program_name": "test program 1"},
    )
    print(response)
    assert response.status_code == 200
    assert response.json()["category"] == "feature"
    assert response.json()["start_time"] == "2021-11-01T12:00:00"
    assert response.json()["comments"] == "some comments"
    assert response.json()["id"]


def test_patch_update_route(client, session, db):
    patch_body = {"comments": "updated comment"}
    flow_item = documents.Program.objects(name="test program 1").first().flow_items[0]
    response = client.patch(
        f"/flowItems/{flow_item.uid}",
        json=patch_body,
        headers={"program_auth_token": "placeholder"},
    )
    assert response.status_code == 200
    assert response.json()["code"] == "success"
    assert response.json()["id"] == str(flow_item.uid)

    updated_flow_item = (
        documents.Program.objects(name="test program 1").first().flow_items[0]
    )
    assert updated_flow_item.category == "feature"
    assert updated_flow_item.comments == "updated comment"


def test_delete_route(client, session, db):
    # TODO: Implement
    flow_item = documents.Program.objects(name="test program 1").first().flow_items[0]
    print(flow_item.uid)
    url = f"/flowItems/{flow_item.uid}"
    print(url)
    # http://localhost:8181/flowItems/61afb2349e3455321ec276c6
    response = client.delete(url, headers={"program_auth_token": "placeholder"})

    assert response.status_code == 200
    assert response.json()["code"] == "success"
    assert response.json()["message"] == f"FlowItem {flow_item.uid} Deleted"

    test_flow_item = (
        documents.Program.objects(name="test program 1").first().flow_items[0]
    )
    assert test_flow_item.uid != flow_item.uid
