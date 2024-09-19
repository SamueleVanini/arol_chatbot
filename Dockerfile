
FROM python:3.10

WORKDIR /arol_chatbot

COPY ./requirements.txt /arol_chatbot/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /arol_chatbot/requirements.txt

COPY ./src /arol_chatbot/src

ENV PYTHONPATH=/arol_chatbot/src

CMD ["fastapi", "run", "src/backend/main.py", "--port", "80"]