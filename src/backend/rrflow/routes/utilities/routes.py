from rrflow.routes.flow_items import crud
from rrflow.logger import create_logger
from rrflow.config import get_settings
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Path, Header
from mongoengine import OperationError
import logging
import rrflow.schemas as schemas
import rrflow.database as database

app_settings = get_settings()

logger = create_logger(__name__)

router = APIRouter()

# Since  FlowItem has no name, use database id to delete item
@router.delete("/")
def clear_database():  # pragma: no cover
    try:
        database.drop_all()
        return {"code": "success", "message": "Database cleared"}
    except OperationError:
        logger.error("Database not cleared")
        return {
            "code": "error",
            "message": "Database not cleared",
        }
