import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="CRM AI Agent Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "CRM AI Agent Platform Backend running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Minimal AI agent simulate endpoint (no external LLMs; just echoes with persona prefix)
class ChatRequest(BaseModel):
    agent_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    reply: str


@app.post("/api/agent/chat", response_model=ChatResponse)
async def agent_chat(body: ChatRequest):
    persona_prefix = "Agent"

    # Try to fetch agent persona if id provided
    if body.agent_id and db is not None:
        try:
            agent = db["agent"].find_one({"_id": ObjectId(body.agent_id)})
            if agent and agent.get("persona"):
                persona_prefix = agent["persona"][:60]
        except Exception:
            pass

    reply = f"{persona_prefix}: I received your message — '{body.message}'. How can I help further?"
    return ChatResponse(reply=reply)


# Lightweight CRUD helpers for key CRM entities (list and create)
class CreateAgent(BaseModel):
    name: str
    role: Optional[str] = "AI Agent"
    channel: Optional[str] = "omni"
    model_hint: Optional[str] = None
    persona: Optional[str] = None
    active: bool = True


@app.get("/api/agents")
async def list_agents(limit: int = 50):
    try:
        docs = get_documents("agent", {}, limit)
        # Convert ObjectId to string
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents")
async def create_agent(agent: CreateAgent):
    try:
        insert_id = create_document("agent", agent.model_dump())
        return {"id": insert_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateContact(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None


@app.get("/api/contacts")
async def list_contacts(limit: int = 50):
    try:
        docs = get_documents("contact", {}, limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/contacts")
async def create_contact(contact: CreateContact):
    try:
        insert_id = create_document("contact", contact.model_dump())
        return {"id": insert_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
