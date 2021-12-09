import pytest
import rrflow.documents as documents


def test_get_program_route(client, session, db):
    response = client.get("/programs/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test program 1"


def test_post_program_route(client, session, db):
    response = client.post(
        "/programs/",
        json={
            "name": "a new creation",
            "description": "test creation on route endpoint",
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "a new creation"
    assert response.json()["description"] == "test creation on route endpoint"
    assert response.json()["flow_items"] == []
    assert response.json()["id"]


def test_get_specific_program_route(client, session, db):
    response = client.get(
        "/programs/specific/", params={"program_name": "test program 1"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test program 1"
    assert response.json()["description"] == "a test description"
    assert len(response.json()["flow_items"]) == 8


def test_patch_program_update(client, session, db):
    patch_body = {"description": "updated description"}
    response = client.patch(
        "programs/", params={"program_name": "test program 1"}, json=patch_body
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test program 1"
    assert response.json()["description"] == "updated description"
    assert len(response.json()["flow_items"]) == 8


def test_delete_program(client, session, db):
    response = client.delete(
        "/programs/",
        params={"program_name": "test program 1", "admin_key": "admin-key"},
    )
    assert response.status_code == 200
    assert response.json()["code"] == "success"
    assert response.json()["message"] != None
