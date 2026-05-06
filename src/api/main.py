"""FastAPI backend for Job Research Agent."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from src.graph.workflow import run_research
from src.config import settings
from src.storage import session_repo, report_repo, message_repo
from src.storage.qdrant_client import get_qdrant_client
from src.conversation import generate_response, intent_detector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Job Research Agent API",
    description="Multi-Agent AI system for job research",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Request/Response Models ==============

class ResearchRequest(BaseModel):
    """Request model for research endpoint."""
    company: str = Field(..., min_length=1, description="Target company name")
    position: str = Field(..., min_length=1, description="Target position")
    session_id: Optional[str] = Field(None, description="Optional existing session ID")


class ResearchResponse(BaseModel):
    """Response model for research endpoint."""
    session_id: str
    report: str
    quality_score: float
    research_plan_count: int
    rewrite_count: int
    messages: list[str]


class DialogueRequest(BaseModel):
    """Request model for dialogue endpoint."""
    query: str = Field(..., min_length=1, description="User's question")
    session_id: str = Field(..., description="Session ID for context")


class DialogueResponse(BaseModel):
    """Response model for dialogue endpoint."""
    message_id: str
    answer: str
    source: Optional[str] = None


class SessionResponse(BaseModel):
    """Response model for session info."""
    id: str
    company: str
    position: str
    report_count: int
    message_count: int
    created_at: str


# ============== Research Endpoint ==============

@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest) -> ResearchResponse:
    """Run research workflow for a company and position.

    Creates a new session or continues existing one.
    """
    try:
        # Determine if new session or existing
        session = None
        if request.session_id:
            session = session_repo.get(request.session_id)

        if not session:
            # Create new session
            session = session_repo.create(request.company, request.position)
            logger.info(f"Created new session: {session.id}")

        logger.info(f"Starting research for {request.company} - {request.position}")

        # Run research workflow
        result = await run_research(request.company, request.position)
        result_dict = dict(result) if hasattr(result, '__iter__') else result

        # Save report
        report = report_repo.create(
            session_id=session.id,
            content=result_dict.get('final_report') or result_dict.get('draft_report', ''),
            quality_score=result_dict.get('quality_score', 0),
            research_plan=[str(p) for p in result_dict.get('research_plan', [])],
            research_results=result_dict.get('research_results', {}),
        )
        session_repo.add_report(session.id, report.id)

        # Index report to Qdrant for RAG
        try:
            qdrant_client = get_qdrant_client()
            await qdrant_client.index_report(
                report_id=report.id,
                session_id=session.id,
                company=request.company,
                position=request.position,
                content=report.content,
            )
            logger.info(f"Report indexed to Qdrant: {report.id}")
        except Exception as e:
            logger.warning(f"Failed to index report to Qdrant: {e}")

        logger.info(f"Research completed. Score: {report.quality_score}")

        return ResearchResponse(
            session_id=session.id,
            report=report.content,
            quality_score=report.quality_score,
            research_plan_count=len(report.research_plan),
            rewrite_count=result_dict.get('rewrite_count', 0),
            messages=result_dict.get('messages', []),
        )

    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Dialogue Endpoint ==============

@app.post("/dialogue", response_model=DialogueResponse)
async def dialogue(request: DialogueRequest) -> DialogueResponse:
    """Continue conversation about a research report."""
    try:
        # Verify session exists
        session = session_repo.get(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Detect intent
        intent = intent_detector.detect(request.query)

        if intent.type == "new_research":
            # If user asks for new research in dialogue, redirect
            raise HTTPException(
                status_code=400,
                detail="请使用 /research 端点开启新研究"
            )

        # Save user message
        user_msg = message_repo.create(
            session_id=request.session_id,
            role="user",
            content=request.query,
        )
        session_repo.add_message(session.id, user_msg.id)

        # Generate response
        result = await generate_response(request.query, request.session_id)

        # Save assistant message
        assistant_msg = message_repo.create(
            session_id=request.session_id,
            role="assistant",
            content=result["answer"],
        )
        session_repo.add_message(session.id, assistant_msg.id)

        return DialogueResponse(
            message_id=assistant_msg.id,
            answer=result["answer"],
            source=result.get("source"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dialogue failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Session Endpoints ==============

@app.get("/sessions", response_model=list[SessionResponse])
async def list_sessions() -> list[SessionResponse]:
    """List all research sessions."""
    sessions = session_repo.list_all()
    return [
        SessionResponse(
            id=s.id,
            company=s.company,
            position=s.position,
            report_count=len(s.report_ids),
            message_count=len(s.message_ids),
            created_at=s.created_at.isoformat(),
        )
        for s in sessions
    ]


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """Get session details."""
    session = session_repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=session.id,
        company=session.company,
        position=session.position,
        report_count=len(session.report_ids),
        message_count=len(session.message_ids),
        created_at=session.created_at.isoformat(),
    )


@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 50):
    """Get conversation history for a session."""
    session = session_repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = message_repo.list_by_session(session_id, limit=limit)
    return {
        "session_id": session_id,
        "messages": [msg.to_dict() for msg in messages],
    }


@app.get("/sessions/{session_id}/reports")
async def get_session_reports(session_id: str):
    """Get all reports for a session."""
    session = session_repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    reports = report_repo.list_by_session(session_id)
    return {
        "session_id": session_id,
        "reports": [r.to_dict() for r in reports],
    }


# ============== Health Check ==============

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )