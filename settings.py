import os

from dotenv import load_dotenv

load_dotenv()

REAL_DATABASE_URL = os.getenv("REAL_DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")