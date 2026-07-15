#-----------------------------------------------------------------------
#                           Import Statements
#-----------------------------------------------------------------------

import os 
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()


#-----------------------------------------------------------------------
#                           Logic Statements
#-----------------------------------------------------------------------


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "test_db")

client=MongoClient(MONGO_URI)
db=client[DB_NAME]

# User collection
users_collection = db["users"]
# Document collection
chunk_collection = db['text']
# Chat collection
chat_history_collection = db['chat_history']
# Quiz collection
quizzes_collection = db['quizzes']
#Quiz history
quiz_history = db['history']