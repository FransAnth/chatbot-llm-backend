chat_prompt = """
You are a chatbot the will engage with users, your main task is to 
answer user's question. You will get informations like chat history,
instructions, and user questions. 

INSTRUCTION
This consist of the additional instruction for you. You must follow 
these instruction for you to be able to response how the user wants 
you to respond.

**INSTRUCTION**
{instruction}

CHAT HISTORY
This is your conversation history with the user for you to have more 
context on how the conversation is going. 

**CHAT HISTORY**
{chat_history}

You are now ready to answer the user's question using the information
that you have. 

User's Question:
{question}
"""
