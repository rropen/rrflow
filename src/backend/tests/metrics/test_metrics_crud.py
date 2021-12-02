import pytest
from datetime import datetime, timedelta
import rrflow.documents as documents
import rrflow.routes.metrics.crud as crud
import tests.utils as testing_utils

def test_metric_velocity(session, db, mocker):
    program = documents.Program.objects.first()
    duration = timedelta(days=7)
    period = timedelta(days=1)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))

    # Test Velocity
    response = crud.flow_master(program, period, duration, "velocity")
    
    assert len(response["buckets"]) == 7
    assert response["metric"] == "velocity"
    assert response["buckets"][0]["feature"] == 0
    assert response["buckets"][4]["feature"] == 1
    assert response["buckets"][5]["feature"] == 1
    assert response["buckets"][0]["defect"] == 0
    assert response["buckets"][5]["defect"] == 1
    assert response["buckets"][5]["debt"] == 1
    assert response["buckets"][0]["risk"] == 0

    
    duration = timedelta(days=31)
    period = timedelta(days=7)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))
    response = crud.flow_master(program, period, duration, "velocity")
    assert len(response["buckets"]) == 5
    assert response["metric"] == "velocity"
    assert response["buckets"][0]["feature"] == 0
    assert response["buckets"][4]["feature"] == 2
    assert response["buckets"][4]["defect"] == 1
    assert response["buckets"][4]["debt"] == 1
    assert response["buckets"][4]["risk"] == 0
    
    duration = timedelta(days=31)
    period = timedelta(days=31)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))
    response = crud.flow_master(program, period, duration, "velocity")
    assert len(response["buckets"]) == 1
    
    duration = timedelta(days=365)
    period = timedelta(days=31)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))
    response = crud.flow_master(program, period, duration, "velocity")
    assert len(response["buckets"]) == 12
    assert response["buckets"][0]["feature"] == 0
    assert response["buckets"][11]["feature"] == 2
    assert response["buckets"][11]["defect"] == 1
    assert response["buckets"][11]["debt"] == 1
    assert response["buckets"][11]["risk"] == 0

def test_metric_time(session, db, mocker):
    program = documents.Program.objects.first()
    duration = timedelta(days=7)
    period = timedelta(days=1)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))

    response = crud.flow_master(program, period, duration, "time")
    assert response["metric"] == "time"
    assert response["buckets"][0]["feature"] == 0
    assert response["buckets"][4]["feature"] == 259200
    assert response["buckets"][5]["feature"] == 432000
    assert response["buckets"][0]["defect"] == 0
    assert response["buckets"][5]["defect"] == 432000
    assert response["buckets"][5]["debt"] == 432000
    assert response["buckets"][3]["risk"] == 0
    
    duration = timedelta(days=31)
    period = timedelta(days=7)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))

    response = crud.flow_master(program, period, duration, "time")
    assert response["metric"] == "time"
    assert response["buckets"][2]["debt"] == 0
    assert response["buckets"][4]["feature"] == 345600
    assert response["buckets"][4]["defect"] == 432000
    assert response["buckets"][4]["debt"] == 432000
    assert response["buckets"][4]["risk"] == 0


def test_metric_efficiency(session, db, mocker):
    program = documents.Program.objects.first()
    duration = timedelta(days=7)
    period = timedelta(days=1)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))

    response = crud.flow_master(program, period, duration, "efficiency")
    assert response["metric"] == "efficiency"
    assert response["buckets"][0]["feature"] == 0
    assert response["buckets"][4]["feature"] == 0.5
    assert response["buckets"][5]["feature"] == 0.2
    assert response["buckets"][0]["defect"] == 0
    assert response["buckets"][5]["defect"] == 0.1
    assert response["buckets"][5]["debt"] == 0.05
    assert response["buckets"][3]["risk"] == 0
    
    duration = timedelta(days=31)
    period = timedelta(days=7)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))

    response = crud.flow_master(program, period, duration, "efficiency")
    assert response["metric"] == "efficiency"
    assert response["buckets"][2]["debt"] == 0
    assert response["buckets"][4]["feature"] == 0.35
    assert response["buckets"][4]["defect"] == 0.1
    assert response["buckets"][4]["debt"] == 0.05
    assert response["buckets"][4]["risk"] == 0
    
def test_metric_load(session, db, mocker):
    program = documents.Program.objects.first()
    duration = timedelta(days=7)
    period = timedelta(days=1)
    
    response = crud.flow_load(program)
    assert response["metric"] == "load"
    assert response["currentLoad"]["feature"] == 1
    assert response["currentLoad"]["defect"] == 1
    assert response["currentLoad"]["debt"] == 1
    assert response["currentLoad"]["risk"] == 1
    

def test_metric_distribution(session, db, mocker):
    program = documents.Program.objects.first()
    duration = timedelta(days=7)
    period = timedelta(days=1)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))

    response = crud.flow_master(program, period, duration, "distribution")
    assert response["metric"] == "distribution"
    assert response["buckets"][0]["feature"] == 0
    assert response["buckets"][4]["feature"] == 1
    assert response["buckets"][5]["feature"] == 1/3
    assert response["buckets"][0]["defect"] == 0
    assert response["buckets"][5]["defect"] == 1/3
    assert response["buckets"][5]["debt"] == 1/3
    assert response["buckets"][3]["risk"] == 0
    
    duration = timedelta(days=31)
    period = timedelta(days=7)
    mocker.patch('rrflow.routes.metrics.crud.duration_filter', return_value=testing_utils.mock_duration_filter(program, duration))
    mocker.patch('rrflow.routes.metrics.crud.bucket_closed_by_period', return_value=testing_utils.mock_bucket_closed_by_period(program, period, duration))

    response = crud.flow_master(program, period, duration, "distribution")
    assert response["metric"] == "distribution"
    assert response["buckets"][2]["debt"] == 0
    assert response["buckets"][4]["feature"] == 0.5
    assert response["buckets"][4]["defect"] == 0.25
    assert response["buckets"][4]["debt"] == 0.25
    assert response["buckets"][4]["risk"] == 0 