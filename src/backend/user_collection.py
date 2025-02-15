import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
import redis
from fastapi import Depends, HTTPException, status
from jwt import InvalidTokenError

from src.backend.utils.auth_service import AuthService
from src.core.config import REDIS_URL
from src.backend.mongo_connection import get_database


class UserConnection:

    def __init__(self):
        self.dbname = get_database()
        self.collection_name = self.dbname["user"]
        self.collection_name.create_index('username', unique=True)
        self.auth = AuthService()

    def get_user(self, username):
        return self.collection_name.find_one({"username": username})

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not user:
            return False
        if not self.auth.verify_password(password, user.get("password")):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=1)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.auth.SECRET_KEY, algorithm=self.auth.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: Annotated[str, Depends(AuthService.oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.auth.SECRET_KEY, algorithms=[self.auth.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception

        except InvalidTokenError:
            raise credentials_exception
        user = self.get_user(username)
        if user is None:
            raise credentials_exception
        return user

    def create_user(self, username: str, password: str):
        user_document = {
            'username': username,
            'password': self.auth.get_password_hash(password),
            'session_ids': [],  # Initialize empty list for session IDs
            'created_at': datetime.now()
        }

        try:
            result = self.collection_name.insert_one(user_document)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def add_session(self, username: str) -> str | None:
        try:
            # Create a new session
            chat_id = uuid.uuid4().hex
            session = username + chat_id

            # Find user and update their sessions list
            result = self.collection_name.update_one(
                {"username": username},
                {
                    "$push": {
                        "sessions": session
                    }
                }
            )

            if result.modified_count == 0:
                return None

            return session

        except Exception as e:
            print(f"Error adding session: {e}")
            return None

    def get_user_sessions(self, username: str):
        user = self.collection_name.find_one(
            {"username": username},
            {"sessions": 1}
        )
        return user.get("sessions", []) if user else []

    @staticmethod
    async def get_session_history(session_id):
        history = []

        r = redis.from_url(REDIS_URL)
        pattern = f"chat:{session_id}:*"

        # Fetch keys that match the pattern
        matching_keys = r.keys(pattern)
        for key in matching_keys:
            # Get the JSON string from Redis
            json_data = r.json().get(key)
            if json_data:
                history.append(json_data)

        return history
