#-----------------------------------------------------------------------
#                           imoport Statements
#-----------------------------------------------------------------------
from fastapi import APIRouter,HTTPException,Depends,Body
from auth.route import authenticate
from chat.chat_query import answer_query,quiz_query
from pydantic import BaseModel
from typing import List,Optional
import datetime
from config.db import chat_history_collection, quizzes_collection, quiz_history
from bson.objectid import ObjectId

#-----------------------------------------------------------------------
#                           imoport Statements
#-----------------------------------------------------------------------

router = APIRouter()

# Quiz Model using Pydantic
class QuizRequest(BaseModel):
    topic : str 
    num_questions : Optional[int] = 5

class QuizAnswerRequest(BaseModel):
    quiz_id : str 
    answers : list[str]

@router.post("/chat")
async def chat(user=Depends(authenticate) , query:str = Body(... , embed=True)):
    """
        Handle a student's chat request by validating access, generating an AI response,
        and storing the conversation in the chat history.
        Args:
            user (dict): Authenticated user details.
            query (str): Question asked by the student.
        Returns:
            dict: A dictionary containing the generated answer and its sources.
    """
    # Validate if the user is student or not
    if user['role'] != "Student":
        raise HTTPException(status_code=403 , detail="Only student can ask question")
    
    response = await answer_query(
        query, user['role'],user['grade']
    )

    chat_history_collection.insert_one({
        "user_id" : user['user_id'],
        "timestamp" : datetime.datetime.utcnow(),
        "query" : query ,
        "response" : response['answer'],
        "sources" : response['sources']
    })

    return response


@router.post("/quiz")
async def quiz(request : QuizRequest , user=Depends(authenticate)):
    """
        Handle a student's quiz generation request, create a quiz based on the given
        topic, store the generated quiz in the database, and return the quiz along
        with its sources and quiz ID.
        Args:
            request (QuizRequest): Quiz generation request containing the topic and
                number of questions.
            user (dict): Authenticated user details.
        Returns:
            dict: A dictionary containing the generated quiz, its sources, and the
            generated quiz ID.
    """
    # Validate if the user is student or not
    if user['role'] != "Student":
        raise HTTPException(status_code=403 , detail="Only student can generate quizes")
    
    # Getting response from the quiz_query
    response = await quiz_query(
        request.topic , 
        user["role"],
        user["grade"],
        request.num_questions
    )

    # Generating quiz doc to push in the db
    quiz_doc = {
        "user_id" : user['user_id'],
        "timestamp" : datetime.datetime.utcnow(),
        "topic" : request.topic,
        "quiz_data" : response['quiz'],
        "sources" : response['sources']
    }

    # Pushing the doc in db
    result = quizzes_collection.insert_one(quiz_doc)

    # Return quiz sources and quiz id to user 
    return {
        "quiz" : response['quiz'],
        "sources" : response['sources'],
        "quiz_id" : str(result.inserted_id)
    }


@router.post("/quiz/check")
async def chec_quiz_answers(request : QuizAnswerRequest , user=Depends(authenticate)):
    """
        Check a student's quiz answers, calculate the score, save the quiz result
        in the database, and return the score with answer details.
        Args:
            request (QuizAnswerRequest): Quiz answer submission containing the quiz
                ID and selected answers.
            user (dict): Authenticated user details.
        Returns:
            dict: A dictionary containing the quiz score, total questions, answer
            results, and a completion message.
    """
    # Find the quiz id
    quiz_doc = quizzes_collection.find_one(
        {"_id" : ObjectId(request.quiz_id)}
    )

    # What if quiz not found
    if not quiz_doc:
        raise HTTPException(status_code=404 , detail="Quiz not found")
    
    # Check user id with quiz generated user id(by which user quiz generated)
    if quiz_doc['user_id'] != user['user_id']:
        raise HTTPException(status_code=403 , detail="UnAuthorize access")
    
    # Finding the answer
    correct_answers = []
    for line in quiz_doc['quiz_data'].split("\n"):
        if line.startswith("Correct Answer:"):
            correct_answers.append(line.split(":")[1].strip()[0])

    # Validate answers
    if len(request.answers) != len(correct_answers):
        raise HTTPException(status_code=400 , detail="Answer count mismatch")
    
    score = 0
    results = []

    for i,ans in enumerate(request.answers):
        is_correct = ans.strip().upper() == correct_answers[i]
        if is_correct:
            score +=1 

        results.append({
            "question_number" : i+1 ,
            "user_answer" : ans,
            "correct_answer" : correct_answers[i],
            "is_correct" : is_correct
        })

    quiz_history.insert_one({
        "user_id" : user['user_id'],
        "quiz_id" : request.quiz_id,
        "timestamp" : datetime.datetime.utcnow(),
        "topic" : quiz_doc['topic'],
        "score" : score ,
        "total" : len(correct_answers),
        "results" : results ,
        "quiz_content" : quiz_doc['quiz_data']
    })

    return {
        "message" : f"Quiz Completed, You scored : {score}/{len(correct_answers)}",
        "score" : score,
        "total" : len(correct_answers),
        "results" : results
    }


@router.get("/quiz/history")
async def get_quiz_history(user=Depends(authenticate)):
    """
    
    """
    # check the role of use is student or not
    if user['role'] != "Student":
        raise HTTPException(status_code=403 , detail="Only student can view the history")
    
    # fetch all the quiz history of particular user in reverse 
    cursor = quiz_history.find({"user_id" : user['user_id']}).sort("timestamp" , -1)

    history = []
    for doc in cursor:
        doc['id'] = str(doc.pop("_id"))
        doc['quiz_id'] = str(doc['quiz_id'])
        doc.pop("user_id" , None)
        history.append(doc)

    return {
        "message" : f"Found {len(history)} attempts",
        "history" : history
    }