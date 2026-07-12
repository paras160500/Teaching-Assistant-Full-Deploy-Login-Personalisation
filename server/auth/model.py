#-----------------------------------------------------------------------
#                           Import Statements
#-----------------------------------------------------------------------

from pydantic import BaseModel


#-----------------------------------------------------------------------
#                           Pydantic Model Defination
#-----------------------------------------------------------------------

# Student model
class StudentUser(BaseModel):
    #id:int 
    fullname : str 
    email : str
    username : str 
    password : str 
    grade : int 
    school : str 

# Teacher Model
class TeacherUser(BaseModel):
    #id : int 
    fullname : str 
    email : str 
    username : str 
    password : str 
    school : str