# CD to backend > source env/Scripts/activate > pip install -r requirements.txt  > uvicron main:app --reload
# UI http://127.0.0.1:8000/docs http://127.0.0.1:8000/openapi.json
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from rrflow.routes.flow_items import routes as flow_items
from rrflow.routes.programs import routes as programs
from rrflow.routes.utilities import routes as utilities
# from rrflow.routes.graphql.routes import query
from rrflow.routes import root
from rrflow.logger import create_logger
from .config import get_settings

app_settings = get_settings()

logger = create_logger(__name__)

description = "<h2>Software Factory Flow API</h2><br><blockquote>A custom app built by the Software Factory to serve as a general use API for value stream flow metrics.</blockquote>"
app = FastAPI(
    debug=os.environ.get("DEBUG"),
    title="RRFLOW API",
    description=description,
    version="0.0.1",
)
    # dependencies=[Depends(has_access)],


# This is how you can get access to environment configuration values throughout the application
# Then app_settings.ENV or app_settings.CONN_STR.  See config.py for possible values.
app_settings = get_settings()

# assert app_settings.ENV != "unset"  # mandate ENV value
assert app_settings.ENV in ("test", "local", "development", "production")
assert app_settings.SECRET_KEY != "unset"  # mandate SECRET_KEY value
assert app_settings.ADMIN_KEY != "unset"  # mandate ADMIN_KEY value
assert app_settings.FRONTEND_URL != "unset"  # mandate FRONTEND_URL value
assert app_settings.GITHUB_API_TOKEN != "unset"  # mandate GITHUB_API_TOKEN value
if app_settings.ENV in ["development", "production"]:
    assert app_settings.DBHOST != "unset"  # mandate DBHOST value
    assert app_settings.DBNAME != "unset"  # mandate DBNAME value
    assert app_settings.DBUSER != "unset"  # mandate DBUSER value
    assert app_settings.DBPASS != "unset"  # mandate DBPASS value

# CORS Stuff
origins = [app_settings.FRONTEND_URL]
# print("Configured Origins: {}".format(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include api item submodules below
app.include_router(root.router, prefix="", tags=["root"])
app.include_router(flow_items.router, prefix="/flowItems", tags=["flowItems"])
app.include_router(programs.router, prefix="/programs", tags=["programs"])
app.include_router(utilities.router, prefix="/utilities", tags=["utilities"])
# app.include_router(utilities.router, prefix="/utilities", tags=["utilities"])
# app.mount("/graph", GraphQLApp(query, on_get=make_graphiql_handler()))
