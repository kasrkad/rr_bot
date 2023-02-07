from os import makedirs
makedirs("logs", exist_ok=True)
makedirs("bot_db", exist_ok=True)

from .sqlite_module.sql_lib import create_tables,load_admin_from_json,load_standard_notify_from_file
create_tables()
load_admin_from_json('./basic_settings/admins.json')
load_standard_notify_from_file('./basic_settings/notifys.json')