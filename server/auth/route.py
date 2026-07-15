#-----------------------------------------------------------------------
#                           Import Statements
#-----------------------------------------------------------------------
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic , HTTPBasicCredentials
from .model import StudentUser, TeacherUser
from config.db import users_collection
from .hash_utils import hash_password,verify_password

router = APIRouter()
security = HTTPBasic()


#-----------------------------------------------------------------------
#                           Logic Statements
#-----------------------------------------------------------------------

def authenticate(credentials : HTTPBasicCredentials = Depends(security)):
    """
        Authenticate a user using simple HTTP Basic Credentials 
        ARgs:
            credentials : HTTPBAsicCredentials for user inorder to make login easy
    """
    user_record = users_collection.find_one({"username" : credentials.username})
    if not user_record:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )
    
    if not verify_password(credentials.password,user_record["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    return {
        "username" : user_record['username'],
        "fullname" : user_record['fullname'],
        "email" : user_record['email'],
        "role" : user_record['role'],
        "grade" : user_record['grade'],
        "user_id" : str(user_record['_id'])
    }

# Route Createion for student signup
@router.post("/signup/student")
def signup_student(req : StudentUser):
    """
        Handles a student signup request
        Args:
            req(StudentUser) : Pydantic class model
    """
    # First check if the user name available or not 
    if users_collection.find_one({"username" : req.username}):
        raise HTTPException(status_code=400 , detail="Username already exists")
    
    # Hash the password before storing
    hashed_password = hash_password(req.password)
    users_collection.insert_one({
        "fullname" : req.fullname,
        "email" : req.email,
        "username" : req.username,
        "password" : hashed_password,
        "role" : "Student",
        "grade" : req.grade,
        "school" : req.school
    })

    return {"message" : "Student user created successfully."}

# Route Createion for teacher signup
@router.post("/signup/teacher")
def signup_teacher(req : TeacherUser):
    """
        Handles a teacher signup request
        Args:
            req(StudentUser) : Pydantic class model
    """
    # First check if the user name available or not 
    if users_collection.find_one({"username" : req.username}):
        raise HTTPException(status_code=400 , detail="Username already exists")
    
    hashed_password = hash_password(req.password)
    users_collection.insert_one({
        "fullname" : req.fullname,
        "email" : req.email,
        "username" : req.username,
        "password" : hashed_password,
        "school" : req.school,
        "role" : "Teacher",
    })
    return {"message" : "Teacher user created successfully."}

# Route creation for login
@router.get("/login")
def login(user = Depends(authenticate)):
    """
        Handles the user logic
        Args:
            user(str) : the username in order to check its valid or not 
    """
    return {"message" : f"Welcome, {user['username']}" , "role" : user['role']} 