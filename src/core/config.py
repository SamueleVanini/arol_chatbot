import os

REDIS_URL: str = \
    "redis://default:QWoHMeuRDr3d0Gn0iqvUDAeasUIeqkB3@redis-19112.c339.eu-west-3-1.ec2.redns.redis-cloud.com:19112"


def configure_system():
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_API_KEY'] = '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"'
    os.environ["GROQ_API_KEY"] = "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"