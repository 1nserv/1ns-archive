import io
import os
from PIL import Image

def open(path: str) -> bytes:
    curr_dir = os.path.dirname(os.path.abspath(os.path.join(__file__)))
    parent_dir = os.path.dirname(curr_dir)
    asset_path = os.path.join(parent_dir, 'assets', path)

    image = Image.open(asset_path)
    val = io.BytesIO()

    image.save(val, format = 'PNG')

    return val.getvalue()