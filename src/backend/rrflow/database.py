import fastapi
import mongoengine
import rrflow.config as config

app_settings = config.get_settings()

# alias = app_settings.DBALIAS
alias = app_settings.DBNAME
print(
    "Connection String: {} to database {}".format(
        app_settings.CONN_STR, app_settings.DBNAME
    )
)


# mongoengine.connect(
#     app_settings.DBNAME,
#     host=app_settings.CONN_STR,
#     alias=alias
# )

# db = mongoengine.connect(
#     app_settings.DBNAME,
#     host=app_settings.CONN_STR,
#     alias=alias
# )
db = mongoengine.connect(app_settings.DBNAME, host=app_settings.CONN_STR, alias=alias)

# TODO: Delete this method before production:
def drop_all():
    if app_settings.ENV != "production":
        db.drop_database(app_settings.DBNAME)
        return
    raise fastapi.HTTPException(
        status_code=405,
        detail="I'm not going to delete a production db, you'll have to do this manually if you really mean it",
    )
