#-----------------------------------------------------------------------
#                           imoport Statements
#-----------------------------------------------------------------------
import os, asyncio
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from config.db import chunk_collection

# For env 
load_dotenv()
OPENAI_API_KEY = os.getenv("OPEN_AI_API")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")


#-----------------------------------------------------------------------
#                           Logic Statements
#-----------------------------------------------------------------------

# Init Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(name=PINECONE_INDEX_NAME)

# Defining Embed model
embed_model = OpenAIEmbeddings(
    api_key=os.getenv("OPEN_AI_API"),
    model="text-embedding-3-small"
)

# Define model
llm = ChatGroq(model = "llama-3.3-70b-versatile" , temperature=0.3 , api_key=GROQ_API_KEY)

# Define chat prompt for RAG 
rag_prompt=PromptTemplate.from_template(
    """
You are a helpful educational assistant.
Answer the question using ONLY the context below.

Question:
{question}

Context:
{context}

If relevant, mention the document source.

"""
)

# Define Chat Prompt for Quiz Generation
quiz_prompt=PromptTemplate.from_template(
     """
You are a test-generating assistant.

Using the context below, generate {num_questions}
multiple-choice questions.

Format STRICTLY as:

Question 1: ...
A) ...
B) ...
C) ...
Correct Answer: A

Context:
{context}
"""
)

# Define the RAG Chain
rag_chain = rag_prompt | llm 
# Define the quiz chain 
quiz_chain = quiz_prompt | llm

# Define the chat function
async def answer_query(query : str , user_role : str , user_grade : int) -> dict:
    """
        Will fetch doc from  pinecone and with that result get the doc id and then 
        it will check across the mongo and find the docs and then combine them
        and pass to llm in order to generate the answer of the query
        Args:
            query(str) : User question
            user_role(str) : Role of user 
            user_grade(int) : Mostly grade of student
        Returns:
            dict: A dictionary containing two keys:
                - answer: The generated answer or an appropriate error message.
                - sources: A list of source documents used to generate the answer.
    """
    # Call embedding model to generate query embedding
    embedding = await asyncio.to_thread(embed_model.embed_query , query)
    # Retrieve relevant embeddings from the pinecone
    results = await asyncio.to_thread(
        index.query , vector = embedding , top_k = 5,include_metadata = True,filter={
            "grade":user_grade,
            "role":{"$in":["Public",user_role]}
        }
    )
    # Validation check
    if not results.get("matches"):
        return {"answer" : "No relevent information found." , "sources" : []}
    
    # Getting context from mongo 
    chunk_ids = [m['id'] for m in results['matches']]                       # Getting the chunk id
    docs = list(chunk_collection.find({"chunk_id":{"$in":chunk_ids}}))      # Getting the docs
    if not docs:                                                            # Simple Validation
        return {"answer":"Context unavailable","sources":[]}
    doc_map = {d['chunk_id']:d for d in docs}                               # Maping the doc with id                   
    ordered_map = [doc_map[cid] for cid in chunk_ids if cid in doc_map]     # Ordering the doc
    context = "\n\n".join(d['text'] for d in ordered_map)                   # Generating the context
    sources=list({ d["source"] for d in ordered_map})                       # Getting Sources
    response = await asyncio.to_thread(                                     # Getting result from rag chain
        rag_chain.invoke , {"question" : query , "context" : context}
    )
    answer_text=(                                                           # Getting content from the result
        response.content                                                    # If not content then response in string
        if hasattr(response,"content")
        else str(response)
    )

    return {
        "answer" : answer_text,
        "sources" : sources
    }



async def quiz_query(topic : str , user_role : str , user_grade : int , num_questions : int = 5) -> dict:
    """
        Will fetch relevant documents from Pinecone based on the given topic, retrieve
        their corresponding chunks from MongoDB, combine them as context, and pass the
        context to the LLM to generate a quiz.
        Args:
            topic (str): Topic for which the quiz should be generated.
            user_role (str): Role of the user.
            user_grade (int): Grade of the student.
            num_questions (int): Number of quiz questions to generate. Defaults to 5.
        Returns:
            dict: A dictionary containing two keys:
                - quiz: The generated quiz or an appropriate error message.
                - sources: A list of source documents used to generate the quiz.
    """
    # Call embedding model to generate query embedding
    embedding = await asyncio.to_thread(embed_model.embed_query , topic)
    # Retrieve relevant embeddings from the pinecone
    results = await asyncio.to_thread(
        index.query , vector = embedding , top_k = 5,include_metadata = True,filter={
            "grade":user_grade,
            "role":{"$in":["Public",user_role]}
        }
    )
    # Validation check
    if not results.get("matches"):
        return {"quiz" : "No relevent information found to generate quiz" , "sources" : []}
    
    # Getting context from mongo 
    chunk_ids = [m['id'] for m in results['matches']]                       # Getting the chunk id
    docs = list(chunk_collection.find({"chunk_id":{"$in":chunk_ids}}))      # Getting the docs
    if not docs:                                                            # Simple Validation
        return {"quiz":"Context unavailable for quiz","sources":[]}
    doc_map = {d['chunk_id']:d for d in docs}                               # Maping the doc with id                   
    ordered_map = [doc_map[cid] for cid in chunk_ids if cid in doc_map]     # Ordering the doc
    context = "\n\n".join(d['text'] for d in ordered_map)                   # Generating the context
    sources=list({ d["source"] for d in ordered_map})                       # Getting Sources
    response = await asyncio.to_thread(                                     # Getting result from rag chain
        quiz_chain.invoke , {"num_questions" : num_questions , "context" : context}
    )
    quiz_text=(                                                             # Getting content from the result
        response.content                                                    # If not content then response in string
        if hasattr(response,"content")
        else str(response)
    )

    return {
        "quiz" : quiz_text,
        "sources" : sources
    }