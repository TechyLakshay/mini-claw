from langchain.messages import AIMessage, HumanMessage

from core.llm import get_llm, get_prompt_template
from tools.web_search import web_search


def run_research_tool(query: str, history: list | None = None) -> str:
    try:
        search_results = web_search(query)

        prompt_template = get_prompt_template(
            system="""You are a research tool.
Analyze the search results and provide a clear, concise, accurate summary.
Always cite the sources you used.
If the search results are not relevant, say so clearly.
Do not make up information that is not present in the results.""",
        )

        llm = get_llm()
        chain = prompt_template | llm

        response = chain.invoke(
            {
                "history": _build_history(history or []),
                "input": f"User query: {query}\n\nSearch Results:\n{search_results}",
            }
        )

        return response.content
    except Exception as exc:
        return f"Research tool failed: {str(exc)}"


def _build_history(history: list) -> list:
    messages = []

    for msg in history:
        if msg["role"] == "human":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            messages.append(AIMessage(content=msg["content"]))

    return messages
