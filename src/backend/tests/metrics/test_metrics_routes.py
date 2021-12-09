import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
import rrflow.documents as documents
import tests.utils as testing_utils


def test_get_velocity_route(client, session, db, mocker):
    response = client.get(
        "/metrics/velocity/", params={"program_name": "test program 1"}
    )
    assert response.status_code == 200
    assert (
        len(response.json()["buckets"]) == 13
    )  # due to month being = 4 weeks instead of true months

    response = client.get(
        "/metrics/velocity/",
        params={"program_name": "test program 1", "period": "Year"},
    )
    assert response.status_code == 200
    assert len(response.json()["buckets"]) == 1

    response = client.get(
        "/metrics/velocity/",
        params={"program_name": "test program 1", "period": "Week"},
    )
    assert response.status_code == 200
    assert len(response.json()["buckets"]) == 52

    response = client.get(
        "/metrics/velocity/",
        params={
            "program_name": "test program 1",
            "period": "Month",
            "duration": "Year",
        },
    )
    assert response.status_code == 200
    assert len(response.json()["buckets"]) == 13

    response = client.get(
        "/metrics/velocity/",
        params={
            "program_name": "test program 1",
            "period": "jibberish",
            "duration": "Year",
        },
    )
    assert response.status_code == 422

    response = client.get(
        "/metrics/velocity/",
        params={"program_name": "jibberish", "period": "Month", "duration": "Year"},
    )
    assert response.status_code == 404


def test_get_time_route(client, session, db, mocker):
    response = client.get(
        "/metrics/time/",
        params={
            "program_name": "test program 1",
            "period": "Month",
            "duration": "Year",
        },
    )
    assert response.status_code == 200
    assert len(response.json()["buckets"]) == 13


def test_get_efficiency_route(client, session, db, mocker):
    response = client.get(
        "/metrics/efficiency/",
        params={
            "program_name": "test program 1",
            "period": "Month",
            "duration": "Year",
        },
    )
    assert response.status_code == 200
    assert len(response.json()["buckets"]) == 13


def test_get_load_route(client, session, db, mocker):
    response = client.get("/metrics/load", params={"program_name": "test program 1"})
    assert response.status_code == 200
    assert len(response.json()["currentLoad"]) == 4


def test_get_distribution_route(client, session, db, mocker):
    response = client.get(
        "/metrics/distribution/",
        params={
            "program_name": "test program 1",
            "period": "Week",
            "duration": "Month",
        },
    )
    assert response.status_code == 200
    assert len(response.json()["buckets"]) == 4
    # Data returns are tested in CRUD tests
