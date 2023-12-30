import torch
import numpy as np
import io
from PIL import Image,ImageOps
from urllib.request import urlopen

def img_from_path(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    image = img.convert("RGB")
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.from_numpy(image)[None,]
    return image

def img_from_url(url):
    img = io.BytesIO(urlopen(url).read())
    return img_from_path(img)