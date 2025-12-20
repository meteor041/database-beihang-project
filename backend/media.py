import base64
import json
import os
import re
import uuid
from typing import Any, List, Optional
from urllib.parse import urlparse

from werkzeug.utils import secure_filename

UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), "uploads")
ITEM_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "items")
ITEM_URL_PREFIX = "/api/uploads/items/"

ALLOWED_IMAGE_EXTS = {"jpg", "jpeg", "png", "gif", "webp"}
MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
}

_DATA_URL_RE = re.compile(r"^data:(image/[a-zA-Z0-9.+-]+);base64,(.*)$", re.DOTALL)


def ensure_item_upload_dir() -> None:
    os.makedirs(ITEM_UPLOAD_DIR, exist_ok=True)


def parse_json_array(value: Any, default: Optional[List[Any]] = None) -> List[Any]:
    if default is None:
        default = []
    if value is None:
        return default
    if isinstance(value, list):
        return value
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8")
        except Exception:
            return default
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else default
        except Exception:
            return default
    return default


def to_public_url(path_or_url: Any, host_url: str) -> Any:
    if not isinstance(path_or_url, str) or not path_or_url:
        return path_or_url
    if path_or_url.startswith(("http://", "https://", "data:")):
        return path_or_url
    if path_or_url.startswith("/"):
        return host_url.rstrip("/") + path_or_url
    return path_or_url


def save_upload_image(file_storage) -> str:
    ensure_item_upload_dir()

    original_name = secure_filename(file_storage.filename or "")
    ext = os.path.splitext(original_name)[1].lower().lstrip(".")
    if ext == "jpeg":
        ext = "jpg"

    mime = (getattr(file_storage, "mimetype", "") or "").lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        ext = MIME_TO_EXT.get(mime, "")
    if not ext:
        raise ValueError("Unsupported image type")

    filename = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(ITEM_UPLOAD_DIR, filename))
    return ITEM_URL_PREFIX + filename


def save_base64_image(data_url: str) -> str:
    match = _DATA_URL_RE.match(data_url or "")
    if not match:
        raise ValueError("Invalid base64 image data URL")

    mime = match.group(1).lower()
    b64_data = match.group(2)
    ext = MIME_TO_EXT.get(mime, "jpg")

    try:
        raw = base64.b64decode(b64_data)
    except Exception as e:
        raise ValueError("Invalid base64 image payload") from e

    ensure_item_upload_dir()
    filename = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(ITEM_UPLOAD_DIR, filename), "wb") as f:
        f.write(raw)
    return ITEM_URL_PREFIX + filename


def normalize_images_for_storage(images: Any, max_images: int = 9) -> List[str]:
    if not images:
        return []
    if not isinstance(images, list):
        return []

    normalized: List[str] = []
    for image in images:
        if not image:
            continue
        if not isinstance(image, str):
            continue

        if image.startswith("data:image/"):
            normalized.append(save_base64_image(image))
            continue

        if image.startswith(("http://", "https://")):
            try:
                parsed = urlparse(image)
                if parsed.path.startswith(ITEM_URL_PREFIX):
                    normalized.append(parsed.path)
                    continue
            except Exception:
                pass

        normalized.append(image)

        if len(normalized) >= max_images:
            break

    return normalized
