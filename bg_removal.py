import logging
import base64
from io import BytesIO

from PIL import Image

try:
    from rembg import remove as rembg_remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    logging.error("rembg is not installed or failed to import.")


def downscale_if_needed(image_bytes: bytes, max_dim=1600) -> bytes:
    """
    Downscale the image if width or height is bigger than max_dim
    to reduce memory usage for the U^2-Net model.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        w, h = img.size
        if w > max_dim or h > max_dim:
            ratio = min(max_dim / w, max_dim / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        # Save back to bytes as PNG
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        logging.error("Error downscaling image", exc_info=True)
        # If something fails, just return original
        return image_bytes


def remove_bg_from_bytes(image_bytes: bytes) -> str:
    """
    Remove the background using rembg with a lighter model (u2netp).
    Returns a base64-encoded PNG string (without the 'data:image/png;base64,' prefix).
    """
    if not REMBG_AVAILABLE:
        raise RuntimeError("rembg library not installed or failed to load.")

    # Downscale to reduce memory usage
    scaled_bytes = downscale_if_needed(image_bytes, max_dim=1600)

    # Use the "u2netp" lighter model (fewer parameters than full u2net)
    output_bytes = rembg_remove(scaled_bytes, model_name="u2netp")

    # Convert to base64
    b64_str = base64.b64encode(output_bytes).decode("utf-8")
    return b64_str