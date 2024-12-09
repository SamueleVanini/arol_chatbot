from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from src.backend.user_collection import UserConnection
from src.service.chatbot_service import ArolChatBot

app = FastAPI()

chat_bot = None

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    # Aggiungi altri domini se necessario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_connection = UserConnection()


# Define your data models
class Query(BaseModel):
    session_id: str
    input: str


class Response(BaseModel):
    answer: str


class UserCreate(BaseModel):
    username: str
    password: str
    password_confirm: str  # Note: field name should match what you're validating

    @field_validator('password_confirm')
    def passwords_match(cls, value, values):
        if 'password' in values.data and value != values.data['password']:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Passwords do not match",
            )
        return value

    @field_validator('password')
    def password_strength(cls, value):
        if len(value) < 8:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Password must be at least 8 characters long",
            )
        return value


class User(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@app.on_event("startup")
async def startup_event():
    global chat_bot
    chat_bot = await ArolChatBot().initialize_chat_bot()


@app.post("/query", response_model=Response)
async def query_model(query: Query, current_user: dict = Depends(user_connection.get_current_user)):
    username = current_user["username"]
    session_ids = user_connection.get_user_sessions(username)
    if not session_ids or (query.session_id not in session_ids):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have the Permission for this request (Wrong Session ID)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        response = chat_bot.invoke(
            {"input": query.input},
            config={"configurable": {"session_id": query.session_id}}
        )
        return Response(answer=response["answer"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login", response_model=Token)
async def login_for_access_token(user: User) -> Token:
    user_exist = user_connection.authenticate_user(user.username, user.password)
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = user_connection.create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


@app.post("/register",status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    user_exist = user_connection.get_user(username=user.username)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    try:
        user_connection.create_user(user.username, user.password)
        return {"username":user.username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/session")
async def get_session(current_user: dict = Depends(user_connection.get_current_user)):
    username = current_user["username"]
    session_id = user_connection.add_session(username)
    return {"session_id": session_id}


@app.get("/user/session/all")
async def get_user_sessions(current_user: dict = Depends(user_connection.get_current_user)):
    username = current_user["username"]
    session_ids = user_connection.get_user_sessions(username)
    return {"session_ids": session_ids}


@app.get("/user/session/{session_id}")
async def get_session_history(session_id: str, current_user: dict = Depends(user_connection.get_current_user)):
    username = current_user["username"]
    session_ids = user_connection.get_user_sessions(username)

    if session_id in session_ids:
        history = await user_connection.get_session_history(session_id)
        return {"history": history}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have the Permission for this request",
            headers={"WWW-Authenticate": "Bearer"},
        )
