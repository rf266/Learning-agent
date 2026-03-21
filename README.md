# Learning AI Agent 

A one to many relationship demonstrated - one topic can have many questions, but one question can have one topic as this is primarily focused on simple concepts as an MVP


## Sources - non exhaustive 

AI was used throuhgout the process, supporting ideation, system design, debugging etc. This was an especially important tool, used with thought, to allow me to navigate through unfamiliar challenges. Rather than taking its suggestions blindly, I tried to understand how and why it would fit into my code. Programming knowledge cannot truly be replaced by AI. 

One of the main challenges was navigating outdated documentation/fixes, even if published recently. Langchain grows at a rapid rate, and updates are done to the package quite frequently, and they are not all reflected. 

By looking at forums, I was able to understand how to better structure my code, especially docstrings, which are the fundamental instruction for the LLM's tool orchestration. 

- Documentation 
Langchain
Groq-Langchain
SQLite - Python docs
HuggingFace - model information 

- Help/research 
https://www.youtube.com/watch?v=jsX99U8UkOo - SQLite DB Creation 
https://www.w3schools.com/sql/sql_datatypes.asp - SQL Datatypes
https://www.youtube.com/watch?v=eD2oAsalw7E - SQLite DB table creation 
https://www.youtube.com/watch?v=YqvCfS6sv7k - SQLite insertion statements
https://stackoverflow.com/questions/29076312/inserting-sqlite-primary-key-in-python - Primary key 
https://www.ibm.com/think/topics/llm-temperature#:~:text=Temperature%20controls%20the%20randomness%20of,according%20to%20a%20probability%20distribution. - model temperature
https://www.reddit.com/r/LangChain/comments/1k0adul/custom_tools_with_multiple_parameters/ - tool parameters and docstring structure
https://www.reddit.com/r/LangChain/comments/1kfifju/is_it_possible_to_do_tool_calling_sql_with/ - Langchain tool calling 
https://github.com/langchain-ai/langchain-aws/issues/524 snake case

Stack overflow questions I posted
https://stackoverflow.com/questions/79907528/why-does-groq-langchain-model-return-tool-use-failed-error/79907609#79907609

https://stackoverflow.com/questions/79910632/langchain-tool-does-not-implement-database-record-addition?r=2