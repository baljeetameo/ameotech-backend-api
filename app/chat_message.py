from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from collections import defaultdict
from typing import List, Dict

from .models import ChatMessage
from .schemas import ChatMessageOut, ChatSessionOut, ChatMessageReadUpdate
from .database import get_db
from .auth_interceptor import role_checker

router = APIRouter(prefix="/sales/messages", tags=["chat-message"])


@router.get("", response_model=List[ChatSessionOut])
async def list_chatmessages(
    db: Session = Depends(get_db),
    role: str = Depends(role_checker(["SalesEngineer"]))
):
  try:
      messages = db.query(ChatMessage).all()

      # Group messages by session_id
      grouped: Dict[str, List[ChatMessageOut]] = defaultdict(list)
      latest_timestamp: Dict[str, datetime] = {}
      session_is_read: Dict[str, bool] = defaultdict(bool)

      for msg in messages:
        grouped[msg.session_id].append(ChatMessageOut.from_orm(msg))

        # Track the latest timestamp per session
        if msg.session_id not in latest_timestamp:
            latest_timestamp[msg.session_id] = msg.created_at
        
        if msg.is_read:
            session_is_read[msg.session_id] = True


      # Convert to list of sessions
      result = []
      for session_id, msgs in grouped.items():
          result.append(ChatSessionOut(session_id=session_id,is_read=session_is_read[session_id], messages=msgs))

      # Sort sessions by latest chat time (DESC)  
      result.sort(key=lambda s: latest_timestamp[s.session_id], reverse=True)
      return result

  except HTTPException:
      raise
  except Exception as e:
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail=f"Failed to fetch chat messages: {str(e)}"
      )


# Need to call this api from ui
@router.put("/mark-session-read", status_code=status.HTTP_200_OK)
def mark_chat_message_read(
    payload: ChatMessageReadUpdate,
    db: Session = Depends(get_db),
    role: str = Depends(role_checker(["SalesEngineer"]))
):
    updated_rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == payload.session_id)
        .update(
            {ChatMessage.is_read: payload.is_read},
            synchronize_session=False
        )
    )

    if updated_rows == 0:
        raise HTTPException(
            status_code=404,
            detail="No messages found for the given session_id"
        )

    db.commit()

    return {
        "message": "Chat messages updated successfully",
        "session_id": payload.session_id,
        "updated_count": updated_rows,
        "is_read": payload.is_read
    }