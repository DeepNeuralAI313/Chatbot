from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.conversation import ChatRequest, ChatResponse
from services.rag_service import search_knowledge, get_conversation_context
from services.llm_service import generate_response_with_tokens
from database.db import (
    get_setting, save_conversation_with_user, save_message,
    get_conversation_history, save_token_usage, update_conversation_title
)
from routes.user import verify_user_token
import uuid

router = APIRouter()
security = HTTPBearer()

def check_escalation(message: str) -> bool:
    """Check if message contains escalation keywords (refund/money back)"""
    keywords = ['refund', 'money back']
    return any(keyword in message.lower() for keyword in keywords)

@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: int = Depends(verify_user_token)):
    """
    Main chat endpoint that handles user messages with RAG and memory
    """
    try:
        # Generate or use conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Save conversation if new
        save_conversation_with_user(conversation_id, user_id)
        
        # Save user message
        save_message(conversation_id, "user", request.message)
        
        # Check for escalation keywords (refund/money back)
        if check_escalation(request.message):
            # Log escalation in JSON format
            import json
            import datetime
            escalation_log = {
                "needs_human": True,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message": request.message,
                "timestamp": datetime.datetime.now().isoformat(),
                "reason": "refund_or_money_back_request"
            }
            print(f"ESCALATION LOG: {json.dumps(escalation_log, indent=2)}")
            
            # Save assistant response with human handoff option
            escalation_message = "I understand you're asking about refunds or money back. I'd be happy to connect you with our support team who can better assist you with this request. Would you like me to transfer you to a human agent?"
            save_message(conversation_id, "assistant", escalation_message)
            
            return ChatResponse(
                reply=escalation_message,
                needs_human=True,
                conversation_id=conversation_id
            )
        
        # Get conversation history for context (memory)
        conversation_memory = get_conversation_history(conversation_id)
        
        # Search for relevant context using RAG
        relevant_chunks, similarity_score = search_knowledge(request.message, top_k=5)
        
        # Get settings from database
        tone_instructions = get_setting("tone_instructions")
        fallback_message = get_setting("fallback_message")
        
        # Build context from relevant chunks (use lower threshold)
        context = "\n\n".join(relevant_chunks) if relevant_chunks else "No specific context available."
        
        # Add conversation memory (last 5 messages for context)
        memory_context = ""
        if len(conversation_memory) > 1:  # More than just the current message
            recent_messages = conversation_memory[-6:-1]  # Last 5 messages before current
            memory_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        # Generate response using LLM with token tracking
        ai_response, token_info = generate_response_with_tokens(
            system_instructions=tone_instructions,
            context=context,
            user_message=request.message,
            memory_context=memory_context
        )
        
        # Save token usage
        if token_info:
            save_token_usage(
                conversation_id,
                user_id,
                token_info["prompt_tokens"],
                token_info["completion_tokens"],
                token_info["total_tokens"],
                token_info["cost"]
            )
        
        # Auto-generate title from first message
        if len(conversation_memory) == 1:  # First message
            # Create a smart title from the user's first message
            title = request.message.strip()
            # Remove question marks and clean up
            title = title.replace('?', '').replace('!', '')
            # Capitalize first letter
            title = title[0].upper() + title[1:] if len(title) > 1 else title
            # Limit length
            if len(title) > 60:
                # Try to cut at a word boundary
                title = title[:60].rsplit(' ', 1)[0] + '...'
            update_conversation_title(conversation_id, title)
        
        # Save assistant response
        save_message(conversation_id, "assistant", ai_response)
        
        return ChatResponse(
            reply=ai_response,
            needs_human=False,
            conversation_id=conversation_id
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        error_msg = {"role": "assistant", "content": "Sorry, an error occurred. Please try again."}
        raise HTTPException(status_code=500, detail=str(e))
