"""
Court Topic Loader (F7).
Loads court meeting topics from COURT_TOPICS_MVP.json.
Follows the same pattern as EventTemplateLoader.
"""
import json
import os
from typing import Dict, List, Optional


class CourtTopicLoader:
    _DEFAULT_PATH = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "docs", "design", "COURT_TOPICS_MVP.json")
    )
    _topics: Optional[List[Dict]] = None

    @classmethod
    def load_topics(cls, path: str = None) -> List[Dict]:
        """Load and cache topics from JSON. Returns list of topic dicts."""
        if cls._topics is None:
            p = path or cls._DEFAULT_PATH
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            cls._topics = data["topics"]
        return cls._topics
