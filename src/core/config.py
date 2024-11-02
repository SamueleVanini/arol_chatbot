import os
from dotenv import load_dotenv

REDIS_URL: str = os.getenv('REDIS_URL')

def configure_system():
    """Entry point to configure the running system, add in the body of the function all the logic to configure the chatbot"""
    load_dotenv()