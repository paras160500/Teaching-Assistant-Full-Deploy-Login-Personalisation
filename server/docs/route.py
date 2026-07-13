#-----------------------------------------------------------------------
#                           Import Statements
#-----------------------------------------------------------------------

from fastapi import APIRouter, UploadFile , File, HTTPException,Form 
from .vectorstore import load_vectorstore
import uuid

#-----------------------------------------------------------------------
#                           main Logic Statements
#-----------------------------------------------------------------------

router = APIRouter()

@router.post("/upload_docs/")
async def upload_docs(file : UploadFile = File(...) , grade : int = Form(...)):
    """
        Uploads a PDF document, processes its contents into text chunks
        and upload into
        - MongoDB (full text chunks)
        - Pinecone (embeddings only)
        Access isset to 'Public' by default 

        Args:
            file (UploadFile): The PDF file uploaded by the user.
            grade (int): The grade/category assigned to the uploaded document.
        Returns:
            dict: A response containing the upload and processing status.
    """

    # Basic validation that doc is pdf or not
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400 , detail="Internal Server Error:Only PDFs are supported")
    
    # Init some variables
    doc_id = str(uuid.uuid4())
    ACCESS_ROLE = "Public"

    # Call vectorstore
    try:
        await load_vectorstore(upload_files=[file] , role = ACCESS_ROLE , doc_id=doc_id , grade=grade)
    except Exception as e:
        print("Error during document upload: " , str(e))
        raise HTTPException(
            status_code=500 , detail="Failed to process and index the document"
        )
    
    return {
        "message" : f"{file.filename} uploaded and indexed successfully.",
        "doc_id" : doc_id,
        "grade" : grade,
        "access" : ACCESS_ROLE
    }