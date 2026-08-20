import threading
import uuid
import time
import json
import os
from config import SESSIONS_DIR

class SessionStore:
    """
    Persistent session store for analysis results.
    Saves context to disk so AI chat survives server restarts.
    """
    def __init__(self, expiry_seconds=3600):
        self._store = {}
        self._lock = threading.Lock()
        self._expiry = expiry_seconds
        self._sessions_dir = SESSIONS_DIR

    def create_session(self, data: dict) -> str:
        """
        Stores analysis data and returns a unique session_id.
        """
        session_id = str(uuid.uuid4())
        timestamp = time.time()
        
        entry = {
            "data": data,
            "timestamp": timestamp
        }
        
        with self._lock:
            self._store[session_id] = entry
            
        # Perisist to disk for restart resilience
        try:
            session_path = os.path.join(self._sessions_dir, f"session_{session_id}.json")
            with open(session_path, 'w') as f:
                json.dump(entry, f)
        except Exception as e:
            print(f"Failed to persist session {session_id}: {e}")
            
        return session_id

    def get_session(self, session_id: str) -> dict:
        """
        Retrieves analysis data for a given session_id.
        Checks memory cache first, then disk.
        """
        with self._lock:
            entry = self._store.get(session_id)
            
            # If not in memory (e.g. after restart), try to load from disk
            if not entry:
                session_path = os.path.join(self._sessions_dir, f"session_{session_id}.json")
                if os.path.exists(session_path):
                    try:
                        with open(session_path, 'r') as f:
                            entry = json.load(f)
                            self._store[session_id] = entry
                    except Exception as e:
                        print(f"Failed to load session {session_id} from disk: {e}")
            
            if entry:
                # Refresh timestamp on access
                entry["timestamp"] = time.time()
                return entry["data"]
                
        return None

    def cleanup(self):
        """
        Removes expired sessions from memory and disk.
        """
        now = time.time()
        with self._lock:
            # Memory cleanup
            expired = [sid for sid, entry in self._store.items() 
                       if now - entry["timestamp"] > self._expiry]
            for sid in expired:
                del self._store[sid]
                
            # Disk cleanup (scan entire directory occasionally)
            try:
                for filename in os.listdir(self._sessions_dir):
                    if filename.startswith("session_") and filename.endswith(".json"):
                        path = os.path.join(self._sessions_dir, filename)
                        if now - os.path.getmtime(path) > self._expiry:
                            os.remove(path)
            except Exception as e:
                print(f"Session cleanup failed: {e}")

# Global instance
session_store = SessionStore()
