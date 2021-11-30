from rrflow import utils
from enum import Enum
import fastapi
from fastapi import APIRouter, Depends, Query, Body
from fastapi.params import Depends
from typing import List
import rrflow.schemas as schemas
from rrflow.schemas import CoreMetricDisplay, LoadMetricDisplay 
import rrflow.documents as documents
import rrflow.routes.programs.crud as program_crud
import rrflow.routes.flow_items.crud as item_crud
import rrflow.routes.metrics.crud as metric_crud
from rrflow.utility_classes import OID

router = fastapi.APIRouter()

# class Metric_Params:
    # """
    # Custom parameter class for GET flow metric routes.
    # This format enables a custom description field for each parameter that will display
    # in the backend swagger docs.
    # """
    # class Metric_Enum(str, Enum):
        # VELOCITY = "Velocity"
        # TIME = "Time"
        # EFFICIENCY = "Efficiency"
        # DISTRIBUTION = "Distribution"

    # def __init__(
        # self,
        # metric: Metric_Enum = Query(
            # "Velocity",
            # description="This parameter selects the metric data to return.",
        # ),
    # ):

        # self.metric = metric
class Program_Params:
    """
    Custom parameter class for GET flow metric routes.
    This format enables a custom description field for each parameter that will display
    in the backend swagger docs.
    """
    def __init__(
        self,
        program_name: str = Query(
            None,
            description="This parameter selects the program by name.",
        ),
        program_id: OID= Query(
            None,
            description="This parameter selects the program by ID.",
        ),
    ):

        self.program = utils.program_selector(program_name, program_id)

class Time_Params:
    """
    Custom parameter class for GET flow metric routes.
    period = month & duration = year by default.
    This format enables a custom description field for each parameter that will display
    in the backend swagger docs.
    """

    class Period_Enum(str, Enum):
        DAY = "Day"
        WEEK = "Week"
        MONTH = "Month"
        YEAR = "Year"

    class Duration_Enum(str, Enum):
        WEEK = "Week"
        MONTH = "Month"
        YEAR = "Year"

    def __init__(
        self,
        period: Period_Enum = Query(
            "Month",
            description="This parameter sets the granularity for how many flow items get placed together.",
        ),
        duration: Duration_Enum = Query(
            "Year",
            description="This parameter sets the amount of time in the past to present the metrics for",
        ),
    ):
        # Convert query params into timedeltas to be used in CRUD functions
        period = utils.convert_enum_to_timedelta(period)
        duration = utils.convert_enum_to_timedelta(duration)

        if period > duration:
            raise AssertionError("Period cannot be greater than total duration")

        self.period = period
        self.duration = duration
        
# @router.get("/")
# def flow_metrics(t_params: Time_Params = Depends(), p_params: Program_Params = Depends(), m_params: Metric_Params = Depends()):
    # """
    # ## Get Flow Metrics

    # ---
    # Query Parameters:
    # """
    # response = metric_crud.flow_master(p_params.program, t_params.period, t_params.duration, m_params.metric)
    # return response


@router.get("/velocity", response_model=CoreMetricDisplay)
def flow_velocity(t_params: Time_Params = Depends(), p_params: Program_Params = Depends()):
    """
    ## Get Flow Velocity

    ---
    Query Parameters:
    """
    # response = metric_crud.flow_velocity(p_params.program, t_params.period, t_params.duration)
    response = metric_crud.flow_master(p_params.program, t_params.period, t_params.duration, metric_select="velocity")
    return response

@router.get("/time", response_model=CoreMetricDisplay)
def flow_time(t_params: Time_Params = Depends(), p_params: Program_Params= Depends()):
    """
    ## Get Flow Time

    ---
    Query Parameters:
    """
    # response = metric_crud.flow_time(p_params.program, t_params.period, t_params.duration)
    response = metric_crud.flow_master(p_params.program, t_params.period, t_params.duration, metric_select="time")
    return response

@router.get("/efficiency", response_model=CoreMetricDisplay)
def flow_efficiency(t_params: Time_Params = Depends(), p_params: Program_Params= Depends()):
    """
    ## Gets Flow Efficiency

    ---
    Query Parameters:
    """
    response = metric_crud.flow_efficiency(p_params.program, t_params.period, t_params.duration, metric_select="efficiency")
    return response

@router.get("/load", response_model=LoadMetricDisplay)
def flow_load(p_params: Program_Params= Depends()):
    """
    ## Get Flow Load

    ---
    Query Parameters:
    """
    response = metric_crud.flow_load(p_params.program)
    return response

@router.get("/distribution", response_model=CoreMetricDisplay)
def flow_distribution(t_params: Time_Params = Depends(), p_params: Program_Params= Depends()):
    """
    ## Get Flow Distribution

    ---
    Query Parameters:
    """
    response = metric_crud.flow_distribution(p_params.program, t_params.period, t_params.duration, metric_select="distribution")
    return response