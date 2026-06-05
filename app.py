from flask import Flask, request 
from flask_cors import CORS
from main2 import setup,mark_response,generate_question,get_ans,generate_topic,api,agent_state,connection, cursor, sql1,sql2,model,Topic_structure,Question_structure,Feedback_structure,pydparserfeed,pydparserquest,pydparsertopic


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