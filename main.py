from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_groq import ChatGroq
import sqlite3
import os

load_dotenv() 
api = os.getenv("GROQ_API_KEY")

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

system_prompt = """You are an expert coding tutor specialised in assisting learners how to develop their Python programming skills.
You take in and process user prompts and respond accordingly. 
Your main functionality is testing users on their Python concepts and skills whilst tracking their responses and providing feedback to help them improve. 

When the user starts, either pick a topic to gauge their understanding, or choose based on their prompt. 

You must generate five questions that you will ask the user. 

You are equipped with a connection to database storage, named learn.db. This is done to allow you to track the questions and topics being tested and monitor user performance. 
The database contains two tables, TOPICS and QUESTIONS. This is a one to many relationship, where one TOPIC can have many QUESTIONS.

The database will contain all the TOPICS and QUESTIONS that YOU will ask the user. IT will grow over time. YOU must do the necessary SQL additions

Schemas and information: 

TOPICS table: 
The TOPICS(TopicID, Topic, Understood) table stores the topics being presented to the user.
 It contains a primary key, TopicID, incremented with each unique topic. 
 It has a Topic column, a string storing the topic name.
 It has an Understood column, an integer signifying 0 for False and 1 for True. It is 0 by default, and when the user correctly answers all questions related to this topic, it becomes 1. 

 
The QUESTIONS(QID, TopicID, Question, Response, Feedback, Attempts) table stores the questions presented with each topic. 
The primary key QID is unique for each question, which is an autoincremented integer.
The foreign key TopicID links to the TOPICS table, where each question has a topic it is part of. 
The Question is a string, which is the question itself
The Response is a string, containing all the responses the user had for that particular question. This means that whenever the user reattempts a question, the answer is appended to the existing cell. 
The Feedback is a string, containing all feedback from YOU, the LLM in the same fashion as Response. 
The Attempts is an integer, incrementing everytime the same question is reattempted. 

You are allowed to perform search queries between both tables to find things like the corresponding TopicID for each question, as well as analysing trends. 

YOU are allowed to add records as stipulated by the tools. 

You must not delete any records in any database. 

YOU MUST ONLY USE THE TOOLS THAT ARE PROVIDED. DO NOT INVENT YOUR OWN TOOLS.

INCLUDE ALL REQUIRED FIELDS FOR EACH TOOL

IF YOU FACE ANY ISSUES WITH THE DATABASE OR ANYTHING AT ALL - BE EXTREMELY SPECIFIC IN YOUR RESPONSE

ONLY MOVE ON TO THE NEXT TOPIC WHEN ALL THE QUESTIONS IN THE PREVIOUS HAVE BEEN OVERRIDEN!!
"""


@tool
def gen_questions(topic:str, q1:str, q2:str, q3:str, q4:str, q5:str)->dict:
    """ Adds a set of five questions regarding a specific programming topic to an array, which is added to a dictionary. 

        Args:
            topic: The topic to be tested, as determined by LLM (str)
            q1: Generated question based on topic above (str)
            q2: Generated question based on topic above (str)
            q3: Generated question based on topic above (str)
            q4: Generated question based on topic above (str)
            q5: Generated question based on topic above (str)

        The questions MUST be generated when there is an indication of a need to practice!    

        The function returns this dictionary as an object, which will be used in the below tools later. 
        The key is the 'topic' and values are the array of questions. 
    """
    try:
        questions = [q1,q2, q3,q4,q5]

        qset = {topic: questions}
        return qset
    except:
        return "Questions not generated"

    

@tool
def add_topic(topic:str):
    """ Adds a row in the TOPICS table for each new topic.

    Args:
        topic: The topic to be added to the table and presented to the user (str)

    The topic is determined by:
    - User input and/or
    - What LLM determines to be the best stepping stone for the user's conceptual understanding to grow

    Topics must be unique, and if possible, progressively increase in difficulty based on user performance. 
    Topics must be a SPECIFIC python concept - NOT broad generalisations like 'python basics'!!

    The Topic is assigned a TopicID, which is auto incremented based on what is in the database table.
    This is why it is passed as NULL in the SQL command. 

    By default, the Understood value is False, denoted by 0. This will be updated to true (1) only when the user has correctly answered all questions regarding this topic.

    """
    try:
        connection = sqlite3.connect("learn.db")

        cursor = connection.cursor()
        sqlinsert = "insert into TOPICS values (?,?,?)"
        print("topic executing...")
        cursor.execute(sqlinsert, (None, topic,0))
        print("topic committing...")
        connection.commit()
        print("connection closing")
        connection.close()
        print("Topic added")
        return "Topic added"
    
    except Exception as e:
        return f"Error adding topic: {e}"

@tool
def add_question(topic_id:int, response:str, feedback:str, qset:dict):
    """ Adds a question to the database as it is being given to the user. When this is happening, the dictionary containing the questions is altered, where the question is removed from the array. 
    It takes in the TopicID as a foreign key relating to the topic in which the question is linked to.
    
    Args:
        topic_id: The TopicID for the particular topic being tested by the question. This is a foreign key, the primary key from the TOPICS table (int)
        response: The user's response to the question (str)
        feedback: The LLM's feedback to the user, accumulated throughout each time the user responds to this particular question (str)
        qset: The dictionary containing each question, returned by gen_questions tool (dict)

    All questions are stored in the 'qset' dictionary. When the question is posed , it is removed, and the updated dictionary is returned by the function. 
    The Attempts cell for the record is set to 1 the first time a question is answered.
    When a user answers, their 'response' and YOUR LLM Feedback is added. 
    If the question is posed again if the user gives the wrong answer, the Attempts cell is incremented by 1.

    This function adds a question to the QUESTIONS table when it is posed to the user for the first time. 
    The questions are sourced from the qset dictionary, returned in the gen_questions tool

    Important Notes: 
    The primary key for the QUESTIONS table, QID, is automatically generated, incremented with each unique question. This is why it is passed as NULL in the SQL command. 
    The TopicID must be sourced by querying the TOPICS table for the Topic that is the key in the qset dictionary. 

    If the user responds incorrectly to the question, their reattemped response should not be overwritten, rather, just appended to what is already stored in the Response cell.
    Feedback must also be dealt with in the same manner as Response. 
    Attempts is set to 1 by default. If the same question is reatttempted, increment this in the cell.
    This helps the LLM understand the user's thought and response pattern, informing how they will perform in future topics. 

    ASK QUESTIONS ONE BY ONE
    """
    try:
        connection = sqlite3.connect("learn.db")

        cursor = connection.cursor()
        question = qset[0][0]
        qset = qset[0][1:]
        sqlinsert = "insert into QUESTIONS values(?,?,?,?,?,?)"
        cursor.execute(sqlinsert, (None, topic_id, question, response, feedback, 1))
        connection.commit()
        connection.close()
        return "Question added", qset
    except Exception as e:
        return f"Error adding question: {e}", qset

model = ChatGroq(api_key=api, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7)
tools = [gen_questions, add_question,add_topic ]
agent = create_agent(model=model, tools=tools, system_prompt=system_prompt)

try: 
    while True: 
        result = agent.invoke(
            {"messages": [{"role": "user", "content": input(">>> ") }]}
        )
        print(result["messages"][-1].content, flush=True)
except Exception as e:
    print("Error ", e)

