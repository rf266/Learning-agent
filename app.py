from flask import Flask, request 
from flask_cors import CORS
from main2 import setup,mark_response,generate_question,get_ans,generate_topic,api,agent_state,connection, cursor, sql1,sql2,model,Topic_structure,Question_structure,Feedback_structure,pydparserfeed,pydparserquest,pydparsertopic
from dotenv import load_dotenv
import os
import sqlite3
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv() 
api = os.getenv("GROQ_API_KEY")

class Topic_structure(BaseModel):
        topic: str = Field(description="Programming topic extracted from user input")

class Question_structure(BaseModel):
        question: str = Field(description="Programming question extracted from predecided topic")

class Feedback_structure(BaseModel):
        feedback: str = Field(description="Feedback from user response")
        correct: int = Field(description="Determines whether the user response is correct (1) or incorrect (0)")


pydparsertopic = PydanticOutputParser(pydantic_object=Topic_structure)
pydparserquest = PydanticOutputParser(pydantic_object=Question_structure)
pydparserfeed = PydanticOutputParser(pydantic_object=Feedback_structure)
#happening_now = ["Accepting Topic","Pose Question", "Waiting for Response", "Providing Feedback", "End of Question" ,"End of Topic"]
text = ""

agent_state = {
    "topic": None,
    "topic_understood": 0,
    "question_list": [], 
    "count_topic_question": 0,
    "num_attempts" :0,
    "correct": 0,
    "feedback": [],
    "responses_to_current_q": [],
    "Now": "Accepting Topic"
}

connection = sqlite3.connect("learn.db")

cursor = connection.cursor()

sql1 = """create table if not exists TOPICS(
    TopicID integer primary key autoincrement, 
    Topic text,
    Understood integer
)"""

sql2 = """create table if not exists QUESTIONS(
    QID integer primary key autoincrement,
    TopicID integer,
    Question text, 
    Response text,
    Feedback text,
    Attempts integer, 
    Correct integer,
    FOREIGN KEY (TopicID) REFERENCES TOPICS(TopicID)
)"""
model = ChatGroq(api_key=api, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.3, streaming=True)


app = Flask(__name__)
CORS(app=app)
setup()
@app.route("/submit", methods=["POST"])
def submission():
    text = request.form.get("text")
    print("Check 1 \n",agent_state)               
    text = generate_topic(agent_state=agent_state,model=model,pydparsertopic=pydparsertopic, text=text)
    print("Check 2 \n",agent_state)
    text = generate_question(agent_state=agent_state, model = model, pydparserquest = pydparserquest)
    print("Check 3 \n",agent_state)
    text= get_ans(agent_state=agent_state, text=text)
    print("Check 4 \n",agent_state)
    text=mark_response(agent_state=agent_state, model = model , pydparserfeed=pydparserfeed)
    print("Check 5 \n",agent_state)
    return text

