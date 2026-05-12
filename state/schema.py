from typing import TypedDict, Literal, Optional, List, Any
from datetime import datetime

class AgentState(TypedDict):
    # --- Core routing ---
    current_agent: str                          # which agent is active
    task: str                                   # what needs to be done
    task_id: str                                # unique task ID
    priority: Literal["low", "medium", "high", "critical"]

    # --- CEO / Human-in-the-loop ---
    needs_ceo_approval: bool                    # pause graph → notify you
    ceo_decision: Optional[Literal["approve", "reject", "modify"]]
    ceo_notes: Optional[str]                    # your instructions back

    # --- Emergency ---
    is_emergency: bool
    emergency_reason: Optional[str]

    # --- Task result passing between agents ---
    messages: List[dict]                        # full conversation log
    result: Optional[Any]                       # output of last agent
    error: Optional[str]                        # if something failed

    # --- Metadata ---
    created_at: str
    updated_at: str
    initiated_by: str                           # which dept started this
    target_agent: Optional[str]                 # handoff target

def new_state(task: str, agent: str, priority="medium") -> AgentState:
    now = datetime.now().isoformat()
    return AgentState(
        current_agent=agent,
        task=task,
        task_id=f"{agent}_{now}",
        priority=priority,
        needs_ceo_approval=False,
        ceo_decision=None,
        ceo_notes=None,
        is_emergency=False,
        emergency_reason=None,
        messages=[],
        result=None,
        error=None,
        created_at=now,
        updated_at=now,
        initiated_by=agent,
        target_agent=None,
    )