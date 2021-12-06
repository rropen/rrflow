"""
CRUD for Flow Metrics
"""
from typing import List

from rrflow.documents import FlowItemCategory
from mongoengine.queryset.transform import update
from rrflow.utils import program_selector, unix_time_seconds
from fastapi import HTTPException
import rrflow.schemas as schemas
import rrflow.documents as documents
import rrflow.routes.flow_items.crud as flow_item_crud
from rrflow.utility_classes import OID
from datetime import datetime, timedelta
import math

# TODO: Possible to round numbers of output before sending to frontend


def duration_filter(program, duration, only_closed=True):
    all_flow_items = program.flow_items
    filtered_flow_items = []
    for flow_item in all_flow_items:
        if (flow_item.end_time is None) and (
            only_closed is False
        ):  # if the flow item is still open, it is still within the duration
            filtered_flow_items.append(flow_item)
        elif (flow_item.end_time is not None) and (
            flow_item.end_time >= datetime.now() - duration
        ):
            filtered_flow_items.append(flow_item)

    return filtered_flow_items


def bucket_closed_by_period(
    flow_items: List[documents.FlowItem], period: timedelta, duration: timedelta
) -> List[dict]:  # {bucket_start: int, flow_items: List}
    """Only works for list of closed flow_items"""

    if flow_items == []:
        # logger.debug("flow_items passed to function is an empty list")
        return []

    if None in [i.end_time for i in flow_items]:
        raise AssertionError(
            "Function 'bucket_closed_by_period' was passed an open flow_item"
        )

    buckets = []
    total_buckets = math.ceil(int(duration.days) / int(period.days))
    initial_date = datetime.now() - total_buckets * period
    for iter in range(0, total_buckets):
        range_start = initial_date + period * iter
        range_end = initial_date + period * (iter + 1)
        bucket_dict = {"bucket_start": unix_time_seconds(range_start), "flow_items": []}

        for item in flow_items:
            if item.end_time >= range_start and item.end_time < range_end:
                bucket_dict["flow_items"].append(item)

        buckets.append(bucket_dict)

    return buckets


def flow_load(program: documents.Program):
    open_items = [item for item in program.flow_items if item.end_time is None]

    response = {}
    categories = [item.category for item in open_items]
    for category in FlowItemCategory:
        response[category] = categories.count(category)

    response = {
        "metric": "load",
        "units": "number of flow items",
        "currentLoad": response,
    }
    return response


def flow_master(
    program: documents.Program,
    period: timedelta,
    duration: timedelta,
    metric_select: str,
):

    in_duration = duration_filter(program, duration)
    buckets = bucket_closed_by_period(in_duration, period, duration)
    if metric_select.lower() == "velocity":
        unit_type = "number of flow items"
    elif metric_select.lower() == "time":
        unit_type = "seconds"
    elif metric_select.lower() == "efficiency":
        unit_type = "percentage of flow time spent in active state"
    elif metric_select.lower() == "distribution":
        unit_type = "percentage of flow items in bucket"

    for bucket in buckets:
        flow_items = bucket.pop("flow_items")
        for category in FlowItemCategory:
            items_in_category = [
                item for item in flow_items if item.category == category
            ]
            if len(items_in_category) == 0:
                bucket[category] = 0
            else:
                if metric_select.lower() == "velocity":
                    bucket[category] = len(items_in_category)
                elif metric_select.lower() == "time":
                    bucket[category] = sum(
                        [i.duration_open for i in items_in_category]
                    ) / len(items_in_category)
                elif metric_select.lower() == "efficiency":
                    # BUG: Check if duration_open is zero before dividing (might be just a swagger issue since it sets start/end_time to be identical)
                    bucket[category] = sum(
                        [(i.sum_active / i.duration_open) for i in items_in_category]
                    ) / len(items_in_category)
                elif metric_select.lower() == "distribution":
                    bucket[category] = len(items_in_category) / len(flow_items)

    response = {"metric": metric_select, "units": unit_type, "buckets": buckets}
    return response
