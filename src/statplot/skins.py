"""
Function for downloading the skin of a user with a given uuid

Adapted from:
https://ourcodeworld.com/articles/read/1293/how-to-retrieve-the-skin-of-a-minecraft-user-from-mojang-using-python-3
"""
import json
from base64 import b64decode
from io import BytesIO
from pathlib import Path
from typing import Optional

import requests
from PIL import Image

SESSION_URL = "https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"


def find_skin_url(session_info: dict) -> Optional[str]:
    """Find the url to the player's skin from the session info"""
    for prop in session_info["properties"]:
        if prop["name"] == "textures":
            texture_info = json.loads(
                b64decode(prop["value"], validate=True).decode("utf-8")
            )
            break
    else:
        return None

    try:
        return texture_info["textures"]["SKIN"]["url"]
    except KeyError:
        return None


def make_head_texture(skin: Image) -> Image:
    """Overlay the base and hat layer for the head"""
    head_base_layer = skin.crop((8, 8, 16, 16))
    head_hat_layer = skin.crop((40, 8, 48, 16))

    return Image.alpha_composite(head_base_layer, head_hat_layer)


def get_head_path(head_dir: Path, uuid: str) -> Path:
    """Return the path to the head for the given uuid"""
    return head_dir / f"{uuid}.png"


def download_head_texture(uuid: str, head_dir: Path) -> Path:
    """Download the head texture for the given uuid to <head_dir>/<uuid>.png"""
    # Get session info
    session_response = requests.get(SESSION_URL.format(uuid=uuid))
    if not session_response:
        raise RuntimeError(
            f"Failed to download user info for '{uuid}': "
            f"{session_response.status_code} {session_response.content}"
        )

    # Get skin url from session info
    session_info = session_response.json()
    skin_url = find_skin_url(session_info)
    if skin_url is None:
        raise RuntimeError(f"Failed to find skin url for '{uuid}': {session_info}")

    # Get skin image
    skin_response = requests.get(skin_url, stream=True)
    if not skin_response:
        raise RuntimeError(
            f"Could not download skin for '{uuid}': "
            f"{skin_response.status_code} {skin_response.content}"
        )

    head_dir.mkdir(parents=True, exist_ok=True)
    head_path = get_head_path(head_dir, uuid)

    skin = Image.open(BytesIO(skin_response.content))
    make_head_texture(skin).save(str(head_path))

    return head_path
