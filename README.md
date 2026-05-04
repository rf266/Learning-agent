# AI Coding Tutor Agent 

This agent is an AI-powered coding tutor. It is designed to help users strengthen their conceptual and code understanding of Python by asking questions targetting specific topics. 

**This project is a work in progress**. Currently, I am working through state preservation challenges, and developing efficient system design to allow the LLM to have an approporiate level of control over the process. 

## Tech Stack
- Langchain agent orchestration
- SQLite database storage
- Streamlit prototyping

*AI was used throuhgout the process, supporting ideation, system design, debugging etc. This was an especially important tool, used with thought, to allow me to navigate through unfamiliar challenges.*

## Significant Decisions in Agent Development

- Agent creation 
The structure and functions of the different components of a Langchain agent were investigated. This was used instead of sending API calls to the LLM due to the presence of tool functions which could be used as required by the situation. The chosen LLM, after experimenting with responses and token size limitations, was Llama 4 Scout, obtained from Groq.

- Tool Development
One of the most significant challenges was seen in tool development, where, after research and AI consultation, it was found that the LLM must be explicitly shown the tools it can used to operate as desired. The uncertainty created by missing information causes the model to behave unpredictably, where I even found that it was creating its own functions, as well as generating its own SQL queries. 

Another important consideration was the level of detail to be provided in tool docstrings. It was often the case that the lengthy docstrings would override token limitations, especially in the earlier LLMs tested. I learnt how to ensure that the LLM has complete knowledge over the full interactions it can have over the tool. 

The system prompt was also one of concern, where it was found that a detailed prompt was required to outline all use cases and prevent uncertainties for the model. It deeply outlined a typical agent workflow, database schema and style of interaction. 

- SQLite database

A database was created to store the topics and questions posed to the user, as part of a tracking system to allow the the agent to analyse how the questions were answered. 

The database schema is below:
TOPICS(TopicID, Topic, Understood)
QUESTIONS(QID, TopicID, Question, Response, Feedback, Attempts)

A one to many relationship is demonstrated - one topic can have many questions, but one question can have one topic, for now. 



## Sources - non exhaustive 

AI was used throuhgout the process, supporting ideation, system design, debugging etc. This was an especially important tool, used with thought, to allow me to navigate through unfamiliar challenges. Rather than taking its suggestions blindly, I tried to understand how and why it would fit into my code. Programming knowledge cannot truly be replaced by AI. 

One of the main challenges was navigating outdated documentation/fixes, even if published recently. Langchain grows at a rapid rate, and updates are done to the package quite frequently, and they are not all reflected. 

By looking at forums, I was able to understand how to better structure my code, especially docstrings, which are the fundamental instruction for the LLM's tool orchestration. 

### Documentation 
Langchain
Groq-Langchain
SQLite - Python docs
HuggingFace - model information 

### Help/research 
- https://www.youtube.com/watch?v=jsX99U8UkOo - SQLite DB Creation 


- https://www.w3schools.com/sql/sql_datatypes.asp - SQL Datatypes

- https://www.youtube.com/watch?v=eD2oAsalw7E - SQLite DB table creation 

- https://www.youtube.com/watch?v=YqvCfS6sv7k - SQLite insertion statements

- https://stackoverflow.com/questions/29076312/inserting-sqlite-primary-key-in-python - Primary key 

-https://www.ibm.com/think/topics/llm-temperature#:~:text=Temperature%20controls%20the%20randomness%20of,according%20to%20a%20probability%20distribution. - model temperature

- https://www.reddit.com/r/LangChain/comments/1k0adul/custom_tools_with_multiple_parameters/ - tool parameters and docstring structure


https://www.reddit.com/r/LangChain/comments/1kfifju/is_it_possible_to_do_tool_calling_sql_with/ - Langchain tool calling 


- https://github.com/langchain-ai/langchain-aws/issues/524 snake case


- https://www.reddit.com/r/LocalLLaMA/comments/13nm96l/models_are_repeating_text_several_times/ - repeated words generated 


https://www.arsturn.com/blog/langchain-llm-returning-empty-results-common-fixes - empty outputs

https://www.youtube.com/watch?v=vzJOAnwIokM - Langchain overview

#### Stack overflow questions I posted

- https://stackoverflow.com/questions/79907528/why-does-groq-langchain-model-return-tool-use-failed-error/79907609#79907609

- https://stackoverflow.com/questions/79910632/langchain-tool-does-not-implement-database-record-addition?r=2

https://stackoverflow.com/questions/79915713/langchain-agent-state-preservation?r=2

https://ai.stackexchange.com/questions/50494/langchain-agent-state-preservation