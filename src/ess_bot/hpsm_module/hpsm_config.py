from os import environ

HPSM_PAGE = environ["HPSM_PAGE"]
HPSM_EXIT_PAGE = environ["HPSM_EXIT_PAGE"]
HPSM_USER = environ["HPSM_USER"]
HPSM_PASS = environ["HPSM_PASS"]
HPSM_SCREENSHOT_USER = environ["HPSM_SCREENSHOT_USER"]
HPSM_SCREENSHOT_PASSWORD = environ["HPSM_SCREENSHOT_PASSWORD"]
HPSM_CHECK_INTERVAL_SECONDS = int(environ["HPSM_CHECK_INTERVAL_SECONDS"])
ESS_CHAT_ID = environ["ESS_CHAT_ID"]
HPSM_WAIT_FRAME_TRIES = int(environ['HPSM_WAIT_FRAME_TRIES'])