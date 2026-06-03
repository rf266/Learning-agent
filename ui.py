import gradio as gr
#import main2

def decide_action():
    return "hey"

with gr.Blocks() as app:
    gr.Markdown("## **Python Tutoring AI Agent**")
    gr.Markdown("Answer questions, get feedback, get stronger!")

    gr.Textbox(lines=5, placeholder="Output")
    gr.Textbox(lines=5, placeholder="Input")
    submit = gr.Button(value="Submit")
    
app.launch()