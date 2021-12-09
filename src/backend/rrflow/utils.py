import hmac
import logging
import random
import string
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional

from fastapi import Depends, HTTPException
from mongoengine.queryset.visitor import Q
from opencensus.ext.azure.log_exporter import AzureLogHandler
from passlib.context import CryptContext

from rrflow import documents
from rrflow.config import get_settings
from rrflow.logger import create_logger


logger = create_logger(__name__)

app_settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_program_auth_token():
    # creates 20 character string of random letters, numbers, symbols.
    logger.debug("A new program auth token has been created")
    low_letters = string.ascii_lowercase
    up_letters = string.ascii_uppercase
    digits = string.digits
    symbols = [
        "!",
        "#",
        "$",
        "%",
        "&",
        "*",
        "+",
        ":",
        ";",
        "?",
        "<",
        ">",
        "=",
        "_",
        "~",
    ]

    rand_arr = []
    for i in range(20):
        choice = random.randrange(4)
        if choice == 0:
            rand_char = random.choice(low_letters)
        elif choice == 1:
            rand_char = random.choice(up_letters)
        elif choice == 2:
            rand_char = random.choice(digits)
        elif choice == 3:
            rand_char = random.choice(symbols)

        rand_arr.append(rand_char)

    return "".join(rand_arr)


def hash_program_auth_token(token: str):
    return pwd_context.hash(token)


def calc_signature(payload):
    digest = hmac.new(
        key=app_settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload,
        digestmod="sha256",
    ).hexdigest()
    return f"sha256={digest}"


def validate_signature(signature, raw):
    if signature != calc_signature(raw):
        logger.warning(
            "Incorrect GitHub credentials included with incoming payload, access was denied"
        )
        raise HTTPException(status_code=401, detail="Github Credentials Incorrect")
    program_auth_token = app_settings.GITHUB_WEBHOOK_SECRET
    return program_auth_token


def verify_program_auth_token(attempt: str, target: str):
    if pwd_context.verify(attempt, target):
        return True
    elif pwd_context.verify(
        attempt, hash_program_auth_token(app_settings.GITHUB_WEBHOOK_SECRET)
    ):
        return True
    else:
        return False


def verify_admin_key(attempt):
    return attempt == app_settings.ADMIN_KEY


def verify_api_auth_token(attempt):
    return pwd_context.verify(attempt, pwd_context.hash(app_settings.API_AUTH_TOKEN))


epoch = datetime.utcfromtimestamp(0)


def unix_time_seconds(date):
    dt = datetime.combine(date, datetime.min.time())
    return (dt - epoch).total_seconds()


def program_selector(program_name=None, program_id=None):
    if program_name and not program_id:
        program = documents.Program.objects(name=program_name).first()
        if not program:
            logger.debug("No program found with the specified name")
            raise HTTPException(
                status_code=404,
                detail=f"No program found with the specified name: {program_name}",
            )
    elif program_id and not program_name:
        program = documents.Program.objects(id=program_id).first()
        if not program:
            logger.debug("No program with the specified id")
            raise HTTPException(
                status_code=404,
                detail=f"No program found with the specified id: {program_id}",
            )
    elif program_id and program_name:
        program = documents.Program.objects(
            Q(id=program_id) & Q(name=program_name)
        ).first()
        if not program:
            logger.debug(
                "Either program_id and program_name do not match or no matching program"
            )
            raise HTTPException(
                status_code=404,
                detail="Either the program_name and program_id do not match, or there is not a program with the specified details. Try passing just one of the parameters instead of both.",
            )
    else:
        raise HTTPException(
            status_code=404, detail="No program selection criterion passed"
        )

    return program


def convert_enum_to_timedelta(option: str):  # pragma: no cover
    if option == "Day":
        delta = timedelta(days=1)
    elif option == "Week":
        delta = timedelta(weeks=1)
    elif option == "Month":
        delta = timedelta(weeks=4)
    elif option == "Year":
        delta = timedelta(weeks=52)
    else:
        delta = None

    return delta
