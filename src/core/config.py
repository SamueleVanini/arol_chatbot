import os

REDIS_URL: str = \
    "redis://default:QWoHMeuRDr3d0Gn0iqvUDAeasUIeqkB3@redis-19112.c339.eu-west-3-1.ec2.redns.redis-cloud.com:19112"


def configure_system():
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_API_KEY'] = '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"'
    os.environ["GROQ_API_KEY"] = "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"