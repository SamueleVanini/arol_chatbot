from dotenv import load_dotenv

# this should be moved in the .env file too
REDIS_URL: str = (
    "redis://default:QWoHMeuRDr3d0Gn0iqvUDAeasUIeqkB3@redis-19112.c339.eu-west-3-1.ec2.redns.redis-cloud.com:19112"
)


def configure_system():
    """Entry point to configure the running system, add in the body of the function all the logic to configure the chatbot"""
    load_dotenv()
