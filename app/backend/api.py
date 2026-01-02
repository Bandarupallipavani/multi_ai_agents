from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import List
from app.core.ai_agents import get_response_from_ai_agents
from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from typing import List, Dict

logger = get_logger(__name__)

app = FastAPI(title="MULTI AI AGENT")

class RequestState(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[Dict[str, str]]   
    allow_search: bool = False

@app.post("/chat")
def chat_endpoint(request:RequestState):
    logger.info(f"Received request for model : {request.model_name}")

    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")

    try:
        response = get_response_from_ai_agents(
            llm_id=request.model_name,
            messages=request.messages,
            allow_search=request.allow_search,
            system_prompt=request.system_prompt
        )

        return {"response": response}

    except Exception as e:
        logger.exception("Backend error")
        raise HTTPException(status_code=500, detail=str(e))

