import os

REDIS_URL: str = \
    "redis://default:CnoMxZif4cCZT8SnaUVriz5wdCYSAnUG@redis-19959.c300.eu-central-1-1.ec2.redns.redis-cloud.com:19959"


def configure_system():
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_API_KEY'] = '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'
    os.environ["GROQ_API_KEY"] = "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"