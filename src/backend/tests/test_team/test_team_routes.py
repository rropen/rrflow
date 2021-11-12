import pytest
from bson import ObjectId
from rrflow import main
from rrflow import schemas, documents
from starlette.testclient import TestClient
import rrflow.routes.team.routes as team_routes

def test_team_create_endpoint(client: TestClient, mocker):
    team_lead = {
        "first_name": "Tony",
        "last_name": "Stark",
        "email": "ironman@starkEnterprises.com"
    }
    list_members = [
        { 
            "first_name": "Tony",
            "last_name": "Stark",
            "email": "ironman@starkEnterprises.com"
        },
        {
            "first_name": "Loki",
            "last_name": "Thunderclaw",
            "email": "hulkfan@starkEnterprises.com"
        },
        {
            "first_name": "Thanos",
            "last_name": "Harmonizer",
            "email": "goodguy@starkEnterprises.com"
        }
    ]

    team_input = {
        "team_name": "The Balancers",
        "team_lead": team_lead, 
        "team_members": list_members
    }

    mocked_team = documents.Team(**{
        "id": ObjectId(),
        "team_name": "The Balancers",
        "team_lead_id": ObjectId(),
        "team_member_ids": [ObjectId(),ObjectId(),ObjectId()]
    })

    mocker.patch('vvuq.routes.team.routes.team_crud.create_team', return_value = mocked_team)
    mocker.patch('vvuq.routes.team.routes.team_crud.documents.UserRole.enforce_at_or_above', return_value = None)

    #This is how you patch a dependency (like get current user)
    #lamda: None is just slick representation of a function that returns None
    main.app.dependency_overrides[team_routes.get_current_user] = lambda: None
    
    response = client.post("/teams/", json=team_input)
    team_id = response.json()["id"]
    print(response.json())
    assert response is not None

    response2 = client.get(f"/teams/{team_id}")
    print(response2.json())
    assert response2 is not None