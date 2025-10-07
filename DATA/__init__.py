import json
import os

BASE_DIR = os.path.dirname(__file__)


BOT_FILE = os.path.join(BASE_DIR, "bot.json")
CLASS_FILE = os.path.join(BASE_DIR,"class.json")
TEST_FILE = os.path.join(BASE_DIR,"test.json")


with open(BOT_FILE, "r", encoding="utf-8") as f:
    MESSAGES = json.load(f)

with open(CLASS_FILE, "r", encoding="utf-8") as f:
    CLASS = json.load(f)
    
with open(CLASS_FILE, "r", encoding="utf-8") as f:
    TEST = json.load(f)


    