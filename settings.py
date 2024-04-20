import os
from dotenv import load_dotenv as ld

ld()

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
