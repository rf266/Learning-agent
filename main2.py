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
happening_now = ["Accepting Topic","Pose Question", "Waiting for Response", "Providing Feedback", "Discussion"]

agent_state = {
    "topic": None,
    "question_list": questlist, 
    "count_topic_question": 0,
    "num_attempts" :0,
    "correct": 0,
    "strength": None,
    "current_response": None,
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

class Feedback_structure(BaseModel):
        feedback: str = Field(description="Feedback from user response")
        correct: int = Field(description="Determines whether the user response is correct (1) or incorrect (0)")


pydparsertopic = PydanticOutputParser(pydantic_object=Topic_structure)
pydparserquest = PydanticOutputParser(pydantic_object=Question_structure)
pydparserfeed = PydanticOutputParser(pydantic_object=Feedback_structure)

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
        If it is unclear then suggest your own topic, which must be python related. If there is a clear topic then just follow what the user meant. \n
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
        agent_state["Now"]="Pose Question"
        print(agent_state["Now"])
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
        agent_state["question_list"].append(question)
        agent_state["Now"]="Waiting for Response"
        return question, agent_state



def get_ans(agent_state=agent_state):
     if agent_state["Now"] == "Waiting for Response":
          response = input("Enter your answer: ")
          agent_state["Now"] = 'Providing Feedback'
          agent_state["current_response"] = response
          return response

def mark_response(agent_state=agent_state, model = model, pydparserfeed=pydparserfeed):
    nowquestion=agent_state["question_list"][-1]
    nowresponse = agent_state["current_response"]
    if agent_state["Now"] == 'Providing Feedback':
        prompt = PromptTemplate(
               template = """
                As part of being a helpful Python tutor, you have to provide feedback to the user's response of a particular python question. Take the following into account strictly:
                \n This is the Question: {nowquestion} \n
                This is the response the user gave: {nowresponse} \n
                Format instructions: {format_instructions} \n
                You must force JSON output only, NOTHING ELSE.
                Feedback must be concise. If incorrect, provide hints to get them to the right answer. 
                """,

                input_variables=["nowquestion", "nowresponse"],
                partial_variables = {"format_instructions": pydparserfeed.get_format_instructions()}
            )
        
        chain = prompt | model | pydparserfeed
        output = chain.invoke({"nowquestion":nowquestion,"nowresponse":nowresponse} )
        print(output)
          
    

generate_topic(agent_state=agent_state,model=model,pydparsertopic=pydparsertopic)
generate_question(agent_state=agent_state, model = model, pydparserquest = pydparserquest)
get_ans(agent_state=agent_state)
mark_response(agent_state=agent_state, model = model , pydparserfeed=pydparserfeed)