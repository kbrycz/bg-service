import logging
import base64
from io import BytesIO

from PIL import Image

try:
    # We'll import remove + new_session from rembg.bg
    from rembg.bg import remove as rembg_remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    logging.error("rembg is not installed or failed to import.")


# Create a global session once, specifying "u2netp"
# so we don't pass model_name again in remove()
session_u2netp = None
if REMBG_AVAILABLE:
    try:
        logging.info("Creating u2netp session...")
        session_u2netp = new_session("u2netp")
        logging.info("u2netp session created successfully.")
    except Exception as e:
        logging.error("Failed to create u2netp session", exc_info=True)
        REMBG_AVAILABLE = False


def downscale_if_needed(image_bytes: bytes, max_dim=1600) -> bytes:
    """
    Downscale the image if width or height is bigger than max_dim
    to reduce memory usage for the model.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        w, h = img.size
        if w > max_dim or h > max_dim:
            ratio = min(max_dim / w, max_dim / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        logging.error("Error downscaling image", exc_info=True)
        return image_bytes


def remove_bg_from_bytes(image_bytes: bytes) -> str:
    """
    Downscale + remove background using a single 'u2netp' session.
    Returns base64-encoded PNG (no 'data:image/png;base64,' prefix).
    """
    if not REMBG_AVAILABLE or session_u2netp is None:
        raise RuntimeError("rembg library or session not available.")

    scaled_bytes = downscale_if_needed(image_bytes, max_dim=1600)

    # We pass session=session_u2netp but do NOT pass model_name
    # to avoid the "got multiple values for argument 'model_name'" error
    output_bytes = rembg_remove(scaled_bytes, session=session_u2netp)

    b64_str = base64.b64encode(output_bytes).decode("utf-8")
    return b64_str