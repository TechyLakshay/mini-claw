# from langchain_community.chat_models import ChatOllama
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.messages import HumanMessage, AIMessage
# # from langchain_anthropic import ChatAnthropic
# from dotenv import load_dotenv
# import os
# import logging

# logging.basicConfig(level=logging.INFO)

# logger = logging.getLogger(__name__)


# load_dotenv()

# # -----------------------------
# # ✅ LLM
# # -----------------------------
# def get_llm():
#     try:
#         logger.info("initializing LLM...")
#         return ChatOllama(
#             base_url=os.getenv("OLLAMA_BASE_URL"),
#             model=os.getenv("MODEL_NAME")
#         )
#     except Exception as e:
#         raise RuntimeError(f"LLM init failed: {e}")

# # def get_llm():
# #     try:
# #         logger.info("initializing LLM...")
# #         return ChatAnthropic(
# #             model=os.getenv("MODEL_NAME"),
# #             anthropic_api_key=os.getenv("CLAUDE_API_KEY")
# #         )
# #     except Exception as e:
# #         raise RuntimeError(f"LLM init failed: {e}")


# # -----------------------------
# # ✅ Dynamic Prompt Template
# # -----------------------------
# def get_prompt_template(system: str):
#     return ChatPromptTemplate.from_messages([
#         ("system", system),
#         MessagesPlaceholder(variable_name="history"),
#         ("human", "{input}")
#     ])


# # -----------------------------
# # ✅ History Builder
# # -----------------------------
# def build_history(history: list) -> list:
#     messages = []

#     for msg in history:
#         content = str(msg.get("content", ""))  # 🔥 force string

#         if msg["role"] == "human":
#             messages.append(HumanMessage(content=content))
#         elif msg["role"] == "ai":
#             messages.append(AIMessage(content=content))

#     return messages


# # -----------------------------
# # ✅ LLM Invocation
# # -----------------------------
# def invoke_llm(prompt: str, system: str, history: list = None) -> str:
#     try:
#         if history is None:
#             history = []

#         llm = get_llm()
#         prompt_template = get_prompt_template(system)

#         chain = prompt_template | llm

#         response = chain.invoke({
#             "history": build_history(history),
#             "input": str(prompt)
#         })

#         return response.content

#     except Exception as e:
#         return f"Error: {str(e)}"
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.messages import HumanMessage, AIMessage
from typing import AsyncIterator, List, Dict, Optional
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)


def get_llm() -> ChatOllama:
    """
    Initialize and return ChatOllama instance.
    Settings loaded from central config.
    """
    settings = get_settings()
    try:
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.model_name
        )
    except Exception as e:
        logger.error(f"LLM init failed: {e}")
        raise RuntimeError(f"LLM init failed: {e}")


def get_prompt_template(system: str) -> ChatPromptTemplate:
    """
    Build a dynamic ChatPromptTemplate with system prompt + history + user input.
    
    Args:
        system: System prompt string for the agent.
    
    Returns:
        ChatPromptTemplate with MessagesPlaceholder for history.
    """
    return ChatPromptTemplate.from_messages([
        ("system", system),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])


def build_history(history: List[Dict]) -> List:
    """
    Convert raw history dicts from Supabase into LangChain message objects.
    Skips any malformed or empty messages silently.
    
    Args:
        history: List of dicts with 'role' and 'content' keys.
    
    Returns:
        List of HumanMessage / AIMessage objects.
    """
    messages = []
    for msg in history:
        try:
            content = msg.get("content", "")
            if not isinstance(content, str):
                content = str(content)
            if not content.strip():
                continue
            if msg["role"] == "human":
                messages.append(HumanMessage(content=content))
            elif msg["role"] == "ai":
                messages.append(AIMessage(content=content))
        except Exception:
            continue
    return messages


def invoke_llm(
    prompt: str,
    system: str,
    history: Optional[List[Dict]] = None
) -> str:
    """
    Invoke LLM with prompt, system message, and conversation history.
    
    Args:
        prompt: User's current message.
        system: System prompt for this specific agent.
        history: Previous conversation history.
    
    Returns:
        LLM response as string.
    """
    if history is None:
        history = []

    try:
        llm = get_llm()
        prompt_template = get_prompt_template(system)
        chain = prompt_template | llm

        response = chain.invoke({
            "history": build_history(history),
            "input": str(prompt)
        })

        return response.content

    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        return f"Error: {str(e)}"


async def stream_llm(
    prompt: str,
    system: str,
    history: Optional[List[Dict]] = None
) -> AsyncIterator[str]:
    """
    Stream LLM response chunk by chunk.
    Use this for Telegram streaming / typing effect.
    
    Args:
        prompt: User's current message.
        system: System prompt for this specific agent.
        history: Previous conversation history.
    
    Yields:
        String chunks as they arrive from Ollama.
    """
    if history is None:
        history = []

    try:
        llm = get_llm()
        prompt_template = get_prompt_template(system)
        chain = prompt_template | llm

        async for chunk in chain.astream({
            "history": build_history(history),
            "input": str(prompt)
        }):
            if chunk.content:
                yield chunk.content

    except Exception as e:
        logger.error(f"LLM streaming failed: {e}")
        yield f"Error: {str(e)}"