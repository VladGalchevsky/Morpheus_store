import os

from dotenv import load_dotenv

load_dotenv()

REAL_DATABASE_URL = os.getenv("REAL_DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

SECRET_KEY: str = os.getenv("SECRET_KEY")
ALGORITHM: str = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")