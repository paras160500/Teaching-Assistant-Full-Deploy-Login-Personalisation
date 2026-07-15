#-----------------------------------------------------------------------
#                           Import Statements
#-----------------------------------------------------------------------
from fastapi import FastAPI
from auth.route import router as auth_router
from docs.route import router as doc_router
from chat.route import router as chat_router
from pymongo import MongoClient
import os


#-----------------------------------------------------------------------
#                           Logic Statements
#-----------------------------------------------------------------------
app = FastAPI()
app.include_router(auth_router)
app.include_router(doc_router)
app.include_router(chat_router)

@app.get("/")
def home():
    return {"message" : "Welcome to the user Management API"}

@app.get("/mongo-test")
def mongo_test():
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        client.admin.command("ping")
        return {"status": "Connected to MongoDB"}
    except Exception as e:
        return {"status": "Failed", "error": str(e)}