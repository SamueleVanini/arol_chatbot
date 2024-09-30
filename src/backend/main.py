from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from src.service.chatbot_service import ArolChatBot
from pydantic import BaseModel


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

@app.options("/query")
async def options_query():
    return {"Allow": "POST, OPTIONS"}


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


@app.post("/query", response_model=HTMLResponse)
async def query_model(query: Query):
    try:
        response = chat_bot.invoke(
            {"input": query.input},
            config={"configurable": {"session_id": query.session_id}}
        )
        return Response(answer=response["answer"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Hello World"}

