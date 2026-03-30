# from core.llm import get_llm, get_prompt_template
# from agents.research_agent import run_research_agent
# from agents.writer_agent import run_writer_agent
# from langchain.schema import HumanMessage, AIMessage
# from pydantic import BaseModel
# from typing import Literal, List, Dict
# import logging

# logger = logging.getLogger(__name__)

# # -----------------------------
# # ✅ Agent Registry (Scalable)
# # -----------------------------
# def run_chat_agent(message: str, history: list):
#     prompt_template = get_prompt_template(
#         system="You are NanoClaw, a helpful AI assistant. Be concise and clear."
#     )
#     llm = get_llm()
#     chain = prompt_template | llm

#     response = chain.invoke({
#         "history": _build_history(history),
#         "input": message
#     })
#     return response.content


# AGENTS = {
#     "RESEARCH": run_research_agent,
#     "WRITE": run_writer_agent,
#     "CHAT": run_chat_agent
# }

# # -----------------------------
# # ✅ Structured Output
# # -----------------------------
# class Decision(BaseModel):
#     agent: Literal["RESEARCH", "WRITE", "CHAT"]

# ORCHESTRATOR_SYSTEM = """
# You are an Orchestrator Agent.

# Your job:
# Decide which agent should handle the user request.

# Available agents:
# - RESEARCH → searching / information / facts
# - WRITE → saving / writing notes / creating content
# - CHAT → normal conversation

# Return ONLY valid JSON:
# {"agent": "RESEARCH"} or {"agent": "WRITE"} or {"agent": "CHAT"}
# """

# # -----------------------------
# # ✅ Decide Agent
# # -----------------------------
# def decide_agent(message: str, history: list) -> str:
#     try:
#         llm = get_llm()

#         structured_llm = llm.with_structured_output(Decision)

#         prompt_template = get_prompt_template(system=ORCHESTRATOR_SYSTEM)
#         chain = prompt_template | structured_llm

#         result: Decision = chain.invoke({
#             "history": _build_history(history),
#             "input": message
#         })

#         logger.info(f"Orchestrator Decision: {result.agent}")
#         return result.agent

#     except Exception as e:
#         logger.error(f"Decision failed: {str(e)}")
#         return "CHAT"


# # -----------------------------
# # ✅ Main Orchestrator
# # -----------------------------
# def run_orchestrator(message: str, history: list = []) -> str:
#     try:
#         decision = decide_agent(message, history)

#         agent_fn = AGENTS.get(decision, run_chat_agent)

#         logger.info(f"Routing → {decision}")

#         # Handle WRITE special case
#         if decision == "WRITE":
#             return agent_fn(message, filename="note", history=history)

#         return agent_fn(message, history)

#     except Exception as e:
#         logger.error(f"Orchestrator Error: {str(e)}")
#         return "Something went wrong."


# # -----------------------------
# # ✅ History Builder
# # -----------------------------
# def _build_history(history: List[Dict]) -> List:
#     messages = []
#     for msg in history:
#         if msg["role"] == "human":
#             messages.append(HumanMessage(content=msg["content"]))
#         elif msg["role"] == "ai":
#             messages.append(AIMessage(content=msg["content"]))
#     return messages

from core.llm import invoke_llm, build_history
from agents.research_agent import run_research_agent
from agents.writer_agent import run_writer_agent
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# ✅ System Prompt
# -----------------------------
ORCHESTRATOR_SYSTEM = """
You are an Orchestrator Agent.

Classify the user request into ONE category:

RESEARCH → facts, search, information
WRITE → create/save notes or content
CHAT → casual conversation

Rules:
- Answer with ONLY ONE WORD
- No explanation
- Just: RESEARCH or WRITE or CHAT
"""

# -----------------------------
# ✅ Agent Functions
# -----------------------------
def run_chat_agent(message: str, history: list):
    return invoke_llm(
        prompt=message,
        system="You are NanoClaw, a helpful AI assistant. Be concise.",
        history=history
    )

AGENTS = {
    "RESEARCH": run_research_agent,
    "WRITE": run_writer_agent,
    "CHAT": run_chat_agent
}

# -----------------------------
# ✅ Decide Agent
# -----------------------------
def decide_agent(message: str, history: list) -> str:
    try:
        response = invoke_llm(
            prompt=message,
            system=ORCHESTRATOR_SYSTEM,
            history=history
        )

        decision = response.strip().upper()
        logger.info(f"Raw Decision: {decision}")

        # ✅ Strong filtering
        if "RESEARCH" in decision:
            return "RESEARCH"
        elif "WRITE" in decision:
            return "WRITE"
        elif "CHAT" in decision:
            return "CHAT"

        return "CHAT"

    except Exception as e:
        logger.error(f"Decision error: {str(e)}")
        return "CHAT"

# -----------------------------
# ✅ Main Orchestrator
# -----------------------------
def run_orchestrator(message: str, history: list = None):
    if history is None:
        history = []

    try:
        decision = decide_agent(message, history)
        logger.info(f"Routing → {decision}")

        agent_fn = AGENTS.get(decision, run_chat_agent)

        if decision == "WRITE":
            return agent_fn(message, filename="note", history=history)

        return agent_fn(message, history)

    except Exception as e:
        logger.error(f"Orchestrator error: {str(e)}")
        return "Something went wrong."