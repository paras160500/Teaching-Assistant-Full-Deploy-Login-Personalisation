#-----------------------------------------------------------------------
#                           Import Statements
#-----------------------------------------------------------------------
from fastapi import FastAPI
from auth.route import router as auth_router

#-----------------------------------------------------------------------
#                           Logic Statements
#-----------------------------------------------------------------------
app = FastAPI()
app.include_router(auth_router)

@app.get("/")
def home():
    return {"message" : "Welcome to the user Management API"}