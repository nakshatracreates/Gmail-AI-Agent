import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from agent.email_tool import send_email
from agent.state import EmailState

load_dotenv()

model = ChatOpenAI(model="gpt-5-mini")

# Bind tools to model
model_with_tools = model.bind_tools([send_email])

def agent_node(state: EmailState):
    system_message = SystemMessage(
        content="""
        You are an email assistant.

        If the user asks you to send an email and provides
        enough information, use the send_email tool.

        Do not ask unnecessary clarification questions.

        If the user says "Langraph", interpret it as
        "LangGraph" when the context clearly indicates that.
        """
    )

    response = model_with_tools.invoke(
        [system_message] + state["messages"]
    )

    return {
        "messages": [response]
    }