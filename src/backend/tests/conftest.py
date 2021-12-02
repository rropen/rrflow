import pytest
import mongoengine
from starlette.testclient import TestClient
from rrflow.main import app
from rrflow.config import get_settings

import tests.utils as testing_utils

app_settings = get_settings()

@pytest.fixture(name="client")
def client_fixture():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="function", name="session")
def mongo_fixture(request):
    mongoengine.connect("mongoenginetest", host="mongomock://localhost")
    client = mongoengine.get_connection()
    yield client
    client.drop_database(app_settings.DBNAME)
    client.close()

@pytest.fixture(scope="function", name="db")
def init_database(session):

    # creates a team consisting of 4 unique people, 1 leader, 3 members
    # testing_utils.create_team(session)

    # creates a solver
    # testing_utils.create_solver(session)

    # creates an engine sim. Meta-deta only
    # testing_utils.create_engine_sim(session)

    # creates a program with 4 flow_items embedded within it
    program = testing_utils.create_program(session)