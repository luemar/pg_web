import os
from datetime import datetime, timedelta

SHARED_FOLDER = "/mnt/pg_web_data"
EXCEL_FILE_PATH = os.path.join(SHARED_FOLDER, "PG_2024.xlsx")

DEBUG_ENABLED = True

SERVER_START_TIME = datetime.now().strftime("%d.%m.%Y")
GROUP_PASSWORD = 'plauschgruppe'
