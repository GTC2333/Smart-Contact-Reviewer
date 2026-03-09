"""
Session storage module.
Provides JSON file-based storage for audit sessions.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class SessionSummary:
    """Summary of an audit session."""
    session_id: str
    contract_name: str
    created_at: str
    updated_at: str
    risk_count: int
    risk_high: int
    risk_medium: int
    risk_low: int


@dataclass
class AuditSession:
    """Full audit session data."""
    session_id: str
    contract_name: str
    created_at: str
    updated_at: str
    audit_result: Dict[str, Any]


class SessionStore:
    """
    Session storage manager using JSON file storage.
    Stores sessions in data/sessions/*.json
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize session store."""
        if storage_dir is None:
            # Default to project_root/data/sessions
            project_root = Path(__file__).parent.parent.parent
            storage_dir = project_root / "data" / "sessions"

        self.storage_dir = Path(storage_dir)
        self._ensure_dir()
        self.index_file = self.storage_dir / "index.json"

    def _ensure_dir(self):
        """Ensure storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_index(self) -> Dict[str, Any]:
        """Load or create session index."""
        if self.index_file.exists():
            with open(self.index_file, encoding="utf-8") as f:
                return json.load(f)
        return {"sessions": []}

    def _save_index(self, index: Dict[str, Any]):
        """Save session index."""
        with open(self.index_file, 'w', encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def _get_session_file(self, session_id: str) -> Path:
        """Get session file path."""
        return self.storage_dir / f"{session_id}.json"

    def save_session(self, contract_name: str, audit_result: Dict[str, Any]) -> str:
        """
        Save a new audit session.

        Args:
            contract_name: Name of the contract
            audit_result: Full audit result dictionary

        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Extract risk statistics (severity is in Chinese: 高/中/低)
        annotations = audit_result.get("annotations", [])
        risk_high = len([a for a in annotations if a.get("severity", "").strip() == "高"])
        risk_medium = len([a for a in annotations if a.get("severity", "").strip() == "中"])
        risk_low = len([a for a in annotations if a.get("severity", "").strip() == "低"])

        # Create session data
        session = AuditSession(
            session_id=session_id,
            contract_name=contract_name,
            created_at=now,
            updated_at=now,
            audit_result=audit_result
        )

        # Save session file
        self._ensure_dir()
        session_file = self._get_session_file(session_id)
        with open(session_file, 'w', encoding="utf-8") as f:
            json.dump(asdict(session), f, ensure_ascii=False, indent=2)

        # Update index
        index = self._get_index()
        summary = SessionSummary(
            session_id=session_id,
            contract_name=contract_name,
            created_at=now,
            updated_at=now,
            risk_count=len(annotations),
            risk_high=risk_high,
            risk_medium=risk_medium,
            risk_low=risk_low
        )
        index["sessions"].insert(0, asdict(summary))
        self._save_index(index)

        return session_id

    def get_session(self, session_id: str) -> Optional[AuditSession]:
        """
        Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            AuditSession if found, None otherwise
        """
        session_file = self._get_session_file(session_id)
        if not session_file.exists():
            return None

        with open(session_file, encoding="utf-8") as f:
            data = json.load(f)

        return AuditSession(**data)

    def list_sessions(self, limit: int = 50) -> List[SessionSummary]:
        """
        List all sessions (most recent first).

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session summaries
        """
        index = self._get_index()
        sessions = index.get("sessions", [])[:limit]
        return [SessionSummary(**s) for s in sessions]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        session_file = self._get_session_file(session_id)
        if not session_file.exists():
            return False

        # Delete session file
        session_file.unlink()

        # Update index
        index = self._get_index()
        index["sessions"] = [s for s in index["sessions"] if s["session_id"] != session_id]
        self._save_index(index)

        return True

    def search_sessions(self, keyword: str) -> List[SessionSummary]:
        """
        Search sessions by keyword.

        Args:
            keyword: Search keyword

        Returns:
            List of matching session summaries
        """
        index = self._get_index()
        keyword_lower = keyword.lower()
        results = [
            SessionSummary(**s) for s in index["sessions"]
            if keyword_lower in s["contract_name"].lower()
        ]
        return results

    def update_session_name(self, session_id: str, new_name: str) -> bool:
        """
        Update session name.

        Args:
            session_id: Session identifier
            new_name: New contract name

        Returns:
            True if updated, False if not found
        """
        session = self.get_session(session_id)
        if not session:
            return False

        now = datetime.now().isoformat()

        # Update session file
        session.contract_name = new_name
        session.updated_at = now
        session_file = self._get_session_file(session_id)
        with open(session_file, 'w', encoding="utf-8") as f:
            json.dump(asdict(session), f, ensure_ascii=False, indent=2)

        # Update index
        index = self._get_index()
        for s in index["sessions"]:
            if s["session_id"] == session_id:
                s["contract_name"] = new_name
                s["updated_at"] = now
                break
        self._save_index(index)

        return True


# Global instance
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get the global session store instance."""
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store
