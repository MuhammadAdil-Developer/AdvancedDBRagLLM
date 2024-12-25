from typing import List, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from MyProject.src.chatbot.load_config import LoadProjectConfig
from MyProject.src.agent_graph.load_tools_config import LoadToolsConfig
from MyProject.src.agent_graph.build_full_graph import build_graph
from MyProject.src.utils.app_utils import create_directory
from MyProject.src.chatbot.memory import Memory
import asyncio
import uuid
from openai import OpenAI
import openai
import os

URL = "https://github.com/Farzad-R/LLM-Zero-to-Hundred/tree/master/RAG-GPT"
hyperlink = f"[RAG-GPT user guideline]({URL})"

PROJECT_CFG = LoadProjectConfig()
TOOLS_CFG = LoadToolsConfig()

graph = build_graph()
config = {"configurable": {"thread_id": TOOLS_CFG.thread_id}}

create_directory("memory")

# FastAPI instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

os.environ['OPENAI_API_KEY'] = os.getenv("OPEN_AI_API_KEY")
api_key = os.environ['OPENAI_API_KEY']  # Assign to a variable for reuse

# Configure OpenAI with the API key
openai.api_key = api_key

async def generate_heading(human_messages: List[str], ai_responses: List[str]) -> str:
    if not human_messages and not ai_responses:
        return "New Conversation"

    # Construct the conversation text
    conversation_text = "\n".join(
        f"User: {user}\nAI: {ai}" for user, ai in zip(human_messages, ai_responses)
    )
    prompt = f"{conversation_text}\n\nGenerate a very short concise and meaningful heading for this conversation. Note: Dont use commas and anytype of brackets please"

    # Use the OpenAI API to get a response
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    # Return the generated heading
    return response.choices[0].message.content.strip()

class ChatBot:
    @staticmethod
    def respond(chatbot: dict, message: str) -> dict:
        events = graph.stream(
            {"messages": [("user", message)]}, config, stream_mode="values"
        )
        bot_response = ""
        for event in events:
            bot_response = event["messages"][-1].content
            event["messages"][-1].pretty_print()

        chatbot['human_message'].append(message)
        chatbot['Ai_response'].append(bot_response)

        return chatbot

# Define Pydantic model for the request body
class MessageRequest(BaseModel):
    message: str

# Define Pydantic model for the response
class ChatResponse(BaseModel):
    thread_id: str
    human_message: List[str]
    Ai_response: List[str]
    heading: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: MessageRequest, thread_id: str = None):
    if thread_id is None:
        # Generate a new thread_id for a new session
        thread_id = str(uuid.uuid4())
        chatbot_history = {'human_message': [request.message], 'Ai_response': []}
        
        # Generate AI response to the first message
        chatbot_history = ChatBot.respond(chatbot_history, request.message)
        
        # Generate heading based on the first message and AI response
        heading = await generate_heading([request.message], chatbot_history['Ai_response'])
    else:
        chatbot_history = Memory.load_chat_history_from_db(thread_id)
        if not chatbot_history['human_message'] and not chatbot_history['Ai_response']:
            raise HTTPException(status_code=404, detail="No chat history found for this thread_id.")

        existing_threads = Memory.load_all_thread_ids_from_db()
        heading = next((thread.get('heading') for thread in existing_threads if thread['thread_id'] == thread_id), None)
        if not heading:
            heading = "Default Heading"

    # For subsequent messages, just respond without generating the heading again
    chatbot_history = ChatBot.respond(chatbot_history, request.message)

    # Save the chat history to the database
    Memory.write_chat_history_to_db(chatbot_history, thread_id, heading)

    # Return the response with the thread_id, human_message, Ai_response, and heading
    return ChatResponse(
        thread_id=thread_id,
        human_message=chatbot_history['human_message'],
        Ai_response=chatbot_history['Ai_response'],
        heading=heading,
    )



@app.get("/chat")
async def get_chat_history(thread_id: str = None):
    """
    Endpoint to retrieve chat history for a specific thread ID or all thread IDs if none is provided.

    Args:
        thread_id (str): Unique identifier for the chat session (optional, passed as a query parameter)

    Returns:
        List[Dict[str, str]] or ChatResponse: A list of thread IDs or the chat history for the given thread ID.
    """
    if thread_id is None:
        # Fetch all thread IDs from the database
        thread_ids = Memory.load_all_thread_ids_from_db()
        if not thread_ids:
            raise HTTPException(status_code=404, detail="No thread IDs found")

        return thread_ids

    # Fetch chat history from the database for the given thread_id
    chat_history = Memory.load_chat_history_from_db(thread_id)

    if not chat_history:
        raise HTTPException(status_code=404, detail="Chat history not found")

    heading = "Default Heading" 
    if 'heading' in chat_history:
        heading = chat_history['heading']

    return ChatResponse(
        thread_id=thread_id,
        human_message=chat_history['human_message'],
        Ai_response=chat_history['Ai_response'],
        heading=heading,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



