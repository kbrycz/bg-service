import logging
import base64
from io import BytesIO

try:
    # If using the pure Python rembg library:
    from rembg import remove as rembg_remove
    REMBG_AVAILABLE = True
except ImportError:
    # In case rembg is not installed or fails on this environment
    REMBG_AVAILABLE = False
    logging.error("rembg is not installed or failed to import.")


def remove_bg_from_bytes(image_bytes: bytes) -> str:
    """
    Remove the background from the given image bytes using rembg.
    Returns a base64-encoded PNG string (without the 'data:image/png;base64,' prefix).
    """

    if not REMBG_AVAILABLE:
        raise RuntimeError("rembg library not installed or failed to load.")

    # rembg returns raw RGBA PNG bytes
    output_bytes = rembg_remove(image_bytes)

    # Convert that raw RGBA PNG into a base64 string
    b64_str = base64.b64encode(output_bytes).decode("utf-8")
    return b64_str