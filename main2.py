from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
import sqlite3
import os

load_dotenv() 
api = os.getenv("GROQ_API_KEY")

questlist = []
responses_to_current = []
happening_now = ["Accepting Topic","Pose Question", "Waiting for Response", "Providing Feedback", "End of Question" ,"End of Topic"]
feed = []
agent_state = {
    "topic": None,
    "topic_understood": 0,
    "question_list": questlist, 
    "count_topic_question": 0,
    "num_attempts" :0,
    "correct": 0,
    "feedback": feed,
    "responses_to_current_q": responses_to_current,
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

def setup():
    try:
        cursor.execute("""SELECT COUNT(*) FROM TOPICS""") 
    except sqlite3.OperationalError:  #if TOPICS doesn't exist - must mean that the QUESTIONS doesn't exist either - checking if the db exists
        agent_state["Now"] = "Accepting Topic"
        cursor.execute(sql1)
        cursor.execute(sql2)     
        print("DB generated")
        
        connection.commit() #create the db from scratch
    else: #otherwise populate the state dictionary with the latest record if the tables aren't empty based on cases
        cursor.execute("""SELECT COUNT(*) FROM TOPICS""")
        rowstopic = cursor.fetchone()
        cursor.execute("""SELECT COUNT(*) FROM QUESTIONS""")
        rowsquest = cursor.fetchone()
        print(rowsquest,rowstopic) #get number of rows in each table if the db exists
 
        if (rowstopic[0]>0) and (rowsquest[0]>0): #if both are not empty, meaning a question has already been asked from a topic 

            sql_latesttopics = """SELECT * FROM TOPICS ORDER BY TopicID DESC LIMIT 1""" # find the latest topic from last record

            cursor.execute(sql_latesttopics)
            out1 = cursor.fetchone() #get the topic
            first_topic = out1[1] #topic last tested
            agent_state["topic"] = first_topic #update state dict
            first_understood = out1[2] 
            agent_state["topic_understood"] = first_understood# update state dict

            sql_quest_lists = f"""SELECT Question FROM QUESTIONS WHERE TopicID = (SELECT TopicID FROM TOPICS WHERE Topic=(?) )  ORDER BY QID""" #get the questions for this topic
            cursor.execute(sql_quest_lists,(first_topic,))
            out2 = cursor.fetchall()
            print(out2)
            for item in out2:
                questlist.append(item[0]) # added the questions previously tested to the state

            agent_state["count_topic_question"] = len(questlist) #number of questions tested added to state

            sql_quest_data = """SELECT * FROM QUESTIONS ORDER BY TopicID DESC LIMIT 1""" #get the last record in QUESTIONS
            cursor.execute(sql_quest_data)
            out3 = cursor.fetchone() #get the tuple of data
            first_resp = out3[3]
            first_feed = out3[4]
            first_attempts = out3[5]
            first_correct = out3[6] #collect all fields

            agent_state["num_attempts"] = first_attempts
            responses_to_current.append(first_resp)
            feed.append(first_feed)
            agent_state["Now"] = "Accepting Topic"

            if agent_state["count_topic_question"] ==5 and first_correct==1: #case where we are at the end of the current topic, reset state dict
                agent_state["Now"] = "Accepting Topic"
                agent_state["topic"]= None
                agent_state["question_list"].clear()
                agent_state["count_topic_question"]= 0
                agent_state["num_attempts"] =0
                agent_state ["correct"]= 0
                agent_state["feedback"].clear()
                agent_state["responses_to_current_q"].clear()    
                agent_state["correct"] = 0  

            if first_correct == 0: 
                agent_state["Now"] = "Waiting for Response" #awaiting another response

        elif (rowstopic[0]>0) and (rowsquest[0]==0): #case where a topic is established but no questions asked yet
            sql_latesttopics = """SELECT * FROM TOPICS ORDER BY TopicID DESC LIMIT 1""" # find the latest topic from last record

            cursor.execute(sql_latesttopics)
            out1 = cursor.fetchone()
            first_topic = out1[1] #topic last tested
            agent_state["topic"] = first_topic
            first_understood = out1[2] 
            agent_state["topic_understood"] = first_understood
            agent_state["Now"] = "Pose Question"

    
model = ChatGroq(api_key=api, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.3)

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
    firstin = input( "Choose a topic: ")
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
    if (agent_state["Now"]=="Accepting Topic" or agent_state["Now"]=="End of Topic" ) and ( agent_state["count_topic_question"]==0 or agent_state["count_topic_question"]==5 ):
        chain = prompt | model | pydparsertopic
        output = chain.invoke({"firstin": firstin})
        print(output)
        topic = output.topic
        agent_state["topic"] = topic
        agent_state["Now"]="Pose Question"
        print(agent_state["Now"])

        topicinsert = """INSERT INTO TOPICS (TopicID, Topic, Understood) VALUES (?,?,?)"""
        cursor.execute(topicinsert, (None, topic, 0))
        connection.commit()

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
    
    topic_now = agent_state["topic"]
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
    if (agent_state["Now"]=="Pose Question" or agent_state["Now"]=="End of Question"  )and len(agent_state["question_list"])<5:
        chain = prompt | model | pydparserquest
        output = chain.invoke({"topic_now": topic_now, "prevq":prevq})
        print(output)
        question = output.question
        agent_state["question_list"].append(question)
        agent_state["Now"]="Waiting for Response"
        agent_state["count_topic_question"] =  agent_state["count_topic_question"] +1
        return question, agent_state



def get_ans(agent_state=agent_state):
     if agent_state["Now"] == "Waiting for Response":
          response = input("Enter your answer: ")
          agent_state["Now"] = 'Providing Feedback'
          agent_state["responses_to_current_q"].append(response)
          agent_state["num_attempts"] = agent_state["num_attempts"] +1
          return response

def mark_response(agent_state=agent_state, model = model, pydparserfeed=pydparserfeed):
    nowquestion=agent_state["question_list"][-1]
    nowresponse = agent_state["responses_to_current_q"][-1]
    pastresponses = agent_state["responses_to_current_q"][:-1]
    num_attempts = agent_state["num_attempts"]
    if agent_state["Now"] == 'Providing Feedback':
        prompt = PromptTemplate(
               template = """
                As part of being a helpful Python tutor, you have to provide feedback to the user's response of a particular python question. Take the following into account strictly:
                \n This is the Question: {nowquestion} \n
                This is the response the user gave: {nowresponse} \n
                These are the past responses to the same question, if you would like to touch on prior mistakes {pastresponses} \n
                This is the number of attempts used in this question {num_attempts} \n
                Format instructions: {format_instructions} \n
                You must force JSON output only, NOTHING ELSE. 
                Feedback must be concise. Don't give away the right answer, unless the number of attempts has increased too much. 
                """,

                input_variables=["nowquestion", "nowresponse","pastresponses","num_attempts"],
                partial_variables = {"format_instructions": pydparserfeed.get_format_instructions()}
            )
        
        chain = prompt | model | pydparserfeed
        output = chain.invoke({"nowquestion":nowquestion,"nowresponse":nowresponse, "pastresponses":pastresponses, "num_attempts":num_attempts} )
        print(output)
        agent_state["correct"] = output.correct
        agent_state["feedback"].append(output.feedback)
        find_topid_id = """SELECT TopicID FROM TOPICS WHERE Topic = (?)"""
        cursor.execute(find_topid_id, (agent_state["topic"],))
        topicid = cursor.fetchone()
        topicid = topicid[0]

        if agent_state["num_attempts"] == 1: #if its the first time the question has beeen posed
            questinsert = """INSERT INTO QUESTIONS (QID, TopicID, Question, Response, Feedback, Attempts, Correct) VALUES (?,?,?,?,?,?,?)"""
            #cursor.execute(topicinsert,(None, agent_state["topic"],0))
            cursor.execute(questinsert,(None, topicid,nowquestion,str(agent_state["responses_to_current_q"]),str(feed),num_attempts,agent_state["correct"] ))
            connection.commit()
        else: #update the response and feedback record
            update_feed_ans = """UPDATE QUESTIONS SET Response = (?), Feedback = (?), Attempts = (?), Correct = (?) WHERE Question=(?)"""
            cursor.execute(update_feed_ans, (str(responses_to_current), str(feed), agent_state["num_attempts"],agent_state["correct"] , nowquestion))
            connection.commit()

        if agent_state["correct"]==1:
            agent_state["Now"] = "End of Question"
             #reset for the next q 
            agent_state["feedback"].clear()
            agent_state["responses_to_current_q"].clear()

            if agent_state["count_topic_question"] == 5: #if we have finished with the topic, reset the state 
                update_understood = """UPDATE TOPICS SET Understood = 1 WHERE TopicID=(?)"""
                cursor.execute(update_understood, (topicid,))
                connection.commit()
                agent_state["topic"]= None
                agent_state["question_list"].clear()
                agent_state["count_topic_question"]= 0
                agent_state["num_attempts"] =0
                agent_state["correct"]= 0
                agent_state["feedback"].clear()
                agent_state["responses_to_current_q"].clear()
                agent_state["Now"] = "End of Topic"

            else:
                agent_state["Now"] = "End of Question"

        else:
            agent_state["Now"] = "Waiting for Response" #awaiting another response

                        
setup()
print("\n State check 1 \n ", agent_state, "=== \n")        
generate_topic(agent_state=agent_state,model=model,pydparsertopic=pydparsertopic)
print("\n State check 2 \n ", agent_state, "=== \n")        
generate_question(agent_state=agent_state, model = model, pydparserquest = pydparserquest)
print("\n State check 3 \n ", agent_state, "=== \n")        
get_ans(agent_state=agent_state)
print("\n State check 4 \n ", agent_state, "=== \n")        
mark_response(agent_state=agent_state, model = model , pydparserfeed=pydparserfeed)
print("\n State check 5 \n ", agent_state, "=== \n")        
