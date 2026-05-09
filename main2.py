from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
import json
import sqlite3
import os

load_dotenv() 
api = os.getenv("GROQ_API_KEY")

strengths = ["Strong", "Intermediate", "Weak"]
questlist = []
happening_now = ["Accepting Topic","Pose Question", "Waiting for Response", "Providing Feedback", "Providing Clarification"]

agent_state = {
    "topic": None,
    "question_list": questlist, 
    "count_topic_question": 0,
    "num_attempts" :0,
    "correct": 0,
    "strength": None,
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
    FOREIGN KEY (TopicID) REFERENCES TOPICS(TopicID)
)"""

cursor.execute(sql1)
cursor.execute(sql2)

print("DB generated")

system_prompt = "You are a helpful Python Programming tutor. " \
"You will generate questions as called by functions to test the user on their desired concepts. " \
"You will then mark their responses. Act as you are told by the prompts - more info will follow"

model = ChatGroq(api_key=api, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.3)
agents = create_agent(model=model, system_prompt=system_prompt)

class Topic_structure(BaseModel):
        topic: str = Field(description="Programming topic extracted from user input")

class Question_structure(BaseModel):
        question: str = Field(description="Programming question extracted from predecided topic")


pydparsertopic = PydanticOutputParser(pydantic_object=Topic_structure)
pydparserquest = PydanticOutputParser(pydantic_object=Question_structure)

def generate_topic(agent_state=agent_state,model=model,pydparsertopic=pydparsertopic): 
    """
    A function that generates a Topic field based on user input.

    Args:
        agent_state - dictionary of agent's current state
        model - agent model
        pydparser - Pydantic parser of LLM output of Topic field

    Returns: 
        JSON output with one field, "Topic" 
    """
    firstin = input(">>> ")
    prompt = PromptTemplate(
         template="""
         You are a helpful python tutor. Right now you need to understand what topic the user wants to be tested on.
        The user has entered this: \n {firstin} \n
        Generate the name of the topic to be tested in the specified schema. 
        If it is unclear then suggest your own topic. If there is a clear topic then just follow what the user meant. \n
        Format instructions: {format_instructions}
        You must force JSON output only, NOTHING ELSE
        """,
        input_variables=["firstin"],
        partial_variables={"format_instructions": pydparsertopic.get_format_instructions()}

    )
    if agent_state["Now"]=="Accepting Topic":
        chain = prompt | model | pydparsertopic
        output = chain.invoke({"firstin": firstin})
        print(output)
        topic = output.topic
        agent_state["Topic"] = topic
        return topic, agent_state
        

def generate_question(agent_state=agent_state, model = model, pydparserquest = pydparserquest):
    """
    A function that takes the state's Topic field and generates a question with the LLM. then updates the state with the current question

    Args:
        agent_state - dictionary of agent's current state
        model - agent model
        pydparser - Pydantic parser of LLM output of Question field

    Returns: 
        JSON output with one field, "Question" 
    """
    
    topic_now = agent_state["Topic"]
    prevq = agent_state["question_list"]

    prompt = PromptTemplate(
        template="""
        You are a helpful python tutor. Right now you need to ask the user a question based on the topic.
        The topic is this: \n {topic_now} \n
        The set of previously asked questions is this: \n {prevq} \n
        Do not repeat any questions of similar nature. \n
        Format instructions: {format_instructions}
        You must force JSON output only, NOTHING ELSE
        """,
        input_variables=["topic_now", "prevq"],
        partial_variables={"format_instructions": pydparserquest.get_format_instructions()}

    )
    if agent_state["Now"]=="Pose Question":
        chain = prompt | model | pydparserquest
        output = chain.invoke({"topic_now": topic_now, "prevq":prevq})
        print(output)
        question = output.question
        agent_state["question_list"] = agent_state["question_list"].append(question)
        return question, agent_state



