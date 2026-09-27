from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt,Command
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from agent.state import EmailState
from agent.agent import agent_node
from agent.email_tool import send_email

load_dotenv()
# -------------------------
# TOOLS
# -------------------------

tools = [send_email]

tool_node = ToolNode(tools)


# -------------------------
# APPROVAL
# -------------------------

def approval_node(state: EmailState):

    last_message = state["messages"][-1]

    tool_call = last_message.tool_calls[0]

    args = tool_call["args"]

    decision = interrupt({
        "message": "Do you want to send this email?",
        "to": args["to"],
        "subject": args["subject"],
        "body": args["body"]
    })

    return {
        "approved": decision
    }


# -------------------------
# AGENT ROUTING
# -------------------------

def should_continue(state: EmailState):

    last_message = state["messages"][-1]

    # Agent wants to use a tool
    if last_message.tool_calls:
        return "approval"

    # Agent doesn't need a tool
    return "end"


# -------------------------
# APPROVAL ROUTING
# -------------------------

def after_approval(state: EmailState):

    if state["approved"] is True:
        return "tools"

    return "end"


# -------------------------
# GRAPH
# -------------------------

builder = StateGraph(EmailState)

builder.add_node("agent", agent_node)
builder.add_node("approval_node", approval_node)
builder.add_node("tools", tool_node)


# START → Agent
builder.add_edge(
    START,
    "agent"
)


# Agent → Approval OR END
builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "approval": "approval_node",
        "end": END
    }
)


# Approval → ToolNode OR END
builder.add_conditional_edges(
    "approval_node",
    after_approval,
    {
        "tools": "tools",
        "end": END
    }
)


# ToolNode → Agent
builder.add_edge(
    "tools",
    END
)


# Memory for interrupt/resume
checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)



if __name__ == "__main__":

    config = {
        "configurable": {
            "thread_id": "email-agent-1"
        }
    }

    # Ask the user what they want the agent to do
    user_request = input("What do you want me to do? ")

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_request
                }
            ],
            "approved": None
        },
        config=config
    )

    # Graph is waiting for human approval
    if "__interrupt__" in result:

        approval = result["__interrupt__"][0].value

        print("\n" + approval["message"])

        print("\nTo:", approval["to"])
        print("Subject:", approval["subject"])
        print("Body:", approval["body"])

        answer = input("\nYes / No: ")

        result = graph.invoke(
            Command(
                resume=answer.lower() == "yes"
            ),
            config=config
        )

    print("\nFinal:", result)


'''                    ┌──────────────┐
                    │    AGENT     │
                    │ LLM + tools  │
                    └──────┬───────┘
                           │
                    tool call?
                     /          \
                   NO            YES
                   ↓              ↓
                 END          APPROVAL
                                  │
                             Yes / No
                            /         \
                          NO           YES
                          ↓             ↓
                         END         TOOLS
                                      │
                                      ↓
                                  Gmail send
                                      │
                                      ↓
                                     END'''