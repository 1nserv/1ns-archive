import io
import math
import os
from PIL import Image

def open_asset(path: str) -> bytes:
    curr_dir = os.path.dirname(os.path.abspath(os.path.join(__file__)))
    parent_dir = os.path.dirname(curr_dir)
    asset_path = os.path.join(parent_dir, 'assets', path)

    image = Image.open(asset_path)
    val = io.BytesIO()

    image.save(val, format = 'PNG')

    return val.getvalue()

def compress_image(data: bytes, _max: int = 1000 ** 2) -> bytes:
    img = Image.open(io.BytesIO(data))
    size = 2 * ( math.floor(math.sqrt(_max),) )

    img.resize(size)

    val = io.BytesIO()
    img.save(val)

    return val.getvalue()