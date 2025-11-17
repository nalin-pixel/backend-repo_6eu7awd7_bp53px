"""
Database Schemas for CRM AI Agent Platform

Each Pydantic model maps to a MongoDB collection (lowercased class name).
Examples:
- Agent -> "agent"
- Contact -> "contact"
- Conversation -> "conversation"

These schemas are used by the Flames database viewer and by the backend
for validation when creating documents.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr

# Core CRM entities

class Agent(BaseModel):
    name: str = Field(..., description="Agent display name")
    role: str = Field("AI Agent", description="Role or title")
    channel: Literal["voice", "chat", "email", "omni"] = Field(
        "omni", description="Primary support channel"
    )
    model_hint: Optional[str] = Field(None, description="LLM or provider hint")
    persona: Optional[str] = Field(None, description="System prompt / persona notes")
    active: bool = Field(True, description="Whether the agent is active")

class Company(BaseModel):
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = Field(None, description="Company size segment")
    notes: Optional[str] = None

class Contact(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    company_id: Optional[str] = Field(None, description="Reference to company _id")
    status: Literal["lead", "prospect", "customer"] = "lead"
    owner_id: Optional[str] = Field(None, description="Assigned agent or user id")
    tags: List[str] = []
    notes: Optional[str] = None

class Deal(BaseModel):
    title: str
    amount: float = 0.0
    stage: Literal["new", "qualified", "proposal", "won", "lost"] = "new"
    contact_id: Optional[str] = None
    company_id: Optional[str] = None
    owner_id: Optional[str] = None

class Task(BaseModel):
    title: str
    due_date: Optional[str] = None
    status: Literal["open", "in_progress", "done"] = "open"
    contact_id: Optional[str] = None
    owner_id: Optional[str] = None
    notes: Optional[str] = None

# Conversational entities

class Conversation(BaseModel):
    agent_id: Optional[str] = None
    contact_id: Optional[str] = None
    channel: Literal["voice", "chat", "email"] = "chat"
    topic: Optional[str] = None
    status: Literal["open", "closed", "pending"] = "open"

class Message(BaseModel):
    conversation_id: str
    sender: Literal["agent", "contact", "system"] = "contact"
    text: str
    meta: Optional[dict] = None

class Knowledge(BaseModel):
    title: str
    content: str
    tags: List[str] = []

# Keep example schemas below for reference if needed by viewer
class User(BaseModel):
    name: str
    email: EmailStr
    address: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
