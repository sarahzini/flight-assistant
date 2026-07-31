from fastapi import APIRouter

from app.models import AdvisorAnswer, AdvisorQuery
from app.services.rag_service import answer_question

router = APIRouter(prefix="/advisor", tags=["queries:advisor"])


@router.post("")
def ask_advisor(request: AdvisorQuery) -> AdvisorAnswer:
    """Ask the AI advisor a question, answered using RAG over the aviation knowledge base."""
    answer, sources = answer_question(request.question)
    return AdvisorAnswer(answer=answer, sources=sources)