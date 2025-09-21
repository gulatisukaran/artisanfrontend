#!/usr/bin/env python3
"""
Advanced Agentic FastAPI Application
A complete single-file FastAPI app with LangGraph workflows, user onboarding, and frontend integration.
"""

import os
import json
import base64
import asyncio
import sqlite3
import re
import traceback
from datetime import datetime
from typing import TypedDict, List, Dict, Optional, Any
from uuid import uuid4

# FastAPI & Web Framework Imports
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
from pydantic import BaseModel
import uvicorn

# Environment & Config
from dotenv import load_dotenv

# LangChain & LangGraph Imports
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
# Removed GenAITool import; using ChatVertexAI.bind_tools for tool bindings
from google import genai
from google.genai import types, errors as genai_errors

# =======================
# 1. CONFIGURATION SETUP
# =======================

load_dotenv()

# Validate required environment variables

# =======================
# 2. FASTAPI APP SETUP
# =======================

app = FastAPI(
    title="Assistant",
    version="2.0.0"
)

# Enable CORS for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# 3. PYDANTIC MODELS
# =======================

class ChatMessage(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    is_onboarding: bool = False
    onboarding_step: Optional[int] = None
    user_profile: Optional[Dict[str, str]] = None
    backstory: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    name: Optional[str] = None
    state: Optional[str] = None
    # Artisan-focused fields
    craft_type: Optional[str] = None
    materials: Optional[str] = None
    years_experience: Optional[str] = None
    sales_channels: Optional[str] = None  # online/offline/both
    price_range: Optional[str] = None
    languages: Optional[str] = None
    brand_style: Optional[str] = None
    backstory: Optional[str] = None

class NotificationResponse(BaseModel):
    user_id: str
    notifications: List[Dict[str, str]]
    total_schemes: int

# =======================
# 4. LANGGRAPH STATE DEFINITION
# =======================

class AgentState(TypedDict):
    """Enhanced state for the agentic workflow."""
    messages: List[BaseMessage]
    user_id: str
    # Onboarding-specific state
    is_onboarding: bool
    onboarding_step: int
    user_profile_data: Dict[str, str]
    # Transient data for a single run
    intent: str
    tool_output: Optional[str]
    final_response_text: str
    # Additional metadata
    timestamp: str
    session_id: str

# =======================
# 4.5. UTILS
# =======================

def sanitize_profile(profile: Optional[Dict]) -> Dict:
    """Return a copy of the profile safe for prompting (excludes large/verbose fields like backstory)."""
    if not profile:
        return {}
    return {k: v for k, v in profile.items() if k.lower() != "backstory"}

def coerce_profile_to_strings(profile: Optional[Dict]) -> Dict[str, str]:
    """For API responses, ensure all values are strings and drop Nones to satisfy Dict[str, str]."""
    if not profile:
        return {}
    result: Dict[str, str] = {}
    for k, v in profile.items():
        if v is None:
            continue
        try:
            result[k] = v if isinstance(v, str) else str(v)
        except Exception:
            # As a last resort, skip values that cannot be stringified
            continue
    return result

# =======================
# 5. WORKFLOW NODES (MOVED BEFORE WORKFLOW CONSTRUCTION)
# =======================

def check_user_profile_node(state: AgentState) -> dict:
    """Checks if a user profile exists and sets initial state, preserving partial data."""
    user_id = state.get('user_id')
    if not user_id:
        return {"error": "User ID not found in state"}

    # Check for a completed profile in SQLite
    try:
        stored_profile = services.store.get_user_profile(user_id)
        profile_exists = stored_profile is not None
    except Exception as e:
        print(f"Error accessing store: {e}")
        profile_exists = False
    
    print(f"Profile check for user {user_id}: exists = {profile_exists}")
    
    if profile_exists and stored_profile:
        # Profile is complete, onboarding is done.
        return {
            "user_id": user_id,
            "is_onboarding": False,
            "user_profile_data": stored_profile,
            "messages": state.get('messages', [])
        }
    else:
        # No completed profile. We are in onboarding.
        partial_profile = state.get('user_profile_data', {})
        print(f"Onboarding active. Current partial profile: {partial_profile}")
        
        # Check if this is a completely new user (no messages yet)
        messages = state.get('messages', [])
        is_new_user = len([msg for msg in messages if isinstance(msg, HumanMessage)]) <= 1 and not partial_profile
        
        if is_new_user:
            welcome_message = "Welcome! I'm your artisan brand assistant. I'll help you set up your craft profile, craft a compelling backstory, and support your content. Let's start simple — what should I call you or your brand?"
            return {
                "user_id": user_id,
                "is_onboarding": True,
                "user_profile_data": partial_profile,
                "messages": messages + [AIMessage(content=welcome_message)],
                "final_response_text": welcome_message
            }
        
        return {
            "user_id": user_id,
            "is_onboarding": True,
            "user_profile_data": partial_profile,
            "messages": state.get('messages', [])
        }

def onboarding_step_node(state: AgentState) -> dict:
    """Handles interactive user onboarding for artisan profiling and setup."""
    if not state.get('is_onboarding'):
        return {"is_onboarding": False}

    current_profile = state.get('user_profile_data', {})
    user_id = state['user_id']
    messages = state.get('messages', [])
    
    # Define artisan-specific fields
    required_fields = [
        "name",
        "state",
        "craft_type",
        "materials",
        "years_experience",
        "sales_channels",
        "price_range",
        "languages",
        "brand_style"
    ]
    
    # Get the most recent human message if available (welcome AI message may be last)
    user_message = ""
    if messages:
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                user_message = m.content
                break
        
    extraction_prompt = ChatPromptTemplate.from_template("""
You are an expert data extractor for an Indian artisan platform. Your goal is to intelligently extract profile information from user messages. Users may respond in English, Hindi, Hinglish, or other regional languages.

Your instructions are to be flexible, understand the intent behind the words, and not fail due to minor spelling errors or variations in phrasing. Return ONLY a JSON object with the extracted data.

Current profile: {current_profile}
User message: {user_message}
Missing fields: {missing_fields}

Fields to Extract (with examples)

Extract these fields if they are mentioned. Recognize both English and common Indian language equivalents.

    name: Full name or shop name.

        e.g., "Mera naam Priya hai," "My shop is called Kala Creations."

    state: Indian state/UT. Infer from any city mentioned.

        e.g., "Main Jaipur se hoon" -> Rajasthan, "I live in Kolkata" -> West Bengal.

    craft_type: The primary craft.

        e.g., pottery (mitti ka kaam), weaving (bunaai), embroidery (kadai), woodwork (lakdi ka kaam), handicrafts.

    materials: Main materials used.

        e.g., clay (mitti), cotton (sooti/kapda), wood (lakdi), brass (peetal), silk (resham).

    years_experience: Years of practice. Extract the number.

        e.g., "dus saal ka anubhav hai" -> 10, "I've been doing this for 5 years." -> 5

    sales_channels: Where they sell their products.

        e.g., Instagram, Etsy, fairs (mela), local markets (bazaar), exhibitions, online, offline.

    price_range: Typical price for their items.

        e.g., "500 rupaye tak," "around 200-500," "premium price."

    languages: Languages the user speaks.

        e.g., "Hindi aur thodi English," "I speak Bengali and Hindi."

    brand_style: The feel or voice of their brand.

        e.g., earthy (zameen se juda), minimalist, premium, traditional (paramparik), vibrant (rangeen).

Behavior and Normalization Rules

    Language-Agnostic: The user's message can be in any common Indian language or a mix (Hinglish). Your primary task is to understand and extract the data regardless of the language.

    Semantic Matching: Do not depend on exact keywords. Understand the meaning.

        If the user mentions "mela," "bazaar," or "exhibition," normalize sales_channels to offline.

        If they mention "Instagram," "website," or "Etsy," normalize sales_channels to online.

        If they mention both, use both.

    Flexible Number Extraction: For years_experience, recognize numbers written as words (e.g., "paanch saal" -> 5, "do saal" -> 2).

    Tolerate Typos: Be forgiving of common spelling mistakes (e.g., "jwellery," "embrodery").

    Multi-field Extraction: If a user provides multiple pieces of information in one sentence (e.g., "Main Ravi, UP se, aur lakdi ka kaam karta hoon 10 saal se"), extract name, state, craft_type, and years_experience all at once.
 Only use strings dont make any dictionary or list.
Return a valid JSON object only. If no new information is found, return {{}} if nothing found.
""")
        
    missing_fields_for_prompt = [field for field in required_fields if field not in current_profile]

    extraction_chain = extraction_prompt | services.llm_gemini.bind_tools([{"google_search": {}}]) | StrOutputParser()

    # Only attempt extraction if we have a human message
    if user_message:
        try:
            response_str = extraction_chain.invoke({
                "current_profile": json.dumps(sanitize_profile(current_profile)),
                "user_message": user_message,
                "missing_fields": json.dumps(missing_fields_for_prompt)
            })

            # Clean and parse the JSON response
            json_match = re.search(r'\{.*\}', response_str, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                current_profile.update(extracted_data)
                print(f"Extracted profile data: {extracted_data}")
            else:
                # Fallback: Try to extract simple responses manually for years_experience
                user_message_lower = user_message.lower().strip()
                if len(missing_fields_for_prompt) > 0 and missing_fields_for_prompt[0] == 'years_experience':
                    numbers = re.findall(r'\d+', user_message)
                    if numbers:
                        current_profile['years_experience'] = numbers[0]
                        print(f"Fallback: Extracted years_experience = {numbers[0]}")
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error extracting profile data: {e}")
            # Final fallback for simple responses when we do have a user message
            if user_message:
                if len(missing_fields_for_prompt) > 0:
                    next_field = missing_fields_for_prompt[0]
                    if next_field == 'years_experience':
                        numbers = re.findall(r'\d+', user_message)
                        if numbers:
                            current_profile['years_experience'] = numbers[0]
                            print(f"Final fallback: years_experience = {numbers[0]}")

    # Check what's still missing
    missing_fields = [field for field in required_fields if field not in current_profile or not current_profile[field]]
    
    # If nothing is missing, onboarding is complete
    if not missing_fields:
        services.store.save_user_profile(user_id, current_profile)
        name = current_profile.get('name', 'there')
        final_text = f"Great! {name}, your artisan profile is set."

        # Auto-generate backstory once if not already present
        try:
            stored = services.store.get_user_profile(user_id) or {}
            existing_backstory = stored.get('backstory')
        except Exception:
            existing_backstory = None

        backstory_text = None
        if not existing_backstory:
            backstory_prompt = ChatPromptTemplate.from_template(
                """
You are a brand storyteller. Create a compelling artisan backstory.

Details:
Name/Brand: {name}
State/Region: {state}
Craft: {craft}
Materials: {materials}
Experience (years): {years}
Sales Channels: {channels}
Brand Style: {style}
Languages: {languages}

Write in simple, sincere language. Avoid clichés and marketing fluff.
Output exactly one sections in this format (no extra text):



"""
            )
            chain = backstory_prompt | services.llm_gemini.bind_tools([{"google_search": {}}]) | StrOutputParser()
            try:
                raw_backstory = chain.invoke({
                    "name": current_profile.get('name', ''),
                    "state": current_profile.get('state', ''),
                    "craft": current_profile.get('craft_type', ''),
                    "materials": current_profile.get('materials', ''),
                    "years": current_profile.get('years_experience', ''),
                    "channels": current_profile.get('sales_channels', ''),
                    "style": current_profile.get('brand_style', ''),
                    "languages": current_profile.get('languages', ''),
                }).strip()

                # Parse into Backstory and Tagline if possible
                bs_match = re.search(r"Backstory:\s*(.+?)(?:\n\s*Tagline:|$)", raw_backstory, re.DOTALL | re.IGNORECASE)
                tl_match = re.search(r"Tagline:\s*(.+)$", raw_backstory, re.DOTALL | re.IGNORECASE)
                backstory_section = bs_match.group(1).strip() if bs_match else raw_backstory
                tagline_section = tl_match.group(1).strip() if tl_match else ""

                # Store backstory (including tagline at the end for convenience)
                backstory_text = backstory_section + (f"\n\nTagline: {tagline_section}" if tagline_section else "")
                services.store.save_backstory(user_id, backstory_text)
                final_text = final_text + " I've also crafted your brand backstory. You can fetch it anytime."
            except Exception as e:
                print(f"Backstory generation failed: {e}")
                backstory_text = None

        return {
            "is_onboarding": False,
            "user_profile_data": current_profile,
            "messages": messages + [AIMessage(content=final_text)],
            "final_response_text": final_text,
            "backstory": backstory_text
        }
        
    # Ask for the next missing piece of information
    next_field_to_ask = missing_fields[0]
    
    # Field-specific prompts for artisans
    field_prompts = {
        "name": "What should I call your brand or what's your name?",
        "state": "Which state/region in India are you based in?",
        "craft_type": "What craft do you practice? (e.g., pottery, weaving, woodwork)",
        "materials": "What materials do you mostly use? (e.g., clay, cotton, bamboo)",
        "years_experience": "How many years have you been practicing this craft?",
        "sales_channels": "Where do you usually sell? Online, offline, or both?",
        "price_range": "What's your typical price range? (e.g., Rs 200-500, premium)",
        "languages": "Which languages do you speak or want content in?",
        "brand_style": "How would you describe your brand style or voice? (e.g., earthy, premium)"
    }
    
    next_question = field_prompts.get(next_field_to_ask, f"Please provide your {next_field_to_ask}")
    
    return {
        "is_onboarding": True,
        "user_profile_data": current_profile,
        "messages": messages + [AIMessage(content=next_question)],
        "final_response_text": next_question
    }

def supervisor_agent_node(state: AgentState) -> dict:
    """Smart intent classification for welfare scheme assistance."""
    user_id = state['user_id']
    
    # Get user profile safely
    try:
        user_profile = services.store.get_user_profile(user_id) or {}
    except:
        user_profile = {}
    
    prompt = ChatPromptTemplate.from_template("""
Classify user intent for welfare scheme assistance:

Intents:
- 'welfare_search': Questions about government schemes, benefits, eligibility
- 'general_query': Other questions

User Profile: {user_profile}
Query: {query}

Respond with intent only.
""")
    
    chain = prompt | services.llm_gemini.bind_tools([{"google_search": {}}]) | StrOutputParser()
    query = state['messages'][-1].content
    intent = chain.invoke({
        "user_profile": json.dumps(sanitize_profile(user_profile)), 
        "query": query
    }).strip().lower()
    
    # Map intent variations
    if "welfare" in intent or "scheme" in intent or "benefit" in intent:
        final_intent = "welfare_search"
    else:
        final_intent = "general_query"
        
    return {"intent": final_intent}

def welfare_search_node(state: AgentState) -> dict:
    """Concise welfare scheme search with user profile matching."""
    query = state['messages'][-1].content
    user_id = state['user_id']
    
    # Get user profile for targeted search
    try:
        user_profile = services.store.get_user_profile(user_id) or {}
    except:
        user_profile = {}
    
    # Create targeted search query
    search_context = ""
    if user_profile:
        sp = sanitize_profile(user_profile)
        search_context = f"Indian welfare schemes for {sp.get('state', '')} {sp.get('income_category', '')} {sp.get('occupation', '')}"
    
    try:
        search_results = services.web_search_tool.invoke({"query": f"{query} {search_context}"})
        
        # Create concise summary
        summary_prompt = ChatPromptTemplate.from_template("""
Provide a natural, conversational answer about welfare schemes based on search results.
Sound like you're speaking to someone naturally, without emojis or bullet points.
Keep response under 150 words and focus on practical information about eligibility and benefits.

User Profile: {profile}
Query: {query}
Search Results: {results}

Provide a helpful answer that sounds natural when spoken aloud.
""")
        
        summary_chain = summary_prompt | services.llm_gemini.bind_tools([{"google_search": {}}]) | StrOutputParser()
        concise_response = summary_chain.invoke({
            "profile": json.dumps(sanitize_profile(user_profile)),
            "query": query,
            "results": json.dumps(search_results[:3])  # Limit to top 3 results
        })
        
        return {"tool_output": concise_response}
    except Exception as e:
        return {"tool_output": f"Unable to search welfare schemes: {str(e)}"}

def general_query_node(state: AgentState) -> dict:
    """Handles concise conversational queries about welfare schemes."""
    user_id = state['user_id']
    
    # Get user profile safely
    try:
        user_profile = services.store.get_user_profile(user_id) or {}
    except:
        user_profile = {}
    
    prompt = ChatPromptTemplate.from_template("""
Answer naturally and conversationally, as if speaking to someone in person.
Remove all emojis, bullet points, and formatting. Keep response under 100 words.
Sound natural and helpful when spoken aloud.

User Profile: {user_profile}
Question: {question}

Provide a natural, spoken response focused on welfare schemes if relevant.
""")
    
    chain = prompt | services.llm_gemini.bind_tools([{"google_search": {}}]) | StrOutputParser()
    response = chain.invoke({
        "user_profile": json.dumps(sanitize_profile(user_profile)),
        "question": state['messages'][-1].content
    })
    
    return {"tool_output": response}

def final_response_node(state: AgentState) -> dict:
    """Creates natural, audio-friendly final responses."""
    tool_output = state.get('tool_output', '')
    
    # For form generation, keep the response natural
    if 'form' in tool_output.lower():
        final_text = tool_output
    else:
        # For other responses, ensure they're concise and natural
        prompt = ChatPromptTemplate.from_template("""
Make this response sound natural and conversational, as if speaking to someone.
Remove all emojis, bullet points, and technical formatting.
Keep it under 150 words and make it sound like natural speech:

{tool_output}

Make it friendly and helpful but natural for voice output.
""")
        
        chain = prompt | services.llm_gemini.bind_tools([{"google_search": {}}]) | StrOutputParser()
        final_text = chain.invoke({"tool_output": tool_output})
    
    return {
        "messages": [AIMessage(content=final_text)], 
        "final_response_text": final_text
    }

# =======================
# 6. WORKFLOW CONSTRUCTION
# =======================

def build_agentic_workflow(services_instance):
    """Builds and returns the optimized agentic workflow."""
    
    def route_after_checking_profile(state: AgentState):
        is_onboarding = state.get('is_onboarding', False)
        print(f"Route after profile check: is_onboarding = {is_onboarding}")
        return "onboarding_step" if is_onboarding else "supervisor"

    def route_after_supervisor(state: AgentState):
        intent = state.get('intent', 'general_query')
        print(f"Route after supervisor: intent = {intent}")
        return intent

    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("check_user_profile", check_user_profile_node)
    workflow.add_node("onboarding_step", onboarding_step_node)
    workflow.add_node("supervisor", supervisor_agent_node)
    workflow.add_node("welfare_search", welfare_search_node)
    workflow.add_node("general_query", general_query_node)
    workflow.add_node("structure_final_response", final_response_node)

    # Set entry point and edges
    workflow.set_entry_point("check_user_profile")
    
    workflow.add_conditional_edges(
        "check_user_profile",
        route_after_checking_profile,
        {
            "onboarding_step": "onboarding_step",
            "supervisor": "supervisor"
        }
    )
    
    # After asking an onboarding question, the turn ends. The "loop" is driven by user responses.
    workflow.add_edge("onboarding_step", END)
    
    workflow.add_conditional_edges(
        "supervisor", 
        route_after_supervisor,
        {
            "welfare_search": "welfare_search",
            "general_query": "general_query"
        }
    )
    
    workflow.add_edge("welfare_search", "structure_final_response")
    workflow.add_edge("general_query", "structure_final_response")
    workflow.add_edge("structure_final_response", END)

    return workflow.compile(checkpointer=services_instance.checkpointer)

# =======================
# 7. SQLITE PERSISTENCE LAYER
# =======================

class SQLiteStore:
    """SQLite-based persistent storage for user profiles and conversations."""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    state TEXT,
                    -- legacy fields (kept for compatibility)
                    age TEXT,
                    gender TEXT,
                    occupation TEXT,
                    income_category TEXT,
                    family_size TEXT,
                    has_disability TEXT,
                    -- artisan fields
                    craft_type TEXT,
                    materials TEXT,
                    years_experience TEXT,
                    sales_channels TEXT,
                    price_range TEXT,
                    languages TEXT,
                    brand_style TEXT,
                    backstory TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migrate existing DBs: add artisan columns if missing
            cursor.execute("PRAGMA table_info(user_profiles)")
            columns = [column[1] for column in cursor.fetchall()]
            migrations = {
                'state': "ALTER TABLE user_profiles ADD COLUMN state TEXT",
                'craft_type': "ALTER TABLE user_profiles ADD COLUMN craft_type TEXT",
                'materials': "ALTER TABLE user_profiles ADD COLUMN materials TEXT",
                'years_experience': "ALTER TABLE user_profiles ADD COLUMN years_experience TEXT",
                'sales_channels': "ALTER TABLE user_profiles ADD COLUMN sales_channels TEXT",
                'price_range': "ALTER TABLE user_profiles ADD COLUMN price_range TEXT",
                'languages': "ALTER TABLE user_profiles ADD COLUMN languages TEXT",
                'brand_style': "ALTER TABLE user_profiles ADD COLUMN brand_style TEXT",
                'backstory': "ALTER TABLE user_profiles ADD COLUMN backstory TEXT",
                'gender': "ALTER TABLE user_profiles ADD COLUMN gender TEXT"
            }
            for col, stmt in migrations.items():
                if col not in columns:
                    try:
                        cursor.execute(stmt)
                        print(f"Added {col} column to existing user_profiles table")
                    except Exception as e:
                        print(f"Column migration for {col} skipped/failed: {e}")
            
            # Conversation history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    message_type TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            # Welfare schemes table for reference
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS welfare_schemes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scheme_name TEXT,
                    category TEXT,
                    eligibility_criteria TEXT,
                    benefits TEXT,
                    application_process TEXT,
                    required_documents TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User generated media table: stores multiple images and captions per user
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_generated_media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    description TEXT,
                    prompt_used TEXT,
                    model_used TEXT,
                    original_image_path TEXT,
                    edited_image_path TEXT,
                    edited_image_blob BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            conn.commit()
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Retrieve user profile from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def save_user_profile(self, user_id: str, profile_data: Dict) -> None:
        """Save or update user profile in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if profile exists
            existing = self.get_user_profile(user_id)
            
            if existing:
                # Update existing profile
                cursor.execute("""
                    UPDATE user_profiles 
                    SET name = ?, state = ?,
                        age = ?, gender = ?, occupation = ?, income_category = ?, family_size = ?, has_disability = ?,
                        craft_type = ?, materials = ?, years_experience = ?, sales_channels = ?, price_range = ?, languages = ?, brand_style = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (
                    profile_data.get('name'),
                    profile_data.get('state'),
                    profile_data.get('age'),
                    profile_data.get('gender'),
                    profile_data.get('occupation'),
                    profile_data.get('income_category'),
                    profile_data.get('family_size'),
                    profile_data.get('has_disability'),
                    profile_data.get('craft_type'),
                    profile_data.get('materials'),
                    profile_data.get('years_experience'),
                    profile_data.get('sales_channels'),
                    profile_data.get('price_range'),
                    profile_data.get('languages'),
                    profile_data.get('brand_style'),
                    user_id
                ))
            else:
                # Insert new profile
                cursor.execute("""
                    INSERT INTO user_profiles 
                    (user_id, name, state, age, gender, occupation, income_category, family_size, has_disability,
                     craft_type, materials, years_experience, sales_channels, price_range, languages, brand_style)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    profile_data.get('name'),
                    profile_data.get('state'),
                    profile_data.get('age'),
                    profile_data.get('gender'),
                    profile_data.get('occupation'),
                    profile_data.get('income_category'),
                    profile_data.get('family_size'),
                    profile_data.get('has_disability'),
                    profile_data.get('craft_type'),
                    profile_data.get('materials'),
                    profile_data.get('years_experience'),
                    profile_data.get('sales_channels'),
                    profile_data.get('price_range'),
                    profile_data.get('languages'),
                    profile_data.get('brand_style')
                ))
            
            conn.commit()

    def save_backstory(self, user_id: str, backstory_text: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_profiles SET backstory = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?
            """, (backstory_text, user_id))
            conn.commit()
    
    def delete_user_profile(self, user_id: str) -> None:
        """Delete user profile from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            conn.commit()
    
    def save_conversation_message(self, user_id: str, message_type: str, content: str) -> None:
        """Save conversation message to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (user_id, message_type, content)
                VALUES (?, ?, ?)
            """, (user_id, message_type, content))
            conn.commit()
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message_type, content, timestamp 
                FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def save_generated_media(
        self,
        user_id: str,
        description: Optional[str],
        prompt_used: Optional[str],
        model_used: Optional[str],
        original_image_path: Optional[str],
        edited_image_path: Optional[str],
        edited_image_blob: Optional[bytes],
    ) -> int:
        """Persist a generated media record and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_generated_media (
                    user_id, description, prompt_used, model_used,
                    original_image_path, edited_image_path, edited_image_blob
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    description,
                    prompt_used,
                    model_used,
                    original_image_path,
                    edited_image_path,
                    edited_image_blob,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_user_media(self, user_id: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, description, prompt_used, model_used,
                       original_image_path, edited_image_path, edited_image_blob, created_at
                FROM user_generated_media
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def get_all_db_entries(self) -> Dict[str, List[Dict]]:
        """Return a dump of all main tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            result: Dict[str, List[Dict]] = {}
            for table in [
                "user_profiles",
                "conversations",
                "welfare_schemes",
                "user_generated_media",
            ]:
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    result[table] = [dict(row) for row in rows]
                except Exception as e:
                    result[table] = [{"error": f"Failed to fetch: {e}"}]
            return result

# =======================
# 8. GLOBAL SERVICES INITIALIZATION
# =======================

class AgentServices:
    """Centralized service management for the agent workflow."""
    
    def __init__(self):
        
        self.llm_gemini = ChatVertexAI(
            model="gemini-2.5-flash", 
            temperature=0.8,
            thinking_budget=0,

        )
        # google-genai client for image generation (prefer Vertex AI per project/location)
        self.genai_client = None
        try:
            project = (
                os.environ.get("GOOGLE_CLOUD_PROJECT")
                or os.environ.get("PROJECT_ID")
            )
            location = (
                os.environ.get("GOOGLE_CLOUD_REGION")
                or os.environ.get("LOCATION")
                or "us-central1"
            )
            if project:
                self.genai_client = genai.Client(vertexai=True, project=project, location=location)
                print(f"Initialized google-genai Vertex client (project={project}, location={location})")
            else:
                api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("KEY") or os.environ.get("GOOGLE_CLOUD_API_KEY")
                if api_key:
                    self.genai_client = genai.Client(api_key=api_key)
                    print("Initialized google-genai client with API key (Google AI API)")
                else:
                    print("No PROJECT/LOCATION or GOOGLE_API_KEY found; image generation disabled")
        except Exception as e:
            print(f"Failed to initialize google-genai client: {e}")

        self.checkpointer = InMemorySaver()
        self.store = SQLiteStore()  # Use SQLite instead of InMemoryStore
        self.workflow = None
        self._initialize_workflow()
    
    def _initialize_workflow(self):
        """Initialize the LangGraph workflow."""
        self.workflow = build_agentic_workflow(self)

# Global services instance
services = AgentServices()

# =======================
# 8. API ENDPOINTS
# =======================

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Serves the main frontend interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welfare Scheme Assistant</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh; display: flex; align-items: center; justify-content: center;
            }
            .chat-container {
                background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 800px; height: 600px; display: flex; flex-direction: column; overflow: hidden;
            }
            .chat-header {
                background: #4f46e5; color: white; padding: 20px; text-align: center;
                font-size: 1.5em; font-weight: bold; display: flex; justify-content: space-between; align-items: center;
            }
            .notification-btn {
                background: rgba(255,255,255,0.2); color: white; border: none; padding: 8px 16px;
                border-radius: 20px; cursor: pointer; font-size: 0.8em; transition: all 0.3s;
            }
            .notification-btn:hover {
                background: rgba(255,255,255,0.3); transform: scale(1.05);
            }
            .chat-messages {
                flex: 1; padding: 20px; overflow-y: auto; background: #f8fafc;
            }
            .message {
                margin: 10px 0; padding: 12px 16px; border-radius: 12px; max-width: 80%;
            }
            .user-message {
                background: #4f46e5; color: white; margin-left: auto; text-align: right;
            }
            .ai-message {
                background: white; border: 1px solid #e2e8f0; color: #374151;
            }
            .chat-input {
                display: flex; padding: 20px; background: white; border-top: 1px solid #e2e8f0;
            }
            .chat-input input {
                flex: 1; padding: 12px; border: 1px solid #d1d5db; border-radius: 8px;
                font-size: 16px; outline: none;
            }
            .chat-input button {
                margin-left: 10px; padding: 12px 20px; background: #4f46e5; color: white;
                border: none; border-radius: 8px; cursor: pointer; font-weight: bold;
            }
            .chat-input button:hover { background: #4338ca; }
            .typing-indicator { 
                display: none; color: #6b7280; font-style: italic; margin: 10px 0;
            }
            
            /* Modal Styles */
            .modal {
                display: none; position: fixed; z-index: 1000; left: 0; top: 0; 
                width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);
            }
            .modal-content {
                background-color: white; margin: 5% auto; padding: 0; border-radius: 15px;
                width: 90%; max-width: 600px; box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            }
            .modal-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 20px; border-radius: 15px 15px 0 0;
                display: flex; justify-content: space-between; align-items: center;
            }
            .modal-header h2 {
                margin: 0; font-size: 1.5em;
            }
            .close {
                color: white; font-size: 28px; font-weight: bold; cursor: pointer;
                transition: color 0.3s;
            }
            .close:hover {
                color: #f1f1f1;
            }
            .modal-body {
                padding: 20px; max-height: 500px; overflow-y: auto;
            }
            .scheme-card {
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 15px; padding: 20px; margin: 15px 0;
                border-left: 5px solid #4f46e5; transition: all 0.3s;
                cursor: pointer; position: relative; overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            }
            .scheme-card:hover {
                transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.15);
                border-left-width: 8px;
            }
            .scheme-card:active {
                transform: translateY(-2px); transition: all 0.1s;
            }
            .top-scheme {
                background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%);
                border-left-color: #f59e0b; box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
            }
            .top-badge {
                position: absolute; top: -5px; right: -5px; 
                background: #ef4444; color: white; padding: 5px 15px;
                border-radius: 0 15px 0 15px; font-size: 0.75em; font-weight: bold;
                animation: pulse 2s infinite;
            }
            .urgent-badge {
                position: absolute; top: 15px; right: 15px;
                background: #dc2626; color: white; padding: 4px 8px;
                border-radius: 12px; font-size: 0.7em; font-weight: bold;
                animation: blink 1.5s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.6; }
            }
            .scheme-title {
                font-size: 1.3em; font-weight: bold; color: #1e293b; margin-bottom: 10px;
                line-height: 1.2; text-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .scheme-description {
                color: #475569; margin-bottom: 15px; line-height: 1.6;
                font-size: 0.95em;
            }
            .scheme-details {
                display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;
            }
            .scheme-tag {
                background: #e0e7ff; color: #3730a3; padding: 5px 12px;
                border-radius: 20px; font-size: 0.8em; font-weight: 500;
            }
            .scheme-benefit {
                background: linear-gradient(135deg, #dcfce7 0%, #22c55e 100%); 
                color: #166534; padding: 6px 14px;
                border-radius: 20px; font-size: 0.85em; font-weight: 700;
                box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
            }
            .priority-tag {
                padding: 4px 10px; border-radius: 15px; font-size: 0.75em; 
                font-weight: 600; color: white;
            }
            .priority-tag.priority-high {
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            }
            .priority-tag.priority-medium {
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            }
            .priority-tag.priority-low {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            }
            .eligibility-section {
                font-size: 0.9em; color: #64748b; margin: 12px 0;
                padding: 10px; background: rgba(248, 250, 252, 0.8);
                border-radius: 8px; border-left: 3px solid #10b981;
            }
            .cta-button {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white; padding: 12px 20px; border-radius: 25px;
                text-align: center; font-weight: bold; margin-top: 15px;
                box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
                transition: all 0.3s; font-size: 0.9em;
            }
            .cta-button:hover {
                transform: translateY(-2px); box-shadow: 0 6px 20px rgba(79, 70, 229, 0.6);
            }
            .priority-high {
                border-left-color: #ef4444; animation: subtleGlow 3s infinite;
            }
            .priority-medium {
                border-left-color: #f59e0b;
            }
            .priority-low {
                border-left-color: #10b981;
            }
            @keyframes subtleGlow {
                0%, 100% { box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
                50% { box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2); }
            }
            .loading {
                text-align: center; padding: 40px; color: #6b7280;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                🏛️ Welfare Scheme Assistant
                <button onclick="showNotifications()" class="notification-btn" id="notificationBtn">
                    🔔 My Schemes
                </button>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="message ai-message">
                    Hello! I'm your welfare scheme assistant. I can help you find government benefits, create application forms, and answer questions about eligibility. What would you like to know?
                </div>
            </div>
            <div class="typing-indicator" id="typingIndicator">AI is thinking...</div>
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Type your message here..." />
                <button onclick="sendMessage()">Send</button>
            </div>
            <div style="padding: 12px; border-top: 1px solid #e2e8f0; background: #fff;">
                <form id="imageEditForm">
                    <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                        <input type="file" id="imageFile" accept="image/*" />
                        <button type="submit" style="padding:8px 16px; background:#10b981; color:#fff; border:none; border-radius:6px; cursor:pointer;">Edit Image</button>
                        <span id="imageEditStatus" style="color:#6b7280;"></span>
                    </div>
                </form>
                <div id="editedPreview" style="margin-top:10px;"></div>
            </div>
        </div>

        <!-- Notifications Modal -->
        <div id="notificationModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Your Recommended Schemes</h2>
                    <span class="close" onclick="closeNotifications()">&times;</span>
                </div>
                <div class="modal-body" id="notificationContent">
                    <div class="loading">Loading your personalized recommendations...</div>
                </div>
            </div>
        </div>

        <script>
            const chatMessages = document.getElementById('chatMessages');
            const messageInput = document.getElementById('messageInput');
            const typingIndicator = document.getElementById('typingIndicator');
            
            let userId = 'user_' + Math.random().toString(36).substr(2, 9);

            function addMessage(content, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
                messageDiv.textContent = content;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function showTyping() {
                typingIndicator.style.display = 'block';
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function hideTyping() {
                typingIndicator.style.display = 'none';
            }

            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                addMessage(message, true);
                messageInput.value = '';
                showTyping();

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message, user_id: userId })
                    });

                    const data = await response.json();
                    hideTyping();
                    
                    addMessage(data.response, false);
                } catch (error) {
                    hideTyping();
                    addMessage('Sorry, there was an error processing your request.', false);
                    console.error('Error:', error);
                }
            }

            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });

            // Focus input on load
            messageInput.focus();

            // Image edit handler
            const imageEditForm = document.getElementById('imageEditForm');
            imageEditForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const fileInput = document.getElementById('imageFile');
                const statusEl = document.getElementById('imageEditStatus');
                const previewEl = document.getElementById('editedPreview');
                if (!fileInput.files || fileInput.files.length === 0) {
                    statusEl.textContent = 'Please choose an image file.';
                    return;
                }
                statusEl.textContent = 'Editing image...';
                previewEl.innerHTML = '';

                const formData = new FormData();
                formData.append('user_id', userId);
                formData.append('image', fileInput.files[0]);

                try {
                    const resp = await fetch('/image/edit', { method: 'POST', body: formData });
                    const data = await resp.json();
                    if (!resp.ok) throw new Error(data.detail || 'Image edit failed');

                    statusEl.textContent = 'Done!';
                    if (data.image_base64) {
                        const img = document.createElement('img');
                        img.src = `data:image/png;base64,${data.image_base64}`;
                        img.style.maxWidth = '100%';
                        img.style.border = '1px solid #e5e7eb';
                        img.style.borderRadius = '8px';
                        previewEl.appendChild(img);
                    } else if (data.saved_uploaded_path) {
                        statusEl.textContent = 'Uploaded saved. No edited image returned.';
                    }
                } catch (err) {
                    console.error(err);
                    statusEl.textContent = 'Error editing image.';
                }
            });

            // Notification functions
            async function showNotifications() {
                const modal = document.getElementById('notificationModal');
                const content = document.getElementById('notificationContent');
                
                modal.style.display = 'block';
                content.innerHTML = '<div class="loading">Loading your personalized recommendations...</div>';
                
                try {
                    const response = await fetch(`/user/${userId}/notifications`);
                    if (response.ok) {
                        const data = await response.json();
                        displayNotifications(data.notifications);
                    } else if (response.status === 404) {
                        content.innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <h3>Complete Your Profile First</h3>
                                <p>Please complete the onboarding process to get personalized scheme recommendations.</p>
                                <button onclick="closeNotifications()" style="background: #4f46e5; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">
                                    Continue Chat
                                </button>
                            </div>
                        `;
                    } else {
                        content.innerHTML = '<div class="loading">Error loading recommendations. Please try again.</div>';
                    }
                } catch (error) {
                    console.error('Error:', error);
                    content.innerHTML = '<div class="loading">Error loading recommendations. Please try again.</div>';
                }
            }

            function displayNotifications(notifications) {
                const content = document.getElementById('notificationContent');
                
                if (!notifications || notifications.length === 0) {
                    content.innerHTML = '<div class="loading">No recommendations available at this time.</div>';
                    return;
                }
                
                let html = `<div style="margin-bottom: 20px; text-align: center; color: #6b7280;">
                    🎯 <strong>${notifications.length} Exclusive Benefits</strong> handpicked for you!
                </div>`;
                
                notifications.forEach((scheme, index) => {
                    const priorityClass = scheme.priority ? `priority-${scheme.priority.toLowerCase()}` : '';
                    const isTopScheme = index === 0; // Highlight first scheme
                    
                    html += `
                        <div class="scheme-card ${priorityClass} ${isTopScheme ? 'top-scheme' : ''}" onclick="handleSchemeClick('${scheme.title}')">
                            ${isTopScheme ? '<div class="top-badge">🏆 BEST MATCH</div>' : ''}
                            ${scheme.priority === 'High' ? '<div class="urgent-badge">⚡ HIGH PRIORITY</div>' : ''}
                            
                            <div class="scheme-title">${scheme.title}</div>
                            <div class="scheme-description">${scheme.description}</div>
                            
                            <div class="scheme-details">
                                <span class="scheme-benefit">💰 ${scheme.benefit_amount}</span>
                                <span class="scheme-tag">${scheme.category || 'Government Scheme'}</span>
                                ${scheme.priority ? `<span class="priority-tag priority-${scheme.priority.toLowerCase()}">${scheme.priority} Priority</span>` : ''}
                            </div>
                            
                            <div class="eligibility-section">
                                <strong>✅ Eligibility:</strong> ${scheme.eligibility}
                            </div>
                            
                            ${scheme.call_to_action ? `
                                <div class="cta-button">
                                    ${scheme.call_to_action} →
                                </div>
                            ` : ''}
                        </div>
                    `;
                });
                
                html += `
                    <div style="text-align: center; margin-top: 20px; padding: 15px; background: #f8fafc; border-radius: 10px;">
                        <p style="color: #6b7280; margin: 0;">💡 <strong>Pro Tip:</strong> Apply for multiple schemes to maximize your benefits!</p>
                    </div>
                `;
                
                content.innerHTML = html;
            }

            function handleSchemeClick(schemeTitle) {
                // Add some interaction feedback
                console.log('User clicked on scheme:', schemeTitle);
                // You can add more functionality here like opening application forms
            }

            function getPriorityColor(priority) {
                switch(priority.toLowerCase()) {
                    case 'high': return '#ef4444';
                    case 'medium': return '#f59e0b';
                    case 'low': return '#10b981';
                    default: return '#6b7280';
                }
            }

            function closeNotifications() {
                document.getElementById('notificationModal').style.display = 'none';
            }

            // Close modal when clicking outside
            window.onclick = function(event) {
                const modal = document.getElementById('notificationModal');
                if (event.target === modal) {
                    closeNotifications();
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Main chat endpoint that processes user messages through the agentic workflow."""
    try:
        config = {"configurable": {"thread_id": chat_message.user_id}}
        
        # Get the current state from the checkpointer to continue the conversation
        current_state = services.workflow.get_state(config)
        
        if current_state and current_state.values:
            # If there's an existing state, add the new message to it
            print("Continuing existing conversation.")
            messages = current_state.values.get("messages", []) + [HumanMessage(content=chat_message.message)]
            # Pass the whole state to continue properly
            input_state = current_state.values
            input_state["messages"] = messages
        else:
            # If no state, this is a new conversation
            print("Starting new conversation.")
            input_state = {
                "messages": [HumanMessage(content=chat_message.message)],
                "user_id": chat_message.user_id
            }

        # Execute workflow with the correct state
        result_state = services.workflow.invoke(input_state, config)
        
        # The final response is in the last AIMessage in the 'messages' list
        final_response = ""
        if result_state and result_state.get('messages'):
            # Find the last AI message in the list
            for msg in reversed(result_state['messages']):
                if isinstance(msg, AIMessage):
                    final_response = msg.content
                    break

        print(f"Workflow result: onboarding={result_state.get('is_onboarding')}, response={final_response[:100]}...")
        
        # Get user profile if it was created
        user_profile = result_state.get('user_profile_data', {})
        if not user_profile:
            try:
                user_profile = services.store.get_user_profile(chat_message.user_id) or {}
            except Exception as e:
                print(f"Error retrieving profile from store: {e}")

        return ChatResponse(
            response=final_response or "I'm sorry, I couldn't process that request.",
            is_onboarding=result_state.get("is_onboarding", False),
            onboarding_step=result_state.get("onboarding_step"),
            user_profile=coerce_profile_to_strings(user_profile),
            backstory=result_state.get("backstory")
        )

    except Exception as e:
        print(f"Chat endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/user/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Retrieves a user's profile information."""
    try:
        # Input validation
        if not user_id or len(user_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        profile_data = services.store.get_user_profile(user_id)
        if not profile_data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Remove user_id from profile_data to avoid conflict when unpacking
        profile_data_copy = profile_data.copy()
        profile_data_copy.pop('user_id', None)  # Remove user_id if it exists
        
        return UserProfile(user_id=user_id, **profile_data_copy)
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")

@app.get("/user/{user_id}/backstory")
async def get_user_backstory(user_id: str):
    """Returns the artisan backstory if available."""
    try:
        if not user_id or len(user_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        profile_data = services.store.get_user_profile(user_id)
        if not profile_data:
            raise HTTPException(status_code=404, detail="User profile not found")
        backstory = profile_data.get('backstory')
        if not backstory:
            raise HTTPException(status_code=404, detail="Backstory not found. Complete onboarding to generate one.")
        return {"user_id": user_id, "backstory": backstory}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving backstory: {str(e)}")

@app.post("/image/edit")
async def edit_image(
    user_id: str = Form(...),
    image: UploadFile = File(...),
    prompt: Optional[str] = Form(None)
):
    """Edits an image using the artisan's user profile to build a default prompt.
    Saves both the uploaded and generated images locally and returns base64 for display.
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=400, detail="user_id is required")
        if not image or not image.filename:
            raise HTTPException(status_code=400, detail="Image file is required")
        # Look up profile for prompt construction
        try:
            profile = services.store.get_user_profile(user_id) or {}
        except Exception:
            profile = {}

        # Build a default prompt from profile if not provided
        if not prompt or not prompt.strip():
            name = profile.get('name') or 'the artisan'
            craft = profile.get('craft_type') or 'handmade crafts'
            style = profile.get('brand_style') or 'warm, natural, earthy'
            region = profile.get('state') or ''
            prompt = (
    f"Edit/enhance this photo for {name}, a {craft} artisan"
    + (f" from {region}." if region else ".")
    + f" Keep the style {style}. Improve lighting and colors, keep it authentic, no text or watermarks. "
    + "Do not change the main product in the image—just make it look better. "
    + "Change or enhance the background so it matches the type of product and looks suitable for advertising but not make it completely different." + 'Make it suitable for use on an e-commerce website. and look like a product photo taken from dslr'
)

        # Read bytes first (UploadFile stream can only be read once)
        image_bytes = await image.read()

        # Ensure folders exist
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        edited_dir = os.path.join(os.getcwd(), "edited")
        os.makedirs(uploads_dir, exist_ok=True)
        os.makedirs(edited_dir, exist_ok=True)

        # Save uploaded image to uploads
        upload_name = f"upload_{uuid4().hex}_{image.filename}"
        upload_path = os.path.join(uploads_dir, upload_name)
        with open(upload_path, 'wb') as f:
            f.write(image_bytes)

        # Use google-genai client if available to generate an edited image
        if getattr(services, 'genai_client', None):
            try:
                mime = image.content_type or 'image/png'
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=prompt),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=mime,
                                    data=image_bytes,
                                )
                            ),
                        ],
                    )
                ]

                generate_content_config = types.GenerateContentConfig(
                    temperature=1,
                    top_p=0.95,
                    max_output_tokens=32768,
                    response_modalities=["TEXT", "IMAGE"],
                    safety_settings=[
                        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
                    ],
                )

                # Preferred model (user override first, then preview image model)
                model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image-preview")

                # Helper to try a call and optionally rebuild client with a different location
                def _try_generate(client, mdl):
                    return client.models.generate_content(
                        model=mdl,
                        contents=contents,
                        config=generate_content_config,
                    )

                resp = None
                err = None
                client_used = services.genai_client
                model_used = model

                try:
                    resp = _try_generate(client_used, model_used)
                except genai_errors.ClientError as ce:
                    err = ce
                    # If Vertex + NotFound or InvalidArgument, try changing location to us-central1/global fallback
                    loc_env = os.environ.get("GOOGLE_CLOUD_REGION") or os.environ.get("LOCATION") or "us-central1"
                    proj_env = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID")
                    # Only attempt location swap if running Vertex mode (has project)
                    if proj_env:
                        try_locations = [
                            os.environ.get("LOCATION") or "global",
                            "us-central1",
                        ]
                        for loc in try_locations:
                            try:
                                client_used = genai.Client(vertexai=True, project=proj_env, location=loc)
                                resp = _try_generate(client_used, model_used)
                                print(f"Image gen succeeded after location change to {loc}")
                                break
                            except genai_errors.ClientError as ce2:
                                err = ce2
                                continue
                    # If still failing, try Imagen text-to-image model
                    if resp is None:
                        for alt_model in ["imagen-3.0-generate-001", "gemini-2.0-flash-exp"]:
                            try:
                                model_used = alt_model
                                resp = _try_generate(client_used, model_used)
                                print(f"Image gen succeeded with alternate model {alt_model}")
                                break
                            except genai_errors.ClientError as ce3:
                                err = ce3
                                continue
                except Exception as e:
                    err = e

                if resp is None:
                    raise HTTPException(status_code=502, detail=f"Image generation failed: {err}")

                # Extract image (base64) from response if present
                def _extract_image_from_genai(r) -> Optional[Dict[str, str]]:
                    try:
                        # Prefer structured access
                        for cand in getattr(r, "candidates", []) or []:
                            content = getattr(cand, "content", None)
                            parts = getattr(content, "parts", []) if content else []
                            for p in parts:
                                inline = getattr(p, "inline_data", None)
                                if inline and getattr(inline, "data", None):
                                    data = inline.data
                                    # Ensure base64 string
                                    if isinstance(data, (bytes, bytearray)):
                                        data = base64.b64encode(data).decode("ascii")
                                    return {
                                        "data": data,
                                        "mime": getattr(inline, "mime_type", "image/png"),
                                    }
                        # Also check top-level content
                        content = getattr(r, "content", None)
                        if content:
                            for p in getattr(content, "parts", []) or []:
                                inline = getattr(p, "inline_data", None)
                                if inline and getattr(inline, "data", None):
                                    data = inline.data
                                    if isinstance(data, (bytes, bytearray)):
                                        data = base64.b64encode(data).decode("ascii")
                                    return {
                                        "data": data,
                                        "mime": getattr(inline, "mime_type", "image/png"),
                                    }
                    except Exception:
                        pass
                    # Fallback: stringify and regex search
                    try:
                        s = str(r)
                        m = re.search(r'data:image\/[^;]+;base64,([A-Za-z0-9+/=]+)', s)
                        if m:
                            return {"data": m.group(1), "mime": "image/png"}
                        m2 = re.search(r'([A-Za-z0-9+/=]{200,})', s)
                        if m2:
                            return {"data": m2.group(1), "mime": "image/png"}
                    except Exception:
                        pass
                    return None

                image_info = _extract_image_from_genai(resp)
                if image_info and image_info.get("data"):
                    img_b64 = image_info["data"]
                    mime_out = image_info.get("mime", "image/png")
                    # Determine extension
                    ext = ".png"
                    if "jpeg" in mime_out or "jpg" in mime_out:
                        ext = ".jpg"
                    elif "webp" in mime_out:
                        ext = ".webp"

                    edited_name = f"edited_{uuid4().hex}{ext}"
                    edited_path = os.path.join(edited_dir, edited_name)
                    try:
                        with open(edited_path, 'wb') as ef:
                            ef.write(base64.b64decode(img_b64))
                    except Exception as se:
                        print(f"Failed saving edited image: {se}")
                        edited_path = None

                    # Generate a caption/description tailored to the user's profile
                    try:
                        prof_for_prompt = sanitize_profile(profile)
                        desc_prompt = ChatPromptTemplate.from_template(
                            """
You are an assistant helping an Indian artisan describe a product photo for social media and catalog listings.
Keep it short (35-60 words), warm, and authentic. Mention craft, materials, region or style if helpful. No emojis.

User Profile (for context): {profile}
Instruction or Prompt used: {prompt}

Write a single paragraph product description suitable for e-commerce and Instagram.
"""
                        )
                        desc_chain = desc_prompt | services.llm_gemini.bind_tools([{ "google_search": {} }]) | StrOutputParser()
                        description_text = desc_chain.invoke({
                            "profile": json.dumps(prof_for_prompt),
                            "prompt": prompt,
                        }).strip()
                    except Exception:
                        description_text = None

                    # Persist record into DB (store edited image blob too for portability)
                    try:
                        record_id = services.store.save_generated_media(
                            user_id=user_id,
                            description=description_text,
                            prompt_used=prompt,
                            model_used=model_used,
                            original_image_path=upload_path,
                            edited_image_path=edited_path,
                            edited_image_blob=base64.b64decode(img_b64) if img_b64 else None,
                        )
                    except Exception as e:
                        print(f"Failed to save generated media: {e}")
                        record_id = None

                    return {
                        "message": "Image edit completed",
                        "record_id": record_id,
                        "prompt_used": prompt,
                        "image_base64": img_b64,
                        "saved_uploaded_path": upload_path,
                        "saved_edited_path": edited_path,
                        "profile_used": prof_for_prompt if 'prof_for_prompt' in locals() else sanitize_profile(profile),
                        "model_used": model_used,
                        "description": description_text,
                    }

                # If we couldn't extract an image, include text response for debugging
                text_out = getattr(resp, "text", None) or ""
                return {
                    "message": "No image found in model response",
                    "prompt_used": prompt,
                    "model_response_text": text_out,
                    "saved_uploaded_path": upload_path,
                }
            except Exception as e:
                print(f"Image generation failed: {e}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

        # Fallback placeholder when image model not available
        # Even if we don't have model, we can still store the upload as a media record with no edited image
        desc_text = None
        try:
            prof_for_prompt = sanitize_profile(profile)
            if prompt:
                desc_prompt = ChatPromptTemplate.from_template(
                    """
Write a concise, warm product description (35-60 words) for an artisan's image based on the prompt and profile. No emojis.

Profile: {profile}
Prompt: {prompt}
"""
                )
                desc_chain = desc_prompt | services.llm_gemini.bind_tools([{ "google_search": {} }]) | StrOutputParser()
                desc_text = desc_chain.invoke({
                    "profile": json.dumps(prof_for_prompt),
                    "prompt": prompt,
                }).strip()
        except Exception:
            pass

        try:
            record_id = services.store.save_generated_media(
                user_id=user_id,
                description=desc_text,
                prompt_used=prompt,
                model_used=None,
                original_image_path=upload_path,
                edited_image_path=None,
                edited_image_blob=None,
            )
        except Exception:
            record_id = None

        result = {
            "message": "Image edit requested, but image-generation model is not configured or available.",
            "record_id": record_id,
            "prompt_used": prompt,
            "saved_uploaded_path": upload_path,
            "description": desc_text,
        }
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error editing image: {str(e)}")

@app.delete("/user/{user_id}/profile")
async def delete_user_profile(user_id: str):
    """Deletes a user's profile (for testing/reset purposes)."""
    try:
        # Input validation
        if not user_id or len(user_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Check if profile exists before deletion
        existing_profile = services.store.get_user_profile(user_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        services.store.delete_user_profile(user_id)
        return {"message": f"Profile for user {user_id} deleted successfully"}
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting profile: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "llm_groq": "operational",
            "llm_gemini": "operational",
            "welfare_search": "operational",
            "sqlite_store": "operational"
        }
    }

@app.get("/db/all")
async def get_all_db_entries():
    """Return all rows from key tables. Intended for admin/debug use."""
    try:
        data = services.store.get_all_db_entries()
        # For blobs, avoid huge payloads: include sizes not raw blobs
        media = data.get("user_generated_media", [])
        for m in media:
            blob = m.get("edited_image_blob")
            if isinstance(blob, (bytes, bytearray)):
                m["edited_image_blob_size"] = len(blob)
                m["edited_image_blob"] = None
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch DB dump: {str(e)}")

@app.get("/user/{user_id}/media")
async def get_user_media(user_id: str):
    """List all generated media for a user with small base64 payloads when possible."""
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=400, detail="Invalid user ID")
        records = services.store.get_user_media(user_id)
        result = []
        for r in records:
            out: Dict[str, Any] = {
                "id": r.get("id"),
                "user_id": r.get("user_id"),
                "description": r.get("description"),
                "prompt_used": r.get("prompt_used"),
                "model_used": r.get("model_used"),
                "original_image_path": r.get("original_image_path"),
                "edited_image_path": r.get("edited_image_path"),
                "created_at": r.get("created_at"),
            }
            # Include base64 if we have a blob; else try reading from file path
            img_b64 = None
            blob = r.get("edited_image_blob")
            if isinstance(blob, (bytes, bytearray)) and len(blob) > 0:
                try:
                    img_b64 = base64.b64encode(blob).decode("ascii")
                except Exception:
                    img_b64 = None
            elif r.get("edited_image_path") and os.path.isfile(r["edited_image_path"]):
                try:
                    with open(r["edited_image_path"], "rb") as f:
                        img_b64 = base64.b64encode(f.read()).decode("ascii")
                except Exception:
                    img_b64 = None
            out["edited_image_base64"] = img_b64
            result.append(out)
        return {"user_id": user_id, "count": len(result), "items": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch media: {str(e)}")

# =======================
# 9. WEBSOCKET SUPPORT (OPTIONAL)
# =======================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat (optional enhancement)."""
    await websocket.accept()
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process through workflow (similar to chat endpoint)
            initial_state = {
                "messages": [HumanMessage(content=message_data["message"])],
                "user_id": user_id,
                "is_onboarding": False,
                "onboarding_step": 0,
                "user_profile_data": {},
                "intent": "",
                "tool_output": None,
                "final_response_text": "",
                "timestamp": datetime.now().isoformat(),
                "session_id": str(uuid4())
            }
            
            config = {"configurable": {"thread_id": user_id}}
            result = services.workflow.invoke(initial_state, config)
            
            # Send response back to client
            response = {
                "response": result.get("final_response_text", "Error processing request"),
                "is_onboarding": result.get("is_onboarding", False),
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user_id}")

# =======================
# 10. APPLICATION STARTUP
# =======================

if __name__ == "__main__":
    print("🚀 Starting Welfare Scheme Assistant...")
    print("📊 Services initialized successfully")
    print("🌐 Frontend available at: http://localhost:8000")
    print("📖 API Documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        "agentic_fastapi_app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )