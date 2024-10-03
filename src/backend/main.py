from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.service.chatbot_service import ArolChatBot

app = FastAPI()

chat_bot = None

origins = [
    "http://localhost:3000",
    # Aggiungi altri domini se necessario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define your data models
class Query(BaseModel):
    session_id: str
    input: str


class Response(BaseModel):
    answer: str


@app.on_event("startup")
async def startup_event():
    global chat_bot
    chat_bot = await ArolChatBot().initialize_chat_bot()


@app.post("/query", response_model=Response)
async def query_model(query: Query):
    try:
        response = chat_bot.invoke(
            {"input": query.input},
            config={"configurable": {"session_id": query.session_id}} # Pass the session
        )
        return Response(answer=response["answer"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Hello World"}