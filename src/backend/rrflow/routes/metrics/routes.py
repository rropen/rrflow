from rrflow import utils
import fastapi
from fastapi import APIRouter, Depends, Query, Body
from fastapi.params import Depends
from typing import List
import rrflow.schemas   as schemas
import rrflow.documents as documents
import rrflow.routes.programs.crud as program_crud
import rrflow.routes.flow_items.crud as item_crud
from rrflow.utility_classes import OID

router = fastapi.APIRouter()

class Time_Params:
    """
    Custom parameter class for GET flow metric routes.
    period = month & duration = year by default.
    This format enables a custom description field for each parameter that will display
    in the backend swagger docs.
    """

    def __init__(
        self,
        period: int = Query(
            "month",
            description="This parameter sets the granularity for how many flow items get placed together.",
        ),
        duration: int = Query(
            "year",
            description="This parameter sets the amount of time in the past to present the metrics for",
        ),
    ):
        self.skip = period
        self.limit = duration

@router.get("/velocity")
def flow_velocity(t_params: Time_Params = Depends()):
    """
    ## Get Flow Velocity

    ---
    Query Parameters:
    """
    return 200

@router.get("/time")
def flow_time(t_params: Time_Params = Depends()):
    """
    ## Get Flow Time

    ---
    Query Parameters:
    """
    return 200

@router.get("/efficiency")
def flow_efficiency(t_params: Time_Params = Depends()):
    """
    ## Gets Flow Efficiency

    ---
    Query Parameters:
    """
    return 200

@router.get("/load")
def flow_load(t_params: Time_Params = Depends()):
    """
    ## Get Flow Load

    ---
    Query Parameters:
    """
    return 200

@router.get("/distribution")
def flow_distribution(t_params: Time_Params = Depends()):
    """
    ## Get Flow Distribution

    ---
    Query Parameters:
    """
    return 200