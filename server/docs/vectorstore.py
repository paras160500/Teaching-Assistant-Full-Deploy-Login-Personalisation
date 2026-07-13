#-----------------------------------------------------------------------
#                           Import Statements
#-----------------------------------------------------------------------
import os 
import time 
import asyncio
from pathlib import Path 
from dotenv import load_dotenv

from pinecone import Pinecone,ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from config.db import chunk_collection

#-----------------------------------------------------------------------
#                           API KEY Statements
#-----------------------------------------------------------------------

load_dotenv()
OPEN_AI_API = os.getenv("OPEN_AI_API")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

#-----------------------------------------------------------------------
#                           Logical Statements
#-----------------------------------------------------------------------

UPLOAD_DIR = "./upload_docs"
os.makedirs(UPLOAD_DIR , exist_ok= True)

# Pinecone global upsert function
pc = None
index = None 

# Getting pinecone index
def get_pinecone_index():
    """ 
        Creating the pc and index variable for global
        and not to init it again and again through the program
        Returns:
            return index(pc.Index())
    """
    global pc,index
    
    # Check if there is a pinecone index there or not
    if index is None:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
    return index 


# loading vector store
async def load_vectorstore(upload_files , role :str , doc_id : str , grade : int):
    """
        Initialize the vectorstore
        Args:   
            upload_files(files) : The Data we want to upload
            role(str) : Role of the user
            doc_id(str) : id of document
            grade(int) : For which grade this document is for
    """
    # init the embedding model
    embed_model = OpenAIEmbeddings(
            api_key=os.getenv("OPEN_AI_API"),
            model="text-embedding-3-small"
        )
    
    # get pinecone index
    pinecone_index = get_pinecone_index()

    #upload files
    for file in upload_files:

        # 1. Save Raw files
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path , "wb") as f:
            f.write(file.file.read())

        # 2. Parse the file(PDF) text
        loader = PyPDFLoader(str(save_path))
        documents = loader.load()

        # 3. Chunking the text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500 , chunk_overlap = 50)
        chunks = text_splitter.split_documents(documents)

        # 4. Guard condition
        if not chunks:
            print(f"No text extracted from {file.filename} , skipping...")
            continue 

        # 5 dual Storing

        # 5.1 Store in mongodb 
        chunk_docs = [] 
        for i,chunk in enumerate(chunks):
            chunk_docs.append({
                "chunk_id" : f"{doc_id}-{i}",
                "doc_id" : doc_id,
                "text" : chunk.page_content,
                "page" : int(chunk.metadata.get("page" , 0)),
                "source" : file.filename,
                "grade" : grade,
                "role" : role
            })

        if chunk_docs:
            chunk_collection.insert_many(chunk_docs)
            print("MongoDB Uploaded")

        # 5.2 Store in Pinecone
        texts = [chunk.page_content for chunk in chunks]
        embeddings = await asyncio.to_thread(embed_model.embed_documents,texts)
        # Upsert in pinecone
        ids = [f'{doc_id}-{i}' for i in range(len(embeddings))]
        metadatas = [
            {
                "doc_id" : doc_id,
                "page" : int(chunks[i].metadata.get("page" , 0)),
                "source" : file.filename,
                "grade" : grade,
                "role" : role
            } 
            for i in range(len(embeddings))
        ]
        pinecone_index.upsert(vectors=zip(ids , embeddings , metadatas))
        print("Pinecone added successfully.")

    print(f"Successfully indexed {file.filename}")
    