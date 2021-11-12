import mongoengine
import rrflow.config as config

app_settings = config.get_settings()

alias = app_settings.DBALIAS

mongoengine.connect(
    app_settings.DBNAME, 
    host=app_settings.CONN_STR,
    alias=alias
)

