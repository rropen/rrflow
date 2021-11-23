"""
CRUD for Flow Metrics
"""
from typing import List

from mongoengine.queryset.transform import update
from rrflow.utils import program_selector
from fastapi import HTTPException
import rrflow.schemas as schemas
import rrflow.documents as documents
import rrflow.routes.flow_items.crud as flow_item_crud
from rrflow.utility_classes import OID


def flow_velocity():
    pass

def flow_time():
    pass

def flow_efficiency():
    pass

def flow_load():
    pass

def flow_distribution():
    pass