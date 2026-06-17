from main2 import setup,mark_response,generate_question,get_ans,generate_topic,api,agent_state,connection, cursor, sql1,sql2,model,Topic_structure,Question_structure,Feedback_structure,pydparserfeed,pydparserquest,pydparsertopic
from dotenv import load_dotenv
import os
import sqlite3
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import gradio as gr

load_dotenv() 
api = os.getenv("GROQ_API_KEY")
text = ""

connection = sqlite3.connect("learn.db", check_same_thread=False)

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


agent_state, message = setup()

def startup():
    return message


def submission(text, prev): 
    inputs = text
    state = agent_state["Now"]
    new = prev + "\n" + text + "\n" 
    print("Check 1 \n",agent_state)
    if state=="Accepting Topic" or state=="End of Topic":
        if (agent_state["Now"]=="Accepting Topic" or agent_state["Now"]=="End of Topic" ) and ( agent_state["count_topic_question"]==0 or agent_state["count_topic_question"]==5 ):               
            text = generate_topic(agent_state=agent_state,model=model,pydparsertopic=pydparsertopic, text=inputs)
            new = new + "\n" + text + "\n" 
            yield "", new
        print("Check 2 \n",agent_state)
        if (agent_state["Now"]=="Pose Question" or agent_state["Now"]=="End of Question"  )and len(agent_state["question_list"])<5:
            text = generate_question(agent_state=agent_state, model = model, pydparserquest = pydparserquest, text=text)
            new = new + "\n" + text + "\n" 
            yield "", new
        print("Check 3 \n",agent_state)
    
    if state=="Waiting for Response":
        if agent_state["Now"] == "Waiting for Response":
            text= get_ans(agent_state=agent_state, text=inputs)
            new = new + "\n" + text + "\n" 
            yield "", new
        print("Check 4 \n",agent_state)

        if agent_state["Now"] == 'Providing Feedback':
            text=mark_response(agent_state=agent_state, model = model , pydparserfeed=pydparserfeed,text=text)
            new = new + "\n" + text + "\n" 
            yield "", new
        print("Check 5 \n",agent_state)

        if (agent_state["Now"]=="Pose Question" or agent_state["Now"]=="End of Question"  )and len(agent_state["question_list"])<5:
            text = generate_question(agent_state=agent_state, model = model, pydparserquest = pydparserquest, text=text)
            new = new + "\n" + text + "\n" 
            yield "", new





with gr.Blocks() as app:
    gr.Markdown("## **Python Tutoring AI Agent**")
    gr.Markdown("Answer questions, get feedback, get stronger!")
    
    out = gr.Textbox(lines=5, placeholder="Output", interactive=False)
    inp = gr.Textbox(lines=1, placeholder="Input")
    submit_b = gr.Button(value="Submit")


    app.load(fn=startup, inputs = None, outputs=out)
    submit_b.click(fn=submission, inputs=[inp, out], outputs=[inp,out])
    
    
app.launch()