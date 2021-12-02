import pytest
import json
import rrflow.documents as documents
import math
from rrflow.utils import unix_time_seconds
from datetime import datetime, timedelta
from typing import List


def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except:
            pass
    return json_dict

initial_program = json.load(open("./testing_files/initial_program.json"))
initial_program_count = len(initial_program)

initial_flow_items = json.load(open("./testing_files/initial_flow_items.json"), object_hook=date_hook)
initial_flow_item_count = len(initial_flow_items)

# def create_team(session):
#     team_lead = documents.Person(**initial_team["team_lead"]).save()
# 
#     team_member_ids = []
#     for person in initial_team["team_members"]:
#         p = documents.Person(**person).save()
#         team_member_ids.append(p.id)
# 
#     team_data = {
#         "team_name": initial_team["team_name"],
#         "team_lead_id": team_lead.id,
#         "team_member_ids": team_member_ids,
#     }
# 
#     documents.Team(**team_data).save()

def create_flow_items(program):
    for flow_item in initial_flow_items:
        flow_item["program_id"] = program.id
        flow_item_doc = documents.FlowItem(**flow_item)
        program.flow_items.append(flow_item_doc)
    program.save()

def create_program(session):
    program = documents.Program(**initial_program).save()
    create_flow_items(program)
    return program

# Date that emulates when the tests are being run to remove moving reference date of datetime.now()
reference_date = datetime(2021, 11, 8, 12, 00, 00, 00)

def mock_duration_filter(program, duration, only_closed=True):
    all_flow_items = program.flow_items
    filtered_flow_items = []
    for flow_item in all_flow_items:
        if (flow_item.end_time == None) and (only_closed == False): # if the flow item is still open, it is still within the duration
            filtered_flow_items.append(flow_item)
        elif (flow_item.end_time != None) and (flow_item.end_time >= reference_date - duration) and (flow_item.end_time <= reference_date):
            filtered_flow_items.append(flow_item)

    return filtered_flow_items


def mock_bucket_closed_by_period(program: documents.Program, period: timedelta, duration: timedelta) -> List[dict]: # {bucket_start: int, flow_items: List}
    """Only works for list of closed flow_items"""

    # Call this here to avoid a messy function call of a mock function as an argument within another mock function
    flow_items = mock_duration_filter(program, duration)
    
    if flow_items == []:
        # logger.debug("flow_items passed to function is an empty list")
        return []
    
    if None in [i.end_time for i in flow_items]:
        raise AssertionError("Function 'bucket_closed_by_period' was passed an open flow_item")
    
    
    buckets = []
    total_buckets = math.ceil(int(duration.total_seconds()/86400) / int(period.total_seconds()/86400))
    initial_date = reference_date - total_buckets*period
    for iter in range(0, total_buckets):
        range_start = initial_date + period*iter
        range_end = initial_date + period*(iter + 1)
        print(f"bucket {iter}: ", f"start_date: {range_start}", f"end_date: {range_end}")
        bucket_dict = {
            "bucket_start": unix_time_seconds(range_start),
            "flow_items": []
        }

        for item in flow_items:
            if item.end_time >= range_start and item.end_time < range_end:
                bucket_dict["flow_items"].append(item)
                
        
        buckets.append(bucket_dict)
    
    print(buckets)
    return buckets