import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env.local"))

DEFAULT_MAX_QUERY_LIMIT = 50
ABSOLUTE_MAX_QUERY_LIMIT = 100