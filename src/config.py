# ponytail: stub for Task 1
import os
from dotenv import load_dotenv

load_dotenv()

MASTER_KEY = os.getenv("MASTER_KEY")
PORT = int(os.getenv("PORT", 8000))
