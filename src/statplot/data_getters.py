import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from asyncpixel.models import Player


class DirTreeIsoJson:
    """
    Store interface for player-data stored like <data_root>/<uuid>/<timestamp>.json
    """

    def __init__(self, data_root: Path):
        self.data_root = data_root

    def _player_dir(self, uuid: str) -> Path:
        """Return the directory containing the stats for this player"""
        return self.data_root / uuid

    def find_files(self, uuid: str) -> dict[datetime, Path]:
        """Return a dict mapping a timestamp to the statfile for that time"""
        return {
            datetime.fromisoformat(str(path.stem)): path
            for path in self._player_dir(uuid).iterdir()
        }

    def get_data(self, path: Path) -> Optional[Player]:
        """Given the path to a statfile return a Player instance, or None if error"""
        try:
            with path.open() as f:
                response = json.load(f)
        except Exception:
            # Handle missing/bad responses
            return None

        if not response["success"]:
            return None

        return Player(**response["player"])
