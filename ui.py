import gradio as gr
#import main2
import requests
from main2 import setup,mark_response,generate_question,get_ans,generate_topic,api,agent_state,connection, cursor, sql1,sql2,model,Topic_structure,Question_structure,Feedback_structure,pydparserfeed,pydparserquest,pydparsertopic

def submit(text, prev): 
       # requests.post("/", data=text)
       ans = requests.post("")
       new = prev + "\n" + text + "\n" 
       return  new

with gr.Blocks() as app:
    gr.Markdown("## **Python Tutoring AI Agent**")
    gr.Markdown("Answer questions, get feedback, get stronger!")
    
    out = gr.Textbox(lines=5, placeholder="Output")
    inp = gr.Textbox(lines=5, placeholder="Input")
    submit_b = gr.Button(value="Submit")
    
    submit_b.click(fn=submit, inputs=[inp, out], outputs=out)
    
    
app.launch()


    