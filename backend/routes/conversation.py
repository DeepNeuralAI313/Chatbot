from fastapi import APIRouter, HTTPException
from models.conversation import ConversationHistory, Message
from database.db import get_conversation_history

router = APIRouter()

@router.get("/api/conversation/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(conversation_id: str):
    """
    Get conversation history by ID
    """
    try:
        messages = get_conversation_history(conversation_id)
        
        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=[Message(**msg) for msg in messages]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
