import json
from datetime import datetime
from glob import glob
from pathlib import Path
from asyncpixel.models import Player


class DirTreeIsoJson:
    """
    Store interface for player-data stored like <data_root>/<uuid>/<timestamp>.json
    """

    def __init__(self, data_root: str):
        self.root_dir = Path(data_root)

    def player_dir(self, uuid: str):
        return self.root_dir / uuid

    def find_files(self, uuid: str):
        return {
            datetime.fromisoformat(str(path.stem)): path
            for path in self.player_dir(uuid).iterdir()
        }

    def get_data(self, path: Path) -> dict:
        with path.open() as f:
            response = json.load(f)

        if not response["success"]:
            return None

        return Player(**response["player"])
