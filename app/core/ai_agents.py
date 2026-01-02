from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from app.common.logger import get_logger
from app.config.settings import settings

logger = get_logger(__name__)

def get_response_from_ai_agents(
    llm_id: str,
    messages: list,
    allow_search: bool,
    system_prompt: str
):
    if not messages:
        raise ValueError("Messages list is empty")

    llm = ChatGroq(
        model=llm_id,
        api_key=settings.GROQ_API_KEY,
        temperature=0.2
    )

    chat_messages = []

    # System prompt
    if system_prompt:
        chat_messages.append(SystemMessage(content=system_prompt))

    # Get last user message safely
    last_user_message = None
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_message = msg["content"]
            break

    # Optional web search
    if allow_search and last_user_message:
        search = TavilySearchResults(max_results=2)
        results = search.invoke(last_user_message)
        chat_messages.append(
            SystemMessage(
                content=f"Use the following web search results if helpful:\n{results}"
            )
        )

    # Add conversation history
    for msg in messages:
        if msg["role"] == "user":
            chat_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_messages.append(AIMessage(content=msg["content"]))

    logger.info("Calling Groq LLM with memory")

    response = llm.invoke(chat_messages)
    content = response.content.strip()

    # Force bullet points if model responds in paragraph
    if not content.startswith("-"):
        lines = []
        for sentence in content.split(". "):
            sentence = sentence.strip()
            if sentence:
                lines.append(f"- {sentence}")
        content = "\n".join(lines)

    return content