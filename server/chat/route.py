#-----------------------------------------------------------------------
#                           imoport Statements
#-----------------------------------------------------------------------
from fastapi import APIRouter,HTTPException,Depends,Body
from auth.route import authenticate
from chat.chat_query import answer_query
from pydantic import BaseModel
from typing import List,Optional
import datetime
from config.db import chat_history_collection
from bson.objectid import ObjectId

#-----------------------------------------------------------------------
#                           imoport Statements
#-----------------------------------------------------------------------

router = APIRouter()

@router.post("/chat")
async def chat(user=Depends(authenticate) , query:str = Body(... , embed=True)):
    """
    
    """
    # Validate if the user is student or not
    if user['role'] != "Student":
        raise HTTPException(status_code=403 , detail="Only student can ask question")
    
    response = await answer_query(
        query, user['role'],user['grade']
    )
    print("--"*40)
    print(user)
    print("*"*50)
    print(response)

    chat_history_collection.insert_one({
        "user_id" : user['user_id'],
        "timestamp" : datetime.datetime.utcnow(),
        "query" : query ,
        "response" : response['answer'],
        "sources" : response['sources']
    })

    return response