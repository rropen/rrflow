import pytest
from fastapi import HTTPException
import rrflow.routes.team.crud as team_crud
import rrflow.schemas as schemas
import rrflow.documents as documents
import tests.utils as testing_utils


def test_team_crud(db, mocker):
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
    team_data = {
        "team_name": "The Balancers",
        "team_lead": team_lead,
        "team_members": list_members
    }
    first_names = [o["first_name"] for o in list_members] 
    last_names  = [o["last_name"] for o in list_members] 
    emails      = [o["email"] for o in list_members] 

    team_input = schemas.TeamCreate(**team_data)
    #Bypass user auth check for unit test:
    mocker.patch('vvuq.documents.UserRole.enforce_at_or_above', return_value=None)
    created_doc = team_crud.create_team(team_input, current_user=None)

    assert created_doc.team_name == "The Balancers"
    created_team_lead = documents.Person.objects(id=created_doc.team_lead_id).first() 
    assert created_team_lead.first_name == "Tony"
    assert created_team_lead.last_name == "Stark"
    assert created_team_lead.email == "ironman@starkEnterprises.com"
    for id, expected_first in zip(created_doc.team_member_ids, first_names):
        assert documents.Person.objects(id=id).first().first_name == expected_first
    for id, expected_last in zip(created_doc.team_member_ids, last_names):
        assert documents.Person.objects(id=id).first().last_name == expected_last
    for id, expected_email in zip(created_doc.team_member_ids, emails):
        assert documents.Person.objects(id=id).first().email == expected_email

    # Testing that the crud works correctly when a team with existing emails is made 
    before_length = len(documents.Person.objects)
    team_data["team_lead"] = testing_utils.initial_team["team_lead"]
    team_input = schemas.TeamCreate(**team_data)
    created_doc = team_crud.create_team(team_input, current_user=None)
    after_length = len(documents.Person.objects)
    assert before_length == after_length



def test_find_by_id(db):
    # Test working as expected
    existing_id = documents.Team.objects.first().id
    team_found = team_crud.find_team_by_id(existing_id, raise_404=True) 
    assert documents.Person.objects(id=team_found.team_lead_id).first().first_name == "Test"

    # Test function raises exception when id of non-existing team is passed
    team_found.delete()
    non_existing_id = existing_id
    with pytest.raises(HTTPException) as ex:
        team_crud.find_team_by_id(non_existing_id, raise_404=True)

def test_refresh_team(db):
    existing_team = documents.Team.objects.first()
    refreshed_team = existing_team

    #Change existing team name:
    existing_team.team_name = "New Name"

    existing_team.save()

    #Refresh team:
    refreshed_team = team_crud.refresh_team(existing_team)

    assert refreshed_team.team_name == "New Name"