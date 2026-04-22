from langchain.messages import AIMessage, HumanMessage

from core.llm import get_llm, get_prompt_template
from tools.file_writer import write_file


def run_writer_tool(content: str, filename: str = "note", history: list | None = None) -> str:
    try:
        prompt_template = get_prompt_template(
            system="""You are a writer tool.
Structure and format content clearly into well-written markdown.
Use headings and bullet points only when they improve readability.
Be concise but complete.""",
        )

        llm = get_llm()
        chain = prompt_template | llm

        response = chain.invoke(
            {
                "history": _build_history(history or []),
                "input": f"Format and structure this content into clean markdown:\n\n{content}",
            }
        )

        formatted_content = response.content
        file_status = write_file(filename, formatted_content)

        return f"{formatted_content}\n\n---\n{file_status}"
    except Exception as exc:
        return f"Writer tool failed: {str(exc)}"


def _build_history(history: list) -> list:
    messages = []

    for msg in history:
        if msg["role"] == "human":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            messages.append(AIMessage(content=msg["content"]))

    return messages
