# AGENTS

Current agents in this project:

- Orchestrator: routes a request to chat, research, or writer
- Research Agent: uses web search results and summarizes them
- Writer Agent: formats content and saves it to a markdown file
- Chat Agent: answers directly with the model

Rules:
- use only agents that actually exist in the codebase
- do not mention planned agents as available
- route based on the user's request, not imagination
