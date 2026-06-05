import gradio as gr
import requests

def submission(text, prev): 
       ans = requests.post("http://127.0.0.1:5000/submit", data={"text":text})
       ans = ans.text
       new = prev + "\n" + ans + "\n" 
       return new

with gr.Blocks() as app:
    gr.Markdown("## **Python Tutoring AI Agent**")
    gr.Markdown("Answer questions, get feedback, get stronger!")
    
    out = gr.Textbox(lines=5, placeholder="Output")
    inp = gr.Textbox(lines=5, placeholder="Input")
    submit_b = gr.Button(value="Submit")
    
    submit_b.click(fn=submission, inputs=[inp, out], outputs=out)
    
    
app.launch()


    