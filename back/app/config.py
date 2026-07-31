import os
from dotenv import load_dotenv

APP_ENV = os.getenv("APP_ENV", "local")
load_dotenv(f".env.{APP_ENV}")

AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")